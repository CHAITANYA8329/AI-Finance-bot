# 🪙 Personal Finance Advisor Bot

A complete, production-ready, full-stack personal finance web application built with **React**, **Vite**, **Tailwind CSS**, and **Python Flask**. Features an **AI-powered financial insights advisor**, real-time budget burn rate monitoring, income vs. expense tracking, savings goals with visual progress, interactive charts, monthly financial reports, and CSV export.

---

## 🌟 Key Features

- **🔐 Secure Authentication & User Management**
  - Email & password registration with Argon2 / Werkzeug password hashing.
  - JWT (JSON Web Token) bearer authorization.
  - Profile customization (full name, currency selector: USD, EUR, GBP, INR, CAD, AUD).
  - **1-Click Demo Login** (`Alex Rivera`) with pre-seeded, realistic transactions.

- **📊 Comprehensive Financial Dashboard**
  - Real-time KPI metric cards: **All-Time Net Balance**, **Monthly Inflow**, **Monthly Outflow**, and **Savings Rate**.
  - **Financial Health Scorecard (0–100)**: Evaluates emergency reserves, savings rates, cash flow, and budget compliance.
  - **6-Month Cash Flow Trend**: Interactive bar & trend comparison with tooltips.
  - **Category Spending Donut**: Interactive breakdown with category pills and percentage shares.
  - **Active Budget Alerts**: Instant warnings for categories nearing or exceeding limits.

- **💳 Transaction Management (Ledger)**
  - Full CRUD operations: Add, Edit, View, and Delete transactions.
  - Filters by Type (`Income` / `Expense`), Category, and custom Date Ranges.
  - Real-time search by description and notes.
  - Recurring transaction tracking flags (Rent, Salary, Subscriptions).
  - **CSV Export**: Instant download of all transactions for external spreadsheet audits.

- **🎯 Monthly Budgets & Burn Rate Alerts**
  - Set spending caps per category (e.g., Dining, Groceries, Shopping).
  - Real-time calculation of spent vs. remaining buffer.
  - Configurable alert thresholds (e.g., alert at 80% utilization; critical warning at 100%+).
  - Visual color-coded progress bars (Green < 80%, Yellow 80–99%, Red ≥ 100%).

- **🏆 Savings & Wealth Goals**
  - Set target amounts, categories, and target completion dates.
  - Track current saved amounts with visual progress rings.
  - Quick deposit and withdrawal modal with live balance preview.
  - Automatic goal completion detection (`in_progress` → `achieved`).

- **📑 Monthly Financial Performance Reports**
  - Select any month/year statement.
  - Automated **50 / 30 / 20 Personal Finance Benchmark** calculation:
    - 50% Needs (Rent, Utilities, Groceries)
    - 30% Wants / Lifestyle (Dining, Shopping, Entertainment)
    - 20% Savings & Debt Repayment
  - Category-by-category expense share audit.
  - Print / Save as PDF capability.

- **🤖 AI-Powered Financial Advisor Bot**
  - Analyzes **only the authenticated user's verified financial data**.
  - Provides personalized budgeting tips, identifies highest spending categories, and advises on saving goals.
  - Supports **Google Gemini 1.5 Flash** and **OpenAI GPT-4o-mini** via environment variables.
  - **Intelligent Heuristic Fallback Engine**: If no API key is provided or the connection is offline, an internal rule-based CFP analyst engine inspects the user's live database metrics and provides numbers-backed Markdown advice.
  - Clickable suggestion prompt chips for rapid analysis.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | React 19 + Vite 8 | Ultra-fast client, responsive modular component structure |
| **Styling** | Tailwind CSS 3.4 | Fintech dark aesthetic, glassmorphic cards, emerald & cyan accents |
| **Icons** | Lucide React | Modern fintech iconography |
| **Backend** | Python Flask 3.0 | RESTful API with modular Blueprints and service layers |
| **ORM / Database** | SQLAlchemy 2.0 | SQLite (development) & PostgreSQL ready (production) |
| **Auth** | PyJWT | HMAC-SHA256 bearer tokens with 7-day expiration |
| **AI Intelligence** | Gemini / OpenAI / Heuristic | Dual LLM support with offline heuristic CFP fallback engine |
| **Testing** | Pytest 8.2 | Automated unit and integration test suite |

---

## 📁 Project Architecture

