import os
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, session
from config import Config
from models import db, User, Income, Expense, Budget, SavingsGoal, ChatMessage
from ai_service import AIFinanceAdvisor
from seed_data import seed_all_scenarios

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
ai_advisor = AIFinanceAdvisor()

def get_current_user_id():
    """Retrieves current user ID from session or defaults to the first user."""
    user_id = session.get('user_id')
    if not user_id:
        user = User.query.first()
        if user:
            session['user_id'] = user.id
            return user.id
    return user_id

@app.route('/')
def index():
    return render_template('index.html')

# =============================================================================
# USER & PERSONA APIS
# =============================================================================
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    current_id = get_current_user_id()
    return jsonify({
        'users': [u.to_dict() for u in users],
        'current_user_id': current_id
    })

@app.route('/api/users/switch', methods=['POST'])
def switch_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    session['user_id'] = user.id
    return jsonify({'success': True, 'user': user.to_dict()})

@app.route('/api/users/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    full_name = data.get('full_name')
    email = data.get('email')
    persona = data.get('persona', 'salaried')
    currency = data.get('currency', '₹')
    monthly_income = float(data.get('monthly_income_target', 0))

    if not username or not email or not full_name:
        return jsonify({'error': 'Missing required user details'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or Email already registered'}), 400

    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        persona=persona,
        currency=currency,
        monthly_income_target=monthly_income
    )
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id

    return jsonify({'success': True, 'user': new_user.to_dict()}), 201

# =============================================================================
# DASHBOARD SUMMARY API
# =============================================================================
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Active user not found'}), 404

    incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.desc()).all()
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).all()
    budgets = Budget.query.filter_by(user_id=user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=user.id).all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    net_savings = max(0, total_income - total_expense)
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Categorize expenses
    category_spending = {}
    essential_spending = 0.0
    discretionary_spending = 0.0

    for exp in expenses:
        category_spending[exp.category] = category_spending.get(exp.category, 0.0) + exp.amount
        if exp.is_essential:
            essential_spending += exp.amount
        else:
            discretionary_spending += exp.amount

    # Budget status check
    budget_cards = []
    overspent_categories = []
    for b in budgets:
        spent = category_spending.get(b.category, 0.0)
        pct = round((spent / b.monthly_limit * 100), 1) if b.monthly_limit > 0 else 0
        is_over = spent > b.monthly_limit
        is_warning = pct >= b.alert_threshold and not is_over
        if is_over:
            overspent_categories.append(b.category)
        budget_cards.append({
            'id': b.id,
            'category': b.category,
            'limit': b.monthly_limit,
            'spent': round(spent, 2),
            'remaining': round(max(0, b.monthly_limit - spent), 2),
            'pct_used': pct,
            'is_over': is_over,
            'is_warning': is_warning
        })

    # Top expenses list
    top_expenses = sorted([
        {'category': k, 'amount': round(v, 2), 'pct': round((v/total_expense*100), 1) if total_expense > 0 else 0}
        for k, v in category_spending.items()
    ], key=lambda x: x['amount'], reverse=True)

    # Financial Health
    health = ai_advisor.calculate_financial_health(
        total_income, total_expense, category_spending,
        essential_spending, discretionary_spending,
        [g.to_dict() for g in goals]
    )

    # Monthly runway calculation (emergency fund vs monthly burn)
    emergency_savings = sum(g.current_amount for g in goals if 'emergency' in g.title.lower() or 'cushion' in g.title.lower() or 'runway' in g.title.lower())
    monthly_runway_months = round(emergency_savings / total_expense, 1) if total_expense > 0 else 0.0

    return jsonify({
        'user': user.to_dict(),
        'metrics': {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'net_savings': round(net_savings, 2),
            'savings_rate': savings_rate,
            'essential_spending': round(essential_spending, 2),
            'discretionary_spending': round(discretionary_spending, 2),
            'emergency_savings': round(emergency_savings, 2),
            'emergency_runway_months': monthly_runway_months
        },
        'health': health,
        'budgets': budget_cards,
        'overspent_categories': overspent_categories,
        'top_expenses': top_expenses,
        'recent_incomes': [i.to_dict() for i in incomes[:6]],
        'recent_expenses': [e.to_dict() for e in expenses[:10]],
        'goals': [g.to_dict() for g in goals]
    })

