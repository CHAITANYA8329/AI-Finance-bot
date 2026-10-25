from datetime import date, timedelta
from models import db, User, Income, Expense, Budget, SavingsGoal, ChatMessage

def seed_all_scenarios():
    """Seeds the 4 complete scenarios for instant demo and evaluation."""
    if User.query.first():
        return  # Already seeded
    
    today = date.today()

    # =========================================================================
    # SCENARIO 1: Salaried Professional (Rahul Sharma)
    # =========================================================================
    u1 = User(
        username='rahul_salaried',
        email='rahul.sharma@example.com',
        full_name='Rahul Sharma',
        persona='salaried',
        currency='₹',
        monthly_income_target=80000.0
    )
    db.session.add(u1)
    db.session.flush()

    db.session.add_all([
        Income(user_id=u1.id, source='Tech Corp Monthly Salary', amount=75000.0, category='Salary', date=today - timedelta(days=20), frequency='Monthly', notes='Direct bank credit'),
        Income(user_id=u1.id, source='Quarterly Performance Bonus', amount=5000.0, category='Bonus', date=today - timedelta(days=5), frequency='One-time', notes='Q3 Target achievement'),
        
        # Expenses
        Expense(user_id=u1.id, title='Apartment Rent', amount=22000.0, category='Rent & Housing', date=today - timedelta(days=22), is_essential=True, notes='2BHK flat rent'),
        Expense(user_id=u1.id, title='Monthly Supermarket Groceries', amount=11500.0, category='Food & Groceries', date=today - timedelta(days=18), is_essential=True, notes='Nature Basket & BigBasket'),
        Expense(user_id=u1.id, title='Metro Card & Fuel', amount=5800.0, category='Transport & Fuel', date=today - timedelta(days=14), is_essential=True, notes='Office commute'),
        Expense(user_id=u1.id, title='Electricity & High-speed Wifi', amount=3600.0, category='Utilities', date=today - timedelta(days=10), is_essential=True, notes='Torrent power & Airtel fiber'),
        Expense(user_id=u1.id, title='Fine Dining & Weekend Pubs', amount=14800.0, category='Entertainment & Dining Out', date=today - timedelta(days=4), is_essential=False, notes='Social dinners with coworkers - Overspent!'),
        Expense(user_id=u1.id, title='Online Shopping & Apparel', amount=7200.0, category='Shopping', date=today - timedelta(days=2), is_essential=False, notes='Myntra festive sale'),
        Expense(user_id=u1.id, title='Netflix, Spotify & Prime', amount=1650.0, category='Subscriptions', date=today - timedelta(days=12), is_essential=False, notes='Streaming bundle'),

        # Budgets
        Budget(user_id=u1.id, category='Rent & Housing', monthly_limit=22000.0, alert_threshold=90.0),
        Budget(user_id=u1.id, category='Food & Groceries', monthly_limit=12000.0, alert_threshold=85.0),
        Budget(user_id=u1.id, category='Entertainment & Dining Out', monthly_limit=8500.0, alert_threshold=80.0), # Will trigger alert!
        Budget(user_id=u1.id, category='Transport & Fuel', monthly_limit=7000.0, alert_threshold=85.0),
        Budget(user_id=u1.id, category='Shopping', monthly_limit=6000.0, alert_threshold=80.0),

        # Savings Goals
        SavingsGoal(user_id=u1.id, title='6-Month Emergency Fund', target_amount=200000.0, current_amount=95000.0, target_date=today + timedelta(days=180), category='Emergency Fund'),
        SavingsGoal(user_id=u1.id, title='Himachal Vacation Trip', target_amount=45000.0, current_amount=30000.0, target_date=today + timedelta(days=60), category='Travel/Vacation'),

        # Sample Initial AI Chat
        ChatMessage(user_id=u1.id, sender='user', message='Can you look at my spending this month and highlight problem areas?'),
        ChatMessage(user_id=u1.id, sender='bot', message='I reviewed your finances, Rahul. You earned ₹80,000 and spent ₹66,550. Your key alert is **Entertainment & Dining Out (₹14,800)** which exceeds your ₹8,500 limit by **74%**. Also, your **Shopping (₹7,200)** crossed its ₹6,000 limit. Capping weekend dining will help you hit your ₹200,000 Emergency Fund goal 2 months earlier!')
    ])

    # =========================================================================
    # SCENARIO 2: College Student (Ananya Verma)
    # =========================================================================
    u2 = User(
        username='ananya_student',
        email='ananya.verma@example.edu',
        full_name='Ananya Verma',
        persona='student',
        currency='₹',
        monthly_income_target=15000.0
    )
    db.session.add(u2)
    db.session.flush()

    db.session.add_all([
        Income(user_id=u2.id, source='Monthly Parental Allowance', amount=12000.0, category='Allowance', date=today - timedelta(days=24), frequency='Monthly', notes='Monthly college stipend'),
        Income(user_id=u2.id, source='Peer Math Tutoring', amount=3000.0, category='Freelance', date=today - timedelta(days=8), frequency='Weekly', notes='2 sessions weekly'),

        # Expenses
        Expense(user_id=u2.id, title='Campus Canteen & Meals', amount=4800.0, category='Food & Groceries', date=today - timedelta(days=20), is_essential=True, notes='Daily lunch and hostel mess'),
        Expense(user_id=u2.id, title='Engineering Textbooks & Notes', amount=2400.0, category='Education', date=today - timedelta(days=16), is_essential=True, notes='Semester reference guides'),
        Expense(user_id=u2.id, title='Student Bus Pass & Auto', amount=1300.0, category='Transport & Fuel', date=today - timedelta(days=15), is_essential=True, notes='Commute to university'),
        Expense(user_id=u2.id, title='Mobile 5G Data Pack', amount=499.0, category='Utilities', date=today - timedelta(days=12), is_essential=True, notes='Prepaid monthly recharge'),
        Expense(user_id=u2.id, title='Cafe Hangouts & Movie Tickets', amount=3900.0, category='Entertainment & Dining Out', date=today - timedelta(days=3), is_essential=False, notes='Discretionary social weekend - High!'),
        Expense(user_id=u2.id, title='Fast Food & Coffee Deliveries', amount=1350.0, category='Food & Groceries', date=today - timedelta(days=2), is_essential=False, notes='Late-night study snacks'),

        # Budgets
        Budget(user_id=u2.id, category='Food & Groceries', monthly_limit=5000.0, alert_threshold=85.0),
        Budget(user_id=u2.id, category='Education', monthly_limit=2500.0, alert_threshold=85.0),
        Budget(user_id=u2.id, category='Entertainment & Dining Out', monthly_limit=2000.0, alert_threshold=75.0), # Alert!
        Budget(user_id=u2.id, category='Transport & Fuel', monthly_limit=1500.0, alert_threshold=80.0),

        # Savings Goals
        SavingsGoal(user_id=u2.id, title='Coding Laptop Upgrade', target_amount=40000.0, current_amount=15500.0, target_date=today + timedelta(days=150), category='Gadget/Asset'),
        SavingsGoal(user_id=u2.id, title='Student Safety Cushion', target_amount=5000.0, current_amount=3200.0, target_date=today + timedelta(days=45), category='Emergency Fund'),

        # Chat
        ChatMessage(user_id=u2.id, sender='user', message='How can I balance fun with my limited student allowance?'),
        ChatMessage(user_id=u2.id, sender='bot', message='Hi Ananya! As a student, your total income is ₹15,000. Your essential expenses (tuition, textbooks, bus pass, mess) are well-managed at ₹8,999. However, discretionary cafe outings and deliveries hit **₹5,250**, eating into 35% of your allowance. Setting a weekly **₹500 cash envelope for coffee & hangouts** will let you save ₹2,000 extra every month towards your new laptop!')
    ])

    # =========================================================================
    # SCENARIO 3: Freelancer with Variable Income (Vikram Roy)
    # =========================================================================
    u3 = User(
        username='vikram_freelance',
        email='vikram.roy@designstudio.dev',
        full_name='Vikram Roy',
        persona='freelancer',
        currency='₹',
        monthly_income_target=100000.0
    )
    db.session.add(u3)
    db.session.flush()

    db.session.add_all([
        Income(user_id=u3.id, source='Fintech SaaS UI/UX Project', amount=48000.0, category='Freelance', date=today - timedelta(days=22), frequency='Project-based', notes='Milestone 2 payout'),
        Income(user_id=u3.id, source='E-Commerce Redesign Contract', amount=36000.0, category='Freelance', date=today - timedelta(days=11), frequency='Project-based', notes='Client Beta delivery'),
        Income(user_id=u3.id, source='WordPress Monthly Maintenance Retainer', amount=18000.0, category='Freelance', date=today - timedelta(days=4), frequency='Monthly', notes='Recurring maintenance'),

        # Expenses
        Expense(user_id=u3.id, title='Home Studio Rent', amount=25000.0, category='Rent & Housing', date=today - timedelta(days=25), is_essential=True, notes='Work-live loft studio'),
        Expense(user_id=u3.id, title='Adobe Creative Cloud & Figma Pro', amount=5400.0, category='Subscriptions', date=today - timedelta(days=19), is_essential=True, notes='Design software subscriptions'),
        Expense(user_id=u3.id, title='AWS Server & Domain Hosting', amount=2600.0, category='Subscriptions', date=today - timedelta(days=18), is_essential=True, notes='Client demo staging'),
        Expense(user_id=u3.id, title='Groceries & Organic Staples', amount=12200.0, category='Food & Groceries', date=today - timedelta(days=14), is_essential=True, notes='Cooking at home'),
        Expense(user_id=u3.id, title='Coworking Day Passes & Hot Desk', amount=4800.0, category='Utilities', date=today - timedelta(days=9), is_essential=False, notes='Alternate work days'),
        Expense(user_id=u3.id, title='Client Dinners & Pitch Meetings', amount=8200.0, category='Entertainment & Dining Out', date=today - timedelta(days=5), is_essential=False, notes='Business networking - High!'),
        Expense(user_id=u3.id, title='High-speed Leased Line Internet', amount=2100.0, category='Utilities', date=today - timedelta(days=15), is_essential=True, notes='300Mbps fiber line'),

        # Budgets
        Budget(user_id=u3.id, category='Rent & Housing', monthly_limit=25000.0, alert_threshold=90.0),
        Budget(user_id=u3.id, category='Subscriptions', monthly_limit=8500.0, alert_threshold=85.0),
        Budget(user_id=u3.id, category='Food & Groceries', monthly_limit=13000.0, alert_threshold=85.0),
        Budget(user_id=u3.id, category='Entertainment & Dining Out', monthly_limit=5000.0, alert_threshold=80.0), # Alert!

        # Savings Goals
        SavingsGoal(user_id=u3.id, title='6-Month Lean Freelance Runway', target_amount=250000.0, current_amount=145000.0, target_date=today + timedelta(days=120), category='Emergency Fund'),
        SavingsGoal(user_id=u3.id, title='M3 Max Studio Workstation', target_amount=180000.0, current_amount=92000.0, target_date=today + timedelta(days=90), category='Gadget/Asset'),

        # Chat
        ChatMessage(user_id=u3.id, sender='user', message='My income varies between ₹60k and ₹110k. How should I plan my emergency fund?'),
        ChatMessage(user_id=u3.id, sender='bot', message='For variable freelance earnings, Vikram, the golden rule is **Income Smoothing**: Base your personal lifestyle on your lowest historical month (₹60k). This month you earned ₹102,000, creating an excess of ₹41,700 over your ₹60,300 expenses. Funnel 60% of this surplus (₹25,000) directly into your **6-Month Lean Freelance Runway**. This guarantees 3-4 months of zero-stress breathing room during slow invoice cycles!')
    ])

    # =========================================================================
    # SCENARIO 4: Household Manager (Sunita Pawar)
    # =========================================================================
    u4 = User(
        username='sunita_household',
        email='sunita.pawar@homefamily.org',
        full_name='Sunita Pawar',
        persona='household',
        currency='₹',
        monthly_income_target=130000.0
    )
    db.session.add(u4)
    db.session.flush()

    db.session.add_all([
        Income(user_id=u4.id, source='Primary Salary Contribution', amount=85000.0, category='Salary', date=today - timedelta(days=25), frequency='Monthly', notes='Partner 1 monthly share'),
        Income(user_id=u4.id, source='Secondary Income & Consultancy', amount=45000.0, category='Salary', date=today - timedelta(days=18), frequency='Monthly', notes='Partner 2 remote consulting'),

        # Expenses
        Expense(user_id=u4.id, title='Family Monthly Wholesale Groceries', amount=29400.0, category='Food & Groceries', date=today - timedelta(days=21), is_essential=True, notes='D-Mart wholesale & milk - Over limit!'),
        Expense(user_id=u4.id, title='Society Maintenance & Home Rent', amount=34000.0, category='Rent & Housing', date=today - timedelta(days=23), is_essential=True, notes='3BHK apartment rent & maintenance'),
        Expense(user_id=u4.id, title='Kids School Tuition & Bus Fees', amount=22500.0, category='Education', date=today - timedelta(days=17), is_essential=True, notes='Quarterly installment for two children'),
        Expense(user_id=u4.id, title='Electricity, Piped Gas & Water Bill', amount=10200.0, category='Utilities', date=today - timedelta(days=13), is_essential=True, notes='Summer AC consumption - Over limit!'),
        Expense(user_id=u4.id, title='Pediatrician & Pharmacy Medicines', amount=6800.0, category='Healthcare', date=today - timedelta(days=8), is_essential=True, notes='Routine health checkup & medications'),
        Expense(user_id=u4.id, title='Family Sunday Buffet & Ice Cream', amount=8600.0, category='Entertainment & Dining Out', date=today - timedelta(days=5), is_essential=False, notes='Family weekend meal'),
        Expense(user_id=u4.id, title='School Uniforms & Kids Books', amount=4200.0, category='Education', date=today - timedelta(days=10), is_essential=True, notes='New term supplies'),

        # Budgets
        Budget(user_id=u4.id, category='Food & Groceries', monthly_limit=24000.0, alert_threshold=85.0), # Overspent!
        Budget(user_id=u4.id, category='Rent & Housing', monthly_limit=34000.0, alert_threshold=90.0),
        Budget(user_id=u4.id, category='Education', monthly_limit=25000.0, alert_threshold=85.0), # Near limit
        Budget(user_id=u4.id, category='Utilities', monthly_limit=7500.0, alert_threshold=80.0), # Overspent!
        Budget(user_id=u4.id, category='Healthcare', monthly_limit=8000.0, alert_threshold=85.0),
        Budget(user_id=u4.id, category='Entertainment & Dining Out', monthly_limit=8000.0, alert_threshold=80.0),

        # Savings Goals
        SavingsGoal(user_id=u4.id, title='Children Higher Education Corpus', target_amount=500000.0, current_amount=220000.0, target_date=today + timedelta(days=365), category='Education'),
        SavingsGoal(user_id=u4.id, title='Family Medical & Health Contingency', target_amount=300000.0, current_amount=180000.0, target_date=today + timedelta(days=180), category='Emergency Fund'),

        # Chat
        ChatMessage(user_id=u4.id, sender='user', message='Can you summarize our household budget overruns this month and tell us what to fix?'),
        ChatMessage(user_id=u4.id, sender='bot', message='Hello Sunita. Your consolidated family income is ₹130,000, with total outflows of **₹115,700** leaving a net surplus of **₹14,300 (11% savings rate)**.\n\n⚠️ **Two critical budget overruns detected:**\n1. **Food & Groceries**: ₹29,400 spent vs ₹24,000 budget (**+₹5,400 overrun**).\n2. **Utilities**: ₹10,200 spent vs ₹7,500 limit (**+₹2,700 overrun**, driven by peak electricity consumption).\n\n**Action Plan:** Switch to bi-weekly grocery inventorying to avoid perishable waste, and set AC timer thresholds. Reclaiming these overruns adds **₹8,100/mo** directly into your **Children Higher Education Corpus**!')
    ])

    db.session.commit()
    print("[Seed] Successfully seeded 4 realistic financial planning scenarios!")