```
Personalfinanceadvoicer_bot_chaitanya pawar/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py          # SQLAlchemy instance & exports
│   │   │   ├── user.py              # User model & password hashing
│   │   │   ├── transaction.py       # Transaction ledger model
│   │   │   ├── budget.py            # Category budget caps model
│   │   │   ├── goal.py              # Savings goals model
│   │   │   └── chat.py              # AI conversation history model
│   │   ├── routes/
│   │   │   ├── auth.py              # Login, register, demo-login, profile
│   │   │   ├── transactions.py      # CRUD, categories, CSV export
│   │   │   ├── budgets.py           # Budget progress & alert status
│   │   │   ├── goals.py             # Goals CRUD & deposit/withdraw
│   │   │   ├── analytics.py         # Dashboard metrics & monthly reports
│   │   │   └── ai_advisor.py        # AI chat, prompt chips, history
│   │   ├── services/
│   │   │   ├── ai_service.py        # Gemini/OpenAI & CFP heuristic engine
│   │   │   └── report_service.py    # Report generator & CSV builder
│   │   ├── utils/
│   │   │   └── auth.py              # JWT token generator & @token_required
│   │   ├── config.py                # App configuration (SQLite/Postgres)
│   │   └── __init__.py              # Flask app factory & CORS
│   ├── tests/
│   │   ├── conftest.py              # Test suite configuration
│   │   └── test_finance_api.py      # Comprehensive API tests
│   ├── run.py                       # Backend server entrypoint
│   ├── seed.py                      # Realistic sample data seeder
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Sample environment variables
│   └── .env                         # Local environment configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx          # Collapsible navigation & AI banner
│   │   │   ├── Header.jsx           # Top bar, alert notifications, quick add
│   │   │   ├── Modal.jsx            # Reusable modal container
│   │   │   ├── StatCard.jsx         # Metric card with trends
│   │   │   ├── TransactionModal.jsx # Add/edit transaction form
│   │   │   ├── BudgetModal.jsx      # Budget cap & threshold slider
│   │   │   ├── GoalModal.jsx        # Savings goal creator
│   │   │   ├── DepositModal.jsx     # Deposit/withdraw funds with live preview
│   │   │   └── InteractiveCharts.jsx# SVG cashflow and category donut charts
│   │   ├── context/
│   │   │   └── AuthContext.jsx      # Authentication & user state
│   │   ├── services/
│   │   │   └── api.js               # Centralized fetch wrapper & endpoints
│   │   ├── views/
│   │   │   ├── DashboardView.jsx    # Metric overview, charts, recent table
│   │   │   ├── TransactionsView.jsx # Ledger, search, filter, CSV download
│   │   │   ├── BudgetsView.jsx      # Category caps & alert cards
│   │   │   ├── GoalsView.jsx        # Savings goals cards & progress
│   │   │   ├── ReportsView.jsx      # Monthly statements & 50/30/20 audit
│   │   │   ├── AdvisorView.jsx      # AI chatbot interface with suggestions
│   │   │   └── LoginView.jsx        # Auth card with 1-click demo login
│   │   ├── App.jsx                  # Main view coordinator
│   │   ├── main.jsx                 # React root with AuthProvider
│   │   └── index.css                # Tailwind base & glassmorphic styling
│   ├── package.json                 # Frontend dependencies & scripts
│   ├── vite.config.js               # Vite config with backend proxy
│   ├── tailwind.config.js           # Theme colors & fonts
│   └── index.html                   # HTML shell with Google fonts
└── README.md
```

---

## 🚀 Quickstart Guide (Windows PowerShell)

Follow these exact commands in **Windows PowerShell** to install dependencies, seed the database, and launch both servers.

### 1. Clone or Open the Workspace

```powershell
cd "d:\Personalfinanceadvoicer_bot_chaitanya pawar"
```

---

### 2. Backend Setup (Python Flask)

#### Step 2.1: Create Virtual Environment and Install Dependencies
```powershell
# Create Python virtual environment
python -m venv backend\venv

# Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# Upgrade pip and install all backend requirements
pip install -r backend\requirements.txt
```

#### Step 2.2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item backend\.env.example backend\.env
```
*(Optional: If you want to use Google Gemini or OpenAI, edit `backend\.env` and set `GEMINI_API_KEY=your_key` or `OPENAI_API_KEY=your_key`. If omitted, the internal heuristic financial engine runs automatically).*

#### Step 2.3: Seed the Database with Sample Data
```powershell
# Run the database seeder to populate demo user, realistic transactions, budgets, and goals
python backend\seed.py
```

#### Step 2.4: Run Backend Tests
```powershell
# Execute the automated test suite
python -m pytest backend\tests
```

#### Step 2.5: Start the Backend Server
```powershell
python backend\run.py
```
> The Flask REST API will start on: **`http://127.0.0.1:5000`**

---

### 3. Frontend Setup (React + Vite + Tailwind)

Open a **new Windows PowerShell terminal** window:

```powershell
cd "d:\Personalfinanceadvoicer_bot_chaitanya pawar\frontend"

# Install frontend dependencies
npm.cmd install

# Start Vite development server
npm.cmd run dev
```
> The frontend application will be live at: **`http://localhost:5173`**

