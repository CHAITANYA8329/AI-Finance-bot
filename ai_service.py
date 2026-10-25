import os
import json
import re
from datetime import datetime
from config import Config

# Optional google.generativeai import
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class AIFinanceAdvisor:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self._init_gemini()

    def set_api_key(self, api_key):
        self.api_key = api_key
        self._init_gemini()

    def _init_gemini(self):
        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.gemini_ready = True
            except Exception as e:
                print(f"[AIFinanceAdvisor] Warning: Failed to initialize Gemini API: {e}")
                self.gemini_ready = False
        else:
            self.gemini_ready = False

    def calculate_financial_health(self, total_income, total_expense, category_totals, essential_total, discretionary_total, savings_goals):
        """Calculates a comprehensive Financial Health Score (0-100) and breakdown."""
        if total_income <= 0:
            return {
                'score': 50,
                'status': 'Neutral / Setup Phase',
                'badge_color': '#f59e0b',
                'savings_rate': 0.0,
                'expense_ratio': 0.0,
                'breakdown': {
                    'savings_score': 10,
                    'spending_control_score': 15,
                    'essential_balance_score': 15,
                    'goals_score': 10
                },
                'summary': 'Add your monthly income to unlock your real-time financial health score.'
            }

        net_savings = max(0, total_income - total_expense)
        savings_rate = (net_savings / total_income) * 100
        expense_ratio = (total_expense / total_income) * 100

        # Component 1: Savings Rate (max 35)
        # Target: >= 25% for full marks, >= 20% for 30 pts
        if savings_rate >= 30:
            savings_score = 35
        elif savings_rate >= 20:
            savings_score = 30
        elif savings_rate >= 10:
            savings_score = 20
        elif savings_rate > 0:
            savings_score = 10
        else:
            savings_score = 0

        # Component 2: Spending Control (max 30)
        # Target: total expense <= 70% of income
        if expense_ratio <= 60:
            spending_control_score = 30
        elif expense_ratio <= 75:
            spending_control_score = 25
        elif expense_ratio <= 90:
            spending_control_score = 15
        elif expense_ratio <= 100:
            spending_control_score = 8
        else:
            spending_control_score = 0

        # Component 3: Discretionary vs Essential Ratio (max 20)
        # Discretionary <= 30% of total expense
        if total_expense > 0:
            discretionary_ratio = (discretionary_total / total_expense) * 100
            if discretionary_ratio <= 25:
                essential_balance_score = 20
            elif discretionary_ratio <= 40:
                essential_balance_score = 15
            elif discretionary_ratio <= 60:
                essential_balance_score = 10
            else:
                essential_balance_score = 4
        else:
            essential_balance_score = 20

        # Component 4: Savings Goals Progress (max 15)
        if savings_goals:
            avg_progress = sum(g.get('progress_percentage', 0) for g in savings_goals) / len(savings_goals)
            goals_score = min(15, round(avg_progress * 0.15))
        else:
            goals_score = 8

        total_score = min(100, savings_score + spending_control_score + essential_balance_score + goals_score)

        if total_score >= 85:
            status = 'Exceptional'
            badge_color = '#10b981' # Emerald
            summary = 'Your finances are well-disciplined! You have high savings velocity and healthy margins.'
        elif total_score >= 70:
            status = 'Healthy'
            badge_color = '#06b6d4' # Cyan
            summary = 'Good financial trajectory. Maintaining this consistency will compound your wealth.'
        elif total_score >= 50:
            status = 'Moderate / Room for Optimization'
            badge_color = '#f59e0b' # Amber
            summary = 'Slight cashflow strain or discretionary leakage. Tightening non-essentials will boost your score.'
        else:
            status = 'At Risk / Deficit Zone'
            badge_color = '#ef4444' # Coral
            summary = 'Expenses exceed or match income. Immediate reduction of discretionary categories is advised.'

        return {
            'score': total_score,
            'status': status,
            'badge_color': badge_color,
            'savings_rate': round(savings_rate, 1),
            'expense_ratio': round(expense_ratio, 1),
            'breakdown': {
                'savings_score': savings_score,
                'spending_control_score': spending_control_score,
                'essential_balance_score': essential_balance_score,
                'goals_score': goals_score
            },
            'summary': summary
        }

    def generate_persona_budget(self, persona, monthly_income, currency='₹'):
        """Generates tailored budget allocations based on user persona."""
        income = max(monthly_income, 1000)
        
        if persona == 'student':
            # College student: tight allowance, essential focus
            allocations = [
                {'category': 'Food & Groceries', 'percentage': 35, 'limit': round(income * 0.35, 2), 'type': 'Essential'},
                {'category': 'Education & Books', 'percentage': 18, 'limit': round(income * 0.18, 2), 'type': 'Essential'},
                {'category': 'Transport & Fuel', 'percentage': 12, 'limit': round(income * 0.12, 2), 'type': 'Essential'},
                {'category': 'Entertainment & Outings', 'percentage': 15, 'limit': round(income * 0.15, 2), 'type': 'Discretionary'},
                {'category': 'Emergency / Student Savings', 'percentage': 20, 'limit': round(income * 0.20, 2), 'type': 'Savings'}
            ]
            advice = "As a student, keeping daily food & leisure expenses under control allows you to graduate with a healthy emergency cushion."

        elif persona == 'freelancer':
            # Freelancer: fluctuating income, emergency fund is #1 priority
            allocations = [
                {'category': 'Rent & Housing', 'percentage': 28, 'limit': round(income * 0.28, 2), 'type': 'Essential'},
                {'category': 'Food & Groceries', 'percentage': 18, 'limit': round(income * 0.18, 2), 'type': 'Essential'},
                {'category': 'Software & Work Tools', 'percentage': 10, 'limit': round(income * 0.10, 2), 'type': 'Essential'},
                {'category': 'Emergency Fund (Lean Month Buffer)', 'percentage': 25, 'limit': round(income * 0.25, 2), 'type': 'Savings'},
                {'category': 'Transport & Utilities', 'percentage': 10, 'limit': round(income * 0.10, 2), 'type': 'Essential'},
                {'category': 'Entertainment & Dining', 'percentage': 9, 'limit': round(income * 0.09, 2), 'type': 'Discretionary'}
            ]
            advice = "With variable freelance cashflows, a 25% emergency reserve guarantees stability during dry contract months."

        elif persona == 'household':
            # Household Manager: family expenses, groceries, utilities, children education, healthcare
            allocations = [
                {'category': 'Groceries & Provisions', 'percentage': 26, 'limit': round(income * 0.26, 2), 'type': 'Essential'},
                {'category': 'Rent & Home Maintenance', 'percentage': 24, 'limit': round(income * 0.24, 2), 'type': 'Essential'},
                {'category': 'Children Education & Activities', 'percentage': 16, 'limit': round(income * 0.16, 2), 'type': 'Essential'},
                {'category': 'Utilities & Household Bills', 'percentage': 12, 'limit': round(income * 0.12, 2), 'type': 'Essential'},
                {'category': 'Healthcare & Medical Care', 'percentage': 8, 'limit': round(income * 0.08, 2), 'type': 'Essential'},
                {'category': 'Family Savings & Contingency', 'percentage': 14, 'limit': round(income * 0.14, 2), 'type': 'Savings'}
            ]
            advice = "Household budgeting requires category containment—especially bulk grocery buying and utility monitoring to prevent budget overruns."

        else:
            # Salaried Professional: Classic 50/30/20 Rule
            allocations = [
                {'category': 'Rent & Housing', 'percentage': 25, 'limit': round(income * 0.25, 2), 'type': 'Essential'},
                {'category': 'Food & Groceries', 'percentage': 15, 'limit': round(income * 0.15, 2), 'type': 'Essential'},
                {'category': 'Transport & Fuel', 'percentage': 10, 'limit': round(income * 0.10, 2), 'type': 'Essential'},
                {'category': 'Utilities & Bills', 'percentage': 6, 'limit': round(income * 0.06, 2), 'type': 'Essential'},
                {'category': 'Dining & Entertainment', 'percentage': 15, 'limit': round(income * 0.15, 2), 'type': 'Discretionary'},
                {'category': 'Shopping & Lifestyle', 'percentage': 9, 'limit': round(income * 0.09, 2), 'type': 'Discretionary'},
                {'category': 'Wealth Building & Savings', 'percentage': 20, 'limit': round(income * 0.20, 2), 'type': 'Savings'}
            ]
            advice = "The 50/30/20 framework structures your salary: 50% on essentials, 30% for quality-of-life wants, and 20% directly into wealth generation."

        return {
            'persona': persona,
            'income': income,
            'currency': currency,
            'advice': advice,
            'allocations': allocations
        }

    def generate_chat_response(self, user_message, financial_context):
        """Processes user chat queries using Gemini AI or Fallback Intelligent Heuristics."""
        curr = financial_context.get('currency', '₹')
        persona = financial_context.get('persona', 'salaried')
        income = financial_context.get('total_income', 0)
        expense = financial_context.get('total_expense', 0)
        savings = max(0, income - expense)
        savings_rate = round((savings / income * 100), 1) if income > 0 else 0
        overspent = financial_context.get('overspent_categories', [])
        top_expenses = financial_context.get('top_expenses', [])
        goals = financial_context.get('goals', [])

        # Try live Gemini AI first if configured
        if self.gemini_ready:
            try:
                system_prompt = f"""
You are the "Personal Finance Advisor Bot", a professional, empathetic, and strategic AI financial planner.
You help individuals master their finances, stick to budgets, eliminate overspending, and grow savings.

User Profile:
- Persona: {persona.capitalize()}
- Currency: {curr}
- Monthly Income: {curr}{income:,.2f}
- Monthly Expenses: {curr}{expense:,.2f}
- Net Savings: {curr}{savings:,.2f} ({savings_rate}% savings rate)
- Overspent/Warning Categories: {', '.join(overspent) if overspent else 'None currently over limit'}
- Top Expense Categories: {', '.join([f"{c['category']}: {curr}{c['amount']:,.2f}" for c in top_expenses])}
- Goals: {', '.join([f"{g['title']} ({g['progress_percentage']}%)" for g in goals]) if goals else 'None set'}

Guidelines:
- Keep responses practical, actionable, formatted cleanly with markdown bullet points and bolding.
- Address their specific persona challenges (e.g. fluctuating freelance income, student allowances, family household costs, salaried overspending).
- If they ask for budget advice, recommend clear percentage breakdowns or concrete cutbacks.
- Keep tone supportive, encouraging, and financially sound.
"""
                chat = self.model.start_chat(history=[])
                response = chat.send_message(f"{system_prompt}\n\nUser Question: {user_message}")
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[AIFinanceAdvisor] Gemini API query error: {e}. Falling back to internal engine.")

        # Robust Built-in Financial Intelligence Rules Engine
        msg = user_message.lower()

        if any(w in msg for w in ['overspend', 'cut', 'reduce', 'curb', 'leak']):
            if overspent:
                items = "\n".join([f"• **{cat}**: Exceeded safe limits. Consider setting a weekly cash envelope or dining limit." for cat in overspent])
                return (
                    f"### ⚠️ Overspending Analysis\n"
                    f"Based on your recent logs, you have exceeded or are near limits in:\n{items}\n\n"
                    f"**Action Plan:**\n"
                    f"1. **Audit Subscriptions & Dining**: Reduce spontaneous takeouts or leisure subscriptions by 30% this week.\n"
                    f"2. **The 48-Hour Rule**: For any non-essential purchase above {curr}1,000, wait 48 hours before buying.\n"
                    f"3. **Target Savings**: Applying these cutbacks will free up approximately **{curr}{round(expense * 0.12):,.2f}** back into your savings!"
                )
            else:
                return (
                    f"### 🔍 Spending Optimization Review\n"
                    f"Your categories are currently within active budget limits! However, your top spending is in:\n"
                    + "\n".join([f"• **{c['category']}**: {curr}{c['amount']:,.2f}" for c in top_expenses[:3]]) +
                    f"\n\n**Recommendation:** To accelerate your savings rate above **{savings_rate}%**, review discretionary expenses in your top categories."
                )

        if any(w in msg for w in ['budget', 'plan', 'rule', 'allocate', 'recommend']):
            budget_data = self.generate_persona_budget(persona, income, curr)
            alloc_str = "\n".join([f"• **{a['category']}** ({a['percentage']}%): **{curr}{a['limit']:,.2f}** [{a['type']}]" for a in budget_data['allocations']])
            return (
                f"### 📊 Personalized Budget Plan for {persona.capitalize()}\n"
                f"{budget_data['advice']}\n\n"
                f"**Recommended Monthly Allocation (Based on {curr}{income:,.2f} Income):**\n"
                f"{alloc_str}\n\n"
                f"💡 *Click 'Auto-Apply Budget' in the Budget Planner tab to lock these limits into your dashboard!*"
            )

        if any(w in msg for w in ['emergency', 'runway', 'buffer', 'safety net']):
            monthly_burn = max(expense, 1000)
            ideal_emergency_3m = monthly_burn * 3
            ideal_emergency_6m = monthly_burn * 6
            return (
                f"### 🛡️ Emergency Fund Strategy\n"
                f"For a **{persona.capitalize()}**, financial security begins with a reliable liquidity cushion.\n\n"
                f"• **Current Monthly Burn**: {curr}{monthly_burn:,.2f}\n"
                f"• **3-Month Baseline Cushion**: **{curr}{ideal_emergency_3m:,.2f}**\n"
                f"• **6-Month Safe Runway**: **{curr}{ideal_emergency_6m:,.2f}**\n\n"
                f"**Step-by-step Execution:**\n"
                f"1. Open a high-yield or liquid sweep-in account.\n"
                f"2. Automate a transfer of **{curr}{round(max(500, savings * 0.4)):,.2f}** directly after income receipt.\n"
                f"3. Treat this fund strictly as an insurance policy for unforeseen emergencies."
            )

        if any(w in msg for w in ['health', 'score', 'status', 'rate', 'how am i doing']):
            health = self.calculate_financial_health(income, expense, {}, expense * 0.6, expense * 0.4, goals)
            return (
                f"### 🩺 Financial Health Evaluation\n"
                f"• **Overall Score**: **{health['score']} / 100** ({health['status']})\n"
                f"• **Savings Velocity**: **{savings_rate}%** of total income retained\n"
                f"• **Expense Pressure**: Spending accounts for **{health['expense_ratio']}%** of income\n\n"
                f"**Advisor Take:** {health['summary']}\n"
                f"Keep logging daily transactions to track your score progression over time!"
            )

        # General / greeting / help response
        return (
            f"Hello! I am your **Personal Finance Advisor Bot** tailored for **{persona.capitalize()}** planning.\n\n"
            f"Here is your current snapshot:\n"
            f"• **Total Income**: {curr}{income:,.2f}\n"
            f"• **Total Expenses**: {curr}{expense:,.2f}\n"
            f"• **Net Savings**: {curr}{savings:,.2f} ({savings_rate}%)\n\n"
            f"You can ask me anything about:\n"
            f"1. *'Generate my personalized budget plan'*\n"
            f"2. *'Where am I overspending and how to cut costs?'*\n"
            f"3. *'How to build an emergency fund for my persona?'*\n"
            f"4. *'What is my financial health score and how to improve it?'*"
        )

    def generate_monthly_report(self, user, incomes, expenses, budgets, savings_goals):
        """Generates a structured comprehensive monthly financial analysis report."""
        total_income = sum(i.amount for i in incomes)
        total_expense = sum(e.amount for e in expenses)
        net_savings = total_income - total_expense
        savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0
        curr = user.currency

        # Category breakdown
        category_spending = {}
        essential_spending = 0
        discretionary_spending = 0

        for exp in expenses:
            category_spending[exp.category] = category_spending.get(exp.category, 0.0) + exp.amount
            if exp.is_essential:
                essential_spending += exp.amount
            else:
                discretionary_spending += exp.amount

        # Budget variance analysis
        budget_analysis = []
        overspent_categories = []
        for b in budgets:
            spent = category_spending.get(b.category, 0.0)
            variance = b.monthly_limit - spent
            pct_used = round((spent / b.monthly_limit * 100), 1) if b.monthly_limit > 0 else 0
            is_over = spent > b.monthly_limit
            if is_over:
                overspent_categories.append(b.category)
            budget_analysis.append({
                'category': b.category,
                'limit': b.monthly_limit,
                'spent': spent,
                'variance': variance,
                'pct_used': pct_used,
                'status': 'Over Budget' if is_over else ('Near Limit' if pct_used >= b.alert_threshold else 'On Track')
            })

        health = self.calculate_financial_health(
            total_income, total_expense, category_spending,
            essential_spending, discretionary_spending,
            [g.to_dict() for g in savings_goals]
        )

        # AI Actionable Next Month Goals
        next_month_goals = [
            f"Cap discretionary leisure spending at {curr}{round(discretionary_spending * 0.85):,.2f} (15% reduction).",
            f"Deposit {curr}{round(max(1000, total_income * 0.20)):,.2f} into high-priority savings goals.",
            f"Ensure {overspent_categories[0] if overspent_categories else 'all categories'} stay within allocated monthly limit."
        ]

        return {
            'generated_at': datetime.now().strftime('%B %d, %Y'),
            'user': user.to_dict(),
            'period': datetime.now().strftime('%B %Y'),
            'currency': curr,
            'summary': {
                'total_income': round(total_income, 2),
                'total_expense': round(total_expense, 2),
                'net_savings': round(net_savings, 2),
                'savings_rate': savings_rate,
                'essential_spending': round(essential_spending, 2),
                'discretionary_spending': round(discretionary_spending, 2)
            },
            'health': health,
            'budget_analysis': budget_analysis,
            'category_spending': [
                {'category': k, 'amount': round(v, 2), 'pct': round((v / total_expense * 100), 1) if total_expense > 0 else 0}
                for k, v in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
            ],
            'savings_goals': [g.to_dict() for g in savings_goals],
            'overspent_categories': overspent_categories,
            'ai_insights': [
                f"You saved {curr}{net_savings:,.2f} ({savings_rate}%), resulting in a '{health['status']}' rating.",
                f"Essential expenses accounted for {round((essential_spending/total_expense*100) if total_expense else 0)}% of total outflows.",
                f"Key area for immediate savings: {overspent_categories[0] if overspent_categories else 'Non-essential dining and lifestyle'}"
            ],
            'next_month_goals': next_month_goals
        }