# =============================================================================
# INCOMES CRUD
# =============================================================================
@app.route('/api/incomes', methods=['GET', 'POST'])
def handle_incomes():
    user_id = get_current_user_id()
    if request.method == 'POST':
        data = request.get_json() or {}
        source = data.get('source')
        amount = float(data.get('amount', 0))
        category = data.get('category', 'Salary')
        frequency = data.get('frequency', 'Monthly')
        notes = data.get('notes', '')
        date_str = data.get('date')

        if not source or amount <= 0:
            return jsonify({'error': 'Source name and positive amount are required'}), 400

        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        income = Income(
            user_id=user_id,
            source=source,
            amount=amount,
            category=category,
            frequency=frequency,
            notes=notes,
            date=entry_date
        )
        db.session.add(income)
        db.session.commit()
        return jsonify({'success': True, 'income': income.to_dict()}), 201

    incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).all()
    return jsonify({'incomes': [i.to_dict() for i in incomes]})

@app.route('/api/incomes/<int:id>', methods=['DELETE'])
def delete_income(id):
    user_id = get_current_user_id()
    income = Income.query.filter_by(id=id, user_id=user_id).first()
    if not income:
        return jsonify({'error': 'Income record not found'}), 404
    db.session.delete(income)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# EXPENSES CRUD
# =============================================================================
@app.route('/api/expenses', methods=['GET', 'POST'])
def handle_expenses():
    user_id = get_current_user_id()
    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title')
        amount = float(data.get('amount', 0))
        category = data.get('category', 'Miscellaneous')
        is_essential = bool(data.get('is_essential', True))
        notes = data.get('notes', '')
        date_str = data.get('date')

        if not title or amount <= 0:
            return jsonify({'error': 'Title and valid positive amount are required'}), 400

        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        expense = Expense(
            user_id=user_id,
            title=title,
            amount=amount,
            category=category,
            is_essential=is_essential,
            notes=notes,
            date=entry_date
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify({'success': True, 'expense': expense.to_dict()}), 201

    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    return jsonify({'expenses': [e.to_dict() for e in expenses]})

@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    user_id = get_current_user_id()
    expense = Expense.query.filter_by(id=id, user_id=user_id).first()
    if not expense:
        return jsonify({'error': 'Expense record not found'}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# BUDGETS APIS
# =============================================================================
@app.route('/api/budgets', methods=['GET', 'POST'])
def handle_budgets():
    user_id = get_current_user_id()
    if request.method == 'POST':
        data = request.get_json() or {}
        category = data.get('category')
        limit = float(data.get('monthly_limit', 0))
        threshold = float(data.get('alert_threshold', 85))

        if not category or limit <= 0:
            return jsonify({'error': 'Valid category and limit are required'}), 400

        # Update or create
        budget = Budget.query.filter_by(user_id=user_id, category=category).first()
        if budget:
            budget.monthly_limit = limit
            budget.alert_threshold = threshold
        else:
            budget = Budget(
                user_id=user_id,
                category=category,
                monthly_limit=limit,
                alert_threshold=threshold
            )
            db.session.add(budget)
        db.session.commit()
        return jsonify({'success': True, 'budget': budget.to_dict()})

    budgets = Budget.query.filter_by(user_id=user_id).all()
    return jsonify({'budgets': [b.to_dict() for b in budgets]})

@app.route('/api/budgets/auto-generate', methods=['POST'])
def auto_generate_budget():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    incomes = Income.query.filter_by(user_id=user.id).all()
    total_income = sum(i.amount for i in incomes) or user.monthly_income_target or 50000

    plan = ai_advisor.generate_persona_budget(user.persona, total_income, user.currency)

    # Apply allocations
    for alloc in plan['allocations']:
        if alloc['type'] != 'Savings':  # Savings goes to goals, not expense budget
            b = Budget.query.filter_by(user_id=user.id, category=alloc['category']).first()
            if b:
                b.monthly_limit = alloc['limit']
            else:
                b = Budget(user_id=user.id, category=alloc['category'], monthly_limit=alloc['limit'])
                db.session.add(b)
    db.session.commit()

    return jsonify({'success': True, 'plan': plan})

@app.route('/api/budgets/<int:id>', methods=['DELETE'])
def delete_budget(id):
    user_id = get_current_user_id()
    budget = Budget.query.filter_by(id=id, user_id=user_id).first()
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    db.session.delete(budget)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# SAVINGS GOALS APIS
# =============================================================================
@app.route('/api/goals', methods=['GET', 'POST'])
def handle_goals():
    user_id = get_current_user_id()
    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title')
        target_amount = float(data.get('target_amount', 0))
        current_amount = float(data.get('current_amount', 0))
        category = data.get('category', 'Emergency Fund')
        target_date_str = data.get('target_date')

        if not title or target_amount <= 0:
            return jsonify({'error': 'Title and positive target amount required'}), 400

        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date() if target_date_str else None
        goal = SavingsGoal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            current_amount=current_amount,
            category=category,
            target_date=target_date
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'success': True, 'goal': goal.to_dict()}), 201

    goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    return jsonify({'goals': [g.to_dict() for g in goals]})