---

## 🔑 Demo Account Credentials

You can click the **"Explore Demo Account (Alex Rivera)"** button directly on the login screen to enter immediately without typing, or manually sign in with:

- **Email**: `demo@financeadvisor.com`
- **Password**: `demo1234`

---

## 📡 REST API Documentation

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Log in and receive JWT token | No |
| `POST` | `/api/auth/demo-login` | Instant demo login for evaluation | No |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | Bearer Token |
| `PUT` | `/api/auth/profile` | Update profile (name, currency) | Bearer Token |

### Transactions (`/api/transactions`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/transactions` | List transactions with filters (`type`, `category`, `search`, `start_date`, `end_date`) | Bearer Token |
| `POST` | `/api/transactions` | Record new transaction | Bearer Token |
| `GET` | `/api/transactions/<id>` | Retrieve single transaction | Bearer Token |
| `PUT` | `/api/transactions/<id>` | Update transaction details | Bearer Token |
| `DELETE` | `/api/transactions/<id>` | Delete transaction | Bearer Token |
| `GET` | `/api/transactions/categories` | Get user & system category lists | Bearer Token |
| `GET` | `/api/transactions/export/csv` | Download complete ledger as CSV | Bearer Token |

### Budgets (`/api/budgets`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/budgets` | Get category budgets, actual spent, and alert status | Bearer Token |
| `POST` | `/api/budgets` | Set or update category budget cap | Bearer Token |
| `DELETE` | `/api/budgets/<id>` | Remove budget cap | Bearer Token |
| `GET` | `/api/budgets/alerts` | Get list of active over-budget alerts | Bearer Token |

### Savings Goals (`/api/goals`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/goals` | List all savings goals & progress | Bearer Token |
| `POST` | `/api/goals` | Create a new savings target | Bearer Token |
| `PUT` | `/api/goals/<id>` | Update savings target | Bearer Token |
| `DELETE` | `/api/goals/<id>` | Remove goal | Bearer Token |
| `POST` | `/api/goals/<id>/deposit` | Deposit or withdraw funds | Bearer Token |

### Analytics & Reports (`/api/analytics`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/analytics/dashboard` | Executive dashboard KPI summary, 6-mo trend, category breakdown, health score | Bearer Token |
| `GET` | `/api/analytics/monthly-report` | Detailed monthly performance statement & 50/30/20 audit | Bearer Token |

### AI Financial Advisor (`/api/ai`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/ai/chat` | Send prompt to AI advisor; analyzes user data | Bearer Token |
| `GET` | `/api/ai/history` | Retrieve conversation history | Bearer Token |
| `DELETE` | `/api/ai/history` | Clear conversation history | Bearer Token |
| `GET` | `/api/ai/suggestions` | Suggested prompt queries | Bearer Token |

---

## 🗄️ Database Migrations & PostgreSQL Support

The application is configured to use **SQLite** by default (`finance.db`) for zero-configuration local development.

To connect to a **PostgreSQL** database in staging or production:
1. Edit `backend/.env` and update `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/finance_advisor_db
   ```
2. Run database migrations:
   ```powershell
   flask --app backend\run.py db init
   flask --app backend\run.py db migrate -m "Initial schema"
   flask --app backend\run.py db upgrade
   ```

---

## 🧪 Running Automated Tests

All test cases are written using `pytest` and execute against an in-memory SQLite database:
```powershell
python -m pytest backend\tests -v
```

All 5 test suites pass:
1. `test_auth_registration_and_login`: User registration, duplicate checks, login, and token generation.
2. `test_transactions_crud_and_csv`: Income/expense transactions CRUD and CSV file generation.
3. `test_budgets_and_alerts`: Category spending caps, warning thresholds (80%), and alert status.
4. `test_savings_goals`: Goal milestones, deposits, withdrawals, and auto-achievement status.
5. `test_ai_advisor_fallback`: Context generation, prompt analysis, and CFP fallback response engine.

---

## 📦 Production Build

To build the optimized production frontend bundle:
```powershell
cd frontend
npm.cmd run build
```
The compiled assets will be created in `frontend/dist/`.

---

## 🔒 Security Practices Implemented

- **Password Hashing**: Uses `werkzeug.security.generate_password_hash` with secure salt.
- **JWT Protection**: All transactional and personal data endpoints require a valid Bearer token.
- **Data Isolation**: Every database query filters by `user_id == current_user.id`, ensuring users cannot access or view another user's financial data.
- **CORS Protection**: Restricted and configured for development and production domains.
- **Input Sanitization & Validation**: Validation on email formats, numeric amounts, date formats, and transaction types.
