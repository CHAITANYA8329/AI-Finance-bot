from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    persona = db.Column(db.String(50), default='salaried')  # salaried, student, freelancer, household
    currency = db.Column(db.String(10), default='₹')
    monthly_income_target = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'persona': self.persona,
            'currency': self.currency,
            'monthly_income_target': self.monthly_income_target,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), default='Salary')  # Salary, Freelance, Allowance, Investment, Bonus, Other
    date = db.Column(db.Date, default=date.today)
    frequency = db.Column(db.String(50), default='Monthly')  # Monthly, Weekly, Project-based, One-time
    notes = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'frequency': self.frequency,
            'notes': self.notes
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Rent, Groceries, Transport, Entertainment, etc.
    date = db.Column(db.Date, default=date.today)
    is_essential = db.Column(db.Boolean, default=True)  # Essential vs Discretionary
    notes = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'is_essential': self.is_essential,
            'notes': self.notes
        }

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), default=lambda: date.today().strftime('%Y-%m'))  # YYYY-MM
    alert_threshold = db.Column(db.Float, default=85.0)  # Alert when % spent >= threshold

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'monthly_limit': self.monthly_limit,
            'month': self.month,
            'alert_threshold': self.alert_threshold
        }

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String(80), default='Emergency Fund')
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, paused

    def to_dict(self):
        progress = round((self.current_amount / self.target_amount * 100), 1) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'category': self.category,
            'status': self.status,
            'progress_percentage': min(progress, 100.0)
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sender': self.sender,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