@app.route('/api/goals/<int:id>/deposit', methods=['POST'])
def deposit_to_goal(id):
    user_id = get_current_user_id()
    goal = SavingsGoal.query.filter_by(id=id, user_id=user_id).first()
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    data = request.get_json() or {}
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({'error': 'Deposit amount must be positive'}), 400

    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    db.session.commit()

    return jsonify({'success': True, 'goal': goal.to_dict()})

@app.route('/api/goals/<int:id>', methods=['DELETE'])
def delete_goal(id):
    user_id = get_current_user_id()
    goal = SavingsGoal.query.filter_by(id=id, user_id=user_id).first()
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# AI CHATBOT & INSIGHTS APIS
# =============================================================================
@app.route('/api/chat', methods=['POST'])
def chat_with_advisor():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Save user message
    user_msg_record = ChatMessage(user_id=user.id, sender='user', message=user_message)
    db.session.add(user_msg_record)

    # Prepare financial context
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budgets = Budget.query.filter_by(user_id=user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=user.id).all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    category_spending = {}
    for e in expenses:
        category_spending[e.category] = category_spending.get(e.category, 0.0) + e.amount

    overspent = [b.category for b in budgets if category_spending.get(b.category, 0.0) > b.monthly_limit]
    top_expenses = sorted([
        {'category': k, 'amount': v} for k, v in category_spending.items()
    ], key=lambda x: x['amount'], reverse=True)[:4]

    context = {
        'currency': user.currency,
        'persona': user.persona,
        'total_income': total_income,
        'total_expense': total_expense,
        'overspent_categories': overspent,
        'top_expenses': top_expenses,
        'goals': [g.to_dict() for g in goals]
    }

    # Generate response
    ai_reply = ai_advisor.generate_chat_response(user_message, context)

    # Save bot message
    bot_msg_record = ChatMessage(user_id=user.id, sender='bot', message=ai_reply)
    db.session.add(bot_msg_record)
    db.session.commit()

    return jsonify({
        'reply': ai_reply,
        'user_message': user_msg_record.to_dict(),
        'bot_message': bot_msg_record.to_dict()
    })

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    user_id = get_current_user_id()
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.asc()).all()
    return jsonify({'messages': [m.to_dict() for m in messages]})

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    user_id = get_current_user_id()
    ChatMessage.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# SETTINGS & GEMINI CONFIG
# =============================================================================
@app.route('/api/settings/gemini-key', methods=['POST'])
def update_gemini_key():
    data = request.get_json() or {}
    key = data.get('api_key', '').strip()
    ai_advisor.set_api_key(key)
    return jsonify({
        'success': True,
        'gemini_ready': ai_advisor.gemini_ready,
        'message': 'Gemini AI configured successfully!' if ai_advisor.gemini_ready else 'API Key saved. Running in dual hybrid mode.'
    })

# =============================================================================
# MONTHLY FINANCIAL REPORT
# =============================================================================
@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    budgets = Budget.query.filter_by(user_id=user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=user.id).all()

    report = ai_advisor.generate_monthly_report(user, incomes, expenses, budgets, goals)
    return jsonify({'report': report})

# =============================================================================
# RESET & SEED DEMO DATA
# =============================================================================
@app.route('/api/reset-data', methods=['POST'])
def reset_demo_data():
    db.drop_all()
    db.create_all()
    seed_all_scenarios()
    session['user_id'] = User.query.first().id
    return jsonify({'success': True, 'message': 'Demo scenarios reset and seeded successfully!'})

# Initialize DB tables and seed data upon startup
with app.app_context():
    db.create_all()
    seed_all_scenarios()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
