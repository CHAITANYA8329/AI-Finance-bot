/**
 * Main Application Frontend Logic
 */
let currentUser = null;
let currentCurrency = '₹';

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initModals();
  initCharts();
  initChatbot();
  loadDashboardData();
  setupEventListeners();
});

// Tab Switcher
function initTabs() {
  const tabs = document.querySelectorAll('.tab-link');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });
}

// Event Listeners for Forms & Buttons
function setupEventListeners() {
  // Scenario Cards click
  document.querySelectorAll('.scenario-card').forEach(card => {
    card.addEventListener('click', () => {
      const userId = card.getAttribute('data-user-id');
      if (userId) switchUser(userId);
    });
  });

  // Persona buttons in top header
  document.querySelectorAll('.persona-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const userId = btn.getAttribute('data-user-id');
      if (userId) switchUser(userId);
    });
  });

  // Auto Generate AI Budget Button
  const autoBudgetBtn = document.getElementById('btnAutoBudget');
  if (autoBudgetBtn) {
    autoBudgetBtn.addEventListener('click', autoGenerateBudget);
  }

  // Monthly Report Button
  const reportBtn = document.getElementById('btnOpenReport');
  if (reportBtn) {
    reportBtn.addEventListener('click', openMonthlyReportModal);
  }

  // Reset Demo Data Button
  const resetBtn = document.getElementById('btnResetData');
  if (resetBtn) {
    resetBtn.addEventListener('click', resetDemoData);
  }

  // Save Gemini Key Form
  const geminiForm = document.getElementById('formGeminiKey');
  if (geminiForm) {
    geminiForm.addEventListener('submit', saveGeminiKey);
  }

  // Add Income Form
  const incomeForm = document.getElementById('formAddIncome');
  if (incomeForm) {
    incomeForm.addEventListener('submit', handleAddIncome);
  }

  // Add Expense Form
  const expenseForm = document.getElementById('formAddExpense');
  if (expenseForm) {
    expenseForm.addEventListener('submit', handleAddExpense);
  }

  // Add Budget Form
  const budgetForm = document.getElementById('formAddBudget');
  if (budgetForm) {
    budgetForm.addEventListener('submit', handleAddBudget);
  }

  // Add Goal Form
  const goalForm = document.getElementById('formAddGoal');
  if (goalForm) {
    goalForm.addEventListener('submit', handleAddGoal);
  }

  // Deposit Form
  const depositForm = document.getElementById('formDepositGoal');
  if (depositForm) {
    depositForm.addEventListener('submit', handleDepositGoal);
  }

  // Create User Form
  const createUserForm = document.getElementById('formCreateUser');
  if (createUserForm) {
    createUserForm.addEventListener('submit', handleCreateUser);
  }
}

// Fetch and render all Dashboard state
async function loadDashboardData() {
  try {
    const res = await fetch('/api/dashboard');
    if (!res.ok) throw new Error('Failed to load dashboard data');
    const data = await res.json();

    currentUser = data.user;
    currentCurrency = data.user.currency || '₹';
    window.currentCurrency = currentCurrency;

    renderUserHeader(data.user);
    renderMetrics(data.metrics, data.health);
    renderHealthGauge(data.health);
    renderBudgetBars(data.budgets, data.overspent_categories);
    renderRecentIncomes(data.recent_incomes);
    renderRecentExpenses(data.recent_expenses);
    renderGoals(data.goals);
    renderOverspendingAlerts(data.overspent_categories, data.budgets);

    // Update charts
    updateCharts(data.metrics, data.top_expenses, currentCurrency);

    // Update scenarios cards active state
    updateScenariosActiveState(data.user.id);

  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

// Switch Active Persona / User
async function switchUser(userId) {
  try {
    const res = await fetch('/api/users/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: parseInt(userId) })
    });
    if (res.ok) {
      await loadDashboardData();
      await loadChatHistory();
    }
  } catch (err) {
    console.error('Error switching user:', err);
  }
}

function updateScenariosActiveState(currentUserId) {
  document.querySelectorAll('.scenario-card').forEach(card => {
    if (card.getAttribute('data-user-id') == currentUserId) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });

  document.querySelectorAll('.persona-btn').forEach(btn => {
    if (btn.getAttribute('data-user-id') == currentUserId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

function renderUserHeader(user) {
  const nameEl = document.getElementById('headerUserName');
  const personaBadge = document.getElementById('headerPersonaBadge');
  const bannerName = document.getElementById('bannerUserName');
  const bannerPersona = document.getElementById('bannerPersona');
  const bannerDesc = document.getElementById('bannerDescription');

  if (nameEl) nameEl.textContent = user.full_name;
  if (personaBadge) personaBadge.textContent = user.persona.toUpperCase();
  if (bannerName) bannerName.textContent = user.full_name;
  if (bannerPersona) bannerPersona.textContent = user.persona.toUpperCase();

  // Persona descriptive banner context
  const descriptions = {
    salaried: 'Salaried Professional: tracking monthly salary, rent, food, transport, and curtailing weekend entertainment overruns with the 50/30/20 budget framework.',
    student: 'College Student: managing restricted monthly allowance, mess bills, and textbooks while putting aside savings towards tech upgrades.',
    freelancer: 'Freelancer with Variable Cashflows: tracking diverse client invoice payouts and building a resilient 6-month lean runway buffer.',
    household: 'Household Financial Manager: coordinating shared family income pool across groceries, utilities, school fees, and medical contingencies.'
  };

  if (bannerDesc) {
    bannerDesc.textContent = descriptions[user.persona] || 'Personalized AI financial guidance active.';
  }
}

function renderMetrics(metrics, health) {
  const incomeEl = document.getElementById('metricTotalIncome');
  const expenseEl = document.getElementById('metricTotalExpense');
  const savingsEl = document.getElementById('metricNetSavings');
  const runwayEl = document.getElementById('metricRunway');

  const savingsRateEl = document.getElementById('metricSavingsRate');
  const essentialEl = document.getElementById('metricEssentialSpending');
  const discretionaryEl = document.getElementById('metricDiscretionarySpending');

  if (incomeEl) incomeEl.textContent = `${currentCurrency}${metrics.total_income.toLocaleString()}`;
  if (expenseEl) expenseEl.textContent = `${currentCurrency}${metrics.total_expense.toLocaleString()}`;
  if (savingsEl) savingsEl.textContent = `${currentCurrency}${metrics.net_savings.toLocaleString()}`;
  if (runwayEl) runwayEl.textContent = `${metrics.emergency_runway_months} Mo`;

  if (savingsRateEl) savingsRateEl.textContent = `${metrics.savings_rate}%`;
  if (essentialEl) essentialEl.textContent = `${currentCurrency}${metrics.essential_spending.toLocaleString()}`;
  if (discretionaryEl) discretionaryEl.textContent = `${currentCurrency}${metrics.discretionary_spending.toLocaleString()}`;
}

// Financial Health Gauge
function renderHealthGauge(health) {
  const scoreNum = document.getElementById('gaugeScoreNum');
  const circle = document.getElementById('gaugeCircleProgress');
  const badge = document.getElementById('healthStatusBadge');
  const summary = document.getElementById('healthSummaryText');
  const headerScore = document.getElementById('headerHealthScore');

  if (scoreNum) scoreNum.textContent = health.score;
  if (headerScore) headerScore.textContent = `Health: ${health.score}/100`;

  if (badge) {
    badge.textContent = health.status;
    badge.style.backgroundColor = `${health.badge_color}20`;
    badge.style.color = health.badge_color;
    badge.style.border = `1px solid ${health.badge_color}50`;
  }

  if (summary) summary.textContent = health.summary;

  if (circle) {
    // 440 is the circle circumference (2 * pi * 70)
    const offset = 440 - (440 * (health.score / 100));
    circle.style.strokeDashoffset = offset;
    circle.style.stroke = health.badge_color;
  }

  // Mini breakdown bars
  const b = health.breakdown;
  if (b) {
    setMiniBar('barSavings', (b.savings_score / 35) * 100);
    setMiniBar('barSpending', (b.spending_control_score / 30) * 100);
    setMiniBar('barEssential', (b.essential_balance_score / 20) * 100);
    setMiniBar('barGoals', (b.goals_score / 15) * 100);
  }
}

function setMiniBar(id, pct) {
  const el = document.getElementById(id);
  if (el) el.style.width = `${Math.min(100, Math.max(5, pct))}%`;
}

// Overspending Alerts Banner
function renderOverspendingAlerts(overspent, budgets) {
  const container = document.getElementById('alertsContainer');
  if (!container) return;

  if (!overspent || overspent.length === 0) {
    container.innerHTML = `
      <div class="alert-banner" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3);">
        <div class="alert-info">
          <div class="alert-icon" style="color: var(--accent-income);">✓</div>
          <div class="alert-desc">
            <strong>Spending On Track</strong>
            <p>None of your active budget categories have breached their limits. Keep it up!</p>
          </div>
        </div>
      </div>
    `;
    return;
  }

  let html = '';
  overspent.forEach(cat => {
    const b = budgets.find(item => item.category === cat);
    const limit = b ? `${currentCurrency}${b.limit.toLocaleString()}` : '';
    const spent = b ? `${currentCurrency}${b.spent.toLocaleString()}` : '';
    html += `
      <div class="alert-banner">
        <div class="alert-info">
          <div class="alert-icon">⚠️</div>
          <div class="alert-desc">
            <strong>Budget Exceeded in ${cat}</strong>
            <p>You have spent ${spent} against a limit of ${limit}. Click the AI Advisor to get targeted reduction strategies.</p>
          </div>
        </div>
        <button class="btn btn-outline" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="askAIBoutOverspending('${cat}')">
          AI Fix Plan
        </button>
      </div>
    `;
  });
  container.innerHTML = html;
}

window.askAIBoutOverspending = function(category) {
  const drawer = document.getElementById('chatDrawer');
  if (drawer) drawer.classList.add('open');
  const inputEl = document.getElementById('chatInput');
  if (inputEl) {
    inputEl.value = `I overspent in ${category}. What are practical steps to reduce costs here?`;
    document.getElementById('chatSendBtn').click();
  }
};

// Category Budget Bars
function renderBudgetBars(budgets, overspent) {
  const container = document.getElementById('budgetBarsContainer');
  const tableBody = document.getElementById('budgetTableBody');
  if (!container) return;

  if (!budgets || budgets.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No budgets configured yet. Click "Auto-Generate AI Budget" above to start!</p>';
    if (tableBody) tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No budgets configured.</td></tr>';
    return;
  }

  let cardsHtml = '';
  let rowsHtml = '';

  budgets.forEach(b => {
    const isOver = b.spent > b.limit;
    const isWarning = b.pct_used >= 80 && !isOver;
    const colorClass = isOver ? 'red' : (isWarning ? 'amber' : 'green');
    const widthPct = Math.min(100, b.pct_used);

    cardsHtml += `
      <div class="category-bar-item">
        <div class="cat-header">
          <span class="cat-name">${b.category}</span>
          <span class="cat-amount">${currentCurrency}${b.spent.toLocaleString()} / <span style="color: var(--text-muted); font-size: 0.8rem;">${currentCurrency}${b.limit.toLocaleString()}</span></span>
        </div>
        <div class="cat-progress-track">
          <div class="cat-progress-fill ${colorClass}" style="width: ${widthPct}%;"></div>
        </div>
        <div class="cat-sub-info">
          <span>${b.pct_used}% utilized</span>
          <span style="color: ${isOver ? 'var(--accent-expense)' : (isWarning ? 'var(--accent-warning)' : 'var(--accent-income)')};">
            ${isOver ? `Over by ${currentCurrency}${(b.spent - b.limit).toLocaleString()}` : `${currentCurrency}${b.remaining.toLocaleString()} left`}
          </span>
        </div>
      </div>
    `;

    rowsHtml += `
      <tr>
        <td><strong>${b.category}</strong></td>
        <td>${currentCurrency}${b.limit.toLocaleString()}</td>
        <td>${currentCurrency}${b.spent.toLocaleString()}</td>
        <td>
          <span class="badge-tag ${isOver ? 'badge-discretionary' : 'badge-essential'}">
            ${isOver ? 'Over Budget' : (isWarning ? 'Near Limit' : 'On Track')} (${b.pct_used}%)
          </span>
        </td>
        <td>
          <button class="btn btn-outline" style="padding: 0.2rem 0.5rem; font-size: 0.72rem; color: var(--accent-expense);" onclick="deleteBudget(${b.id})">Delete</button>
        </td>
      </tr>
    `;
  });

  container.innerHTML = cardsHtml;
  if (tableBody) tableBody.innerHTML = rowsHtml;
}

// Incomes Table
function renderRecentIncomes(incomes) {
  const table = document.getElementById('incomeTableBody');
  if (!table) return;

  if (!incomes || incomes.length === 0) {
    table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No income entries logged yet.</td></tr>';
    return;
  }

  let html = '';
  incomes.forEach(i => {
    html += `
      <tr>
        <td>${i.date}</td>
        <td><strong>${i.source}</strong></td>
        <td><span class="badge-tag" style="background: rgba(99, 102, 241, 0.15); color: #818cf8;">${i.category}</span></td>
        <td>${i.frequency}</td>
        <td style="color: var(--accent-income); font-weight: 700;">+${currentCurrency}${i.amount.toLocaleString()}</td>
        <td>
          <button class="btn btn-outline" style="padding: 0.2rem 0.5rem; font-size: 0.72rem; color: var(--accent-expense);" onclick="deleteIncome(${i.id})">Delete</button>
        </td>
      </tr>
    `;
  });
  table.innerHTML = html;
}

// Expenses Table
function renderRecentExpenses(expenses) {
  const table = document.getElementById('expenseTableBody');
  if (!table) return;

  if (!expenses || expenses.length === 0) {
    table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No expenses logged yet.</td></tr>';
    return;
  }

  let html = '';
  expenses.forEach(e => {
    html += `
      <tr>
        <td>${e.date}</td>
        <td><strong>${e.title}</strong></td>
        <td><span class="badge-tag" style="background: rgba(255, 255, 255, 0.06);">${e.category}</span></td>
        <td>
          <span class="badge-tag ${e.is_essential ? 'badge-essential' : 'badge-discretionary'}">
            ${e.is_essential ? 'Essential' : 'Discretionary'}
          </span>
        </td>
        <td style="color: var(--accent-expense); font-weight: 700;">-${currentCurrency}${e.amount.toLocaleString()}</td>
        <td>
          <button class="btn btn-outline" style="padding: 0.2rem 0.5rem; font-size: 0.72rem; color: var(--accent-expense);" onclick="deleteExpense(${e.id})">Delete</button>
        </td>
      </tr>
    `;
  });
  table.innerHTML = html;
}

// Goals Cards
function renderGoals(goals) {
  const container = document.getElementById('goalsContainer');
  if (!container) return;

  if (!goals || goals.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No savings goals created yet. Click "Add Goal" to set one!</p>';
    return;
  }

  let html = '';
  goals.forEach(g => {
    const isCompleted = g.current_amount >= g.target_amount;
    html += `
      <div class="goal-card glass-panel">
        <div class="goal-top">
          <div>
            <div class="goal-title">${g.title}</div>
            <div class="goal-category">${g.category}</div>
          </div>
          <span class="badge-tag ${isCompleted ? 'badge-essential' : 'badge-tag'}" style="${!isCompleted ? 'background: rgba(6, 182, 212, 0.15); color: var(--accent-ai-cyan);' : ''}">
            ${isCompleted ? 'Completed' : `${g.progress_percentage}%`}
          </span>
        </div>

        <div class="goal-amounts">
          <span class="goal-current">${currentCurrency}${g.current_amount.toLocaleString()}</span>
          <span class="goal-target">of ${currentCurrency}${g.target_amount.toLocaleString()}</span>
        </div>

        <div class="goal-progress-bar">
          <div class="goal-progress-fill" style="width: ${g.progress_percentage}%;"></div>
        </div>

        <div class="goal-meta">
          <span>Target Date: ${g.target_date || 'Ongoing'}</span>
          <span>${currentCurrency}${Math.max(0, g.target_amount - g.current_amount).toLocaleString()} remaining</span>
        </div>

        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
          <button class="btn btn-primary" style="flex: 1; font-size: 0.8rem; padding: 0.4rem 0.6rem;" onclick="openDepositModal(${g.id}, '${g.title.replace(/'/g, "\\'")}', ${g.target_amount}, ${g.current_amount})">
            + Deposit
          </button>
          <button class="btn btn-outline" style="padding: 0.4rem 0.6rem; font-size: 0.75rem; color: var(--accent-expense);" onclick="deleteGoal(${g.id})">
            Delete
          </button>
        </div>
      </div>
    `;
  });
  container.innerHTML = html;
}

// Auto-Generate AI Budget
async function autoGenerateBudget() {
  const btn = document.getElementById('btnAutoBudget');
  const origText = btn.innerHTML;
  btn.innerHTML = '⚡ Generating Budget...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/budgets/auto-generate', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      await loadDashboardData();
      alert(`AI Budget Applied for ${data.plan.persona.toUpperCase()}!\n${data.plan.advice}`);
    } else {
      alert(`Failed to auto-generate: ${data.error}`);
    }
  } catch (err) {
    alert('Error connecting to backend API');
  } finally {
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

// Monthly Report Modal
async function openMonthlyReportModal() {
  const modal = document.getElementById('modalMonthlyReport');
  const body = document.getElementById('reportModalBody');
  if (!modal || !body) return;

  body.innerHTML = '<div style="text-align: center; padding: 2rem;">Loading comprehensive financial report...</div>';
  modal.classList.add('open');

  try {
    const res = await fetch('/api/reports/monthly');
    const data = await res.json();
    const r = data.report;
    const curr = r.currency;

    let catRows = '';
    r.category_spending.forEach(c => {
      catRows += `
        <tr>
          <td><strong>${c.category}</strong></td>
          <td>${curr}${c.amount.toLocaleString()}</td>
          <td>${c.pct}%</td>
        </tr>
      `;
    });

    let budgetRows = '';
    r.budget_analysis.forEach(b => {
      const isOver = b.status === 'Over Budget';
      budgetRows += `
        <tr>
          <td>${b.category}</td>
          <td>${curr}${b.limit.toLocaleString()}</td>
          <td>${curr}${b.spent.toLocaleString()}</td>
          <td style="color: ${isOver ? 'var(--accent-expense)' : 'var(--accent-income)'}; font-weight: 600;">
            ${b.status} (${b.pct_used}%)
          </td>
        </tr>
      `;
    });

    let goalsList = r.next_month_goals.map(g => `<li>${g}</li>`).join('');
    let insightsList = r.ai_insights.map(i => `<li>${i}</li>`).join('');

    body.innerHTML = `
      <div class="report-header-banner">
        <h2>Personal Financial Advisory Statement</h2>
        <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.25rem;">
          Prepared for <strong>${r.user.full_name}</strong> (${r.user.persona.toUpperCase()}) | Statement Period: <strong>${r.period}</strong>
        </p>
      </div>

      <div class="report-grid-summary">
        <div class="report-summary-box">
          <h4>Total Income</h4>
          <div class="val text-emerald">${curr}${r.summary.total_income.toLocaleString()}</div>
        </div>
        <div class="report-summary-box">
          <h4>Total Expenses</h4>
          <div class="val text-coral">${curr}${r.summary.total_expense.toLocaleString()}</div>
        </div>
        <div class="report-summary-box">
          <h4>Net Savings</h4>
          <div class="val text-cyan">${curr}${r.summary.net_savings.toLocaleString()} (${r.summary.savings_rate}%)</div>
        </div>
      </div>

      <div style="background: rgba(255, 255, 255, 0.02); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
        <h3 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #fff;">🩺 AI Financial Health Rating: <span style="color: ${r.health.badge_color}">${r.health.score}/100 (${r.health.status})</span></h3>
        <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">${r.health.summary}</p>
        <ul style="padding-left: 1.2rem; margin-top: 0.75rem; font-size: 0.84rem; color: var(--text-secondary);">
          ${insightsList}
        </ul>
      </div>

      <h3 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #fff;">📊 Spending by Category</h3>
      <table class="data-table" style="margin-bottom: 1.5rem;">
        <thead>
          <tr><th>Category</th><th>Amount</th><th>Share of Outflows</th></tr>
        </thead>
        <tbody>${catRows || '<tr><td colspan="3">No expenses recorded</td></tr>'}</tbody>
      </table>

      <h3 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #fff;">🎯 Budget Variance Breakdown</h3>
      <table class="data-table" style="margin-bottom: 1.5rem;">
        <thead>
          <tr><th>Category</th><th>Budget Limit</th><th>Actual Spent</th><th>Status</th></tr>
        </thead>
        <tbody>${budgetRows || '<tr><td colspan="4">No budgets set</td></tr>'}</tbody>
      </table>

      <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); padding: 1.25rem; border-radius: var(--radius-md);">
        <h4 style="font-size: 0.9rem; margin-bottom: 0.5rem; color: #fff;">🚀 Actionable Objectives for Next Month:</h4>
        <ul style="padding-left: 1.2rem; font-size: 0.85rem; line-height: 1.6; color: var(--text-secondary);">
          ${goalsList}
        </ul>
      </div>
    `;
  } catch (err) {
    body.innerHTML = '<div style="color: var(--accent-expense);">Failed to generate report. Please try again.</div>';
  }
}

// Reset Demo Data
async function resetDemoData() {
  if (!confirm('Reset and re-seed all 4 scenario datasets? Current modifications will be reset to factory defaults.')) return;
  try {
    const res = await fetch('/api/reset-data', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      alert('Data reset successfully!');
      window.location.reload();
    }
  } catch (e) {
    alert('Reset failed');
  }
}

// Modals Handler
function initModals() {
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
    });
  });

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('open');
      }
    });
  });

  // Open modal buttons
  const map = {
    'btnOpenAddIncome': 'modalAddIncome',
    'btnOpenAddExpense': 'modalAddExpense',
    'btnOpenAddBudget': 'modalAddBudget',
    'btnOpenAddGoal': 'modalAddGoal',
    'btnOpenGeminiSettings': 'modalGeminiSettings',
    'btnOpenCreateUser': 'modalCreateUser'
  };

  Object.entries(map).forEach(([btnId, modalId]) => {
    const btn = document.getElementById(btnId);
    const modal = document.getElementById(modalId);
    if (btn && modal) {
      btn.addEventListener('click', () => modal.classList.add('open'));
    }
  });
}

// Delete Handlers
window.deleteIncome = async function(id) {
  if (!confirm('Delete this income record?')) return;
  await fetch(`/api/incomes/${id}`, { method: 'DELETE' });
  loadDashboardData();
};

window.deleteExpense = async function(id) {
  if (!confirm('Delete this expense record?')) return;
  await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
  loadDashboardData();
};

window.deleteBudget = async function(id) {
  if (!confirm('Remove this budget?')) return;
  await fetch(`/api/budgets/${id}`, { method: 'DELETE' });
  loadDashboardData();
};

window.deleteGoal = async function(id) {
  if (!confirm('Delete this goal?')) return;
  await fetch(`/api/goals/${id}`, { method: 'DELETE' });
  loadDashboardData();
};

window.openDepositModal = function(id, title, target, current) {
  const modal = document.getElementById('modalDepositGoal');
  if (!modal) return;
  document.getElementById('depositGoalId').value = id;
  document.getElementById('depositGoalTitle').textContent = `Deposit into: ${title}`;
  document.getElementById('depositGoalRemaining').textContent = `Remaining: ${currentCurrency}${(target - current).toLocaleString()}`;
  document.getElementById('depositAmount').value = '';
  modal.classList.add('open');
};

// Form Submission Handlers
async function handleAddIncome(e) {
  e.preventDefault();
  const source = document.getElementById('incomeSource').value;
  const amount = parseFloat(document.getElementById('incomeAmount').value);
  const category = document.getElementById('incomeCategory').value;
  const frequency = document.getElementById('incomeFrequency').value;
  const date = document.getElementById('incomeDate').value;
  const notes = document.getElementById('incomeNotes').value;

  const res = await fetch('/api/incomes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, amount, category, frequency, date, notes })
  });
  if (res.ok) {
    document.getElementById('modalAddIncome').classList.remove('open');
    document.getElementById('formAddIncome').reset();
    loadDashboardData();
  }
}

async function handleAddExpense(e) {
  e.preventDefault();
  const title = document.getElementById('expenseTitle').value;
  const amount = parseFloat(document.getElementById('expenseAmount').value);
  const category = document.getElementById('expenseCategory').value;
  const is_essential = document.getElementById('expenseEssential').checked;
  const date = document.getElementById('expenseDate').value;
  const notes = document.getElementById('expenseNotes').value;

  const res = await fetch('/api/expenses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, amount, category, is_essential, date, notes })
  });
  if (res.ok) {
    document.getElementById('modalAddExpense').classList.remove('open');
    document.getElementById('formAddExpense').reset();
    loadDashboardData();
  }
}

async function handleAddBudget(e) {
  e.preventDefault();
  const category = document.getElementById('budgetCategory').value;
  const monthly_limit = parseFloat(document.getElementById('budgetLimit').value);
  const alert_threshold = parseFloat(document.getElementById('budgetThreshold').value || 85);

  const res = await fetch('/api/budgets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, monthly_limit, alert_threshold })
  });
  if (res.ok) {
    document.getElementById('modalAddBudget').classList.remove('open');
    document.getElementById('formAddBudget').reset();
    loadDashboardData();
  }
}

async function handleAddGoal(e) {
  e.preventDefault();
  const title = document.getElementById('goalTitle').value;
  const target_amount = parseFloat(document.getElementById('goalTarget').value);
  const current_amount = parseFloat(document.getElementById('goalCurrent').value || 0);
  const category = document.getElementById('goalCategory').value;
  const target_date = document.getElementById('goalDate').value;

  const res = await fetch('/api/goals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, target_amount, current_amount, category, target_date })
  });
  if (res.ok) {
    document.getElementById('modalAddGoal').classList.remove('open');
    document.getElementById('formAddGoal').reset();
    loadDashboardData();
  }
}

async function handleDepositGoal(e) {
  e.preventDefault();
  const id = document.getElementById('depositGoalId').value;
  const amount = parseFloat(document.getElementById('depositAmount').value);

  const res = await fetch(`/api/goals/${id}/deposit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount })
  });
  if (res.ok) {
    document.getElementById('modalDepositGoal').classList.remove('open');
    loadDashboardData();
  }
}

async function handleCreateUser(e) {
  e.preventDefault();
  const full_name = document.getElementById('createFullName').value;
  const username = document.getElementById('createUsername').value;
  const email = document.getElementById('createEmail').value;
  const persona = document.getElementById('createPersona').value;
  const currency = document.getElementById('createCurrency').value;
  const monthly_income_target = parseFloat(document.getElementById('createIncomeTarget').value || 0);

  const res = await fetch('/api/users/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name, username, email, persona, currency, monthly_income_target })
  });
  const data = await res.json();
  if (res.ok) {
    document.getElementById('modalCreateUser').classList.remove('open');
    window.location.reload();
  } else {
    alert(data.error || 'Failed to create user');
  }
}

async function saveGeminiKey(e) {
  e.preventDefault();
  const key = document.getElementById('geminiApiKeyInput').value.trim();
  const statusMsg = document.getElementById('geminiStatusMsg');

  try {
    const res = await fetch('/api/settings/gemini-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key })
    });
    const data = await res.json();
    if (data.success) {
      statusMsg.innerHTML = `<span style="color: var(--accent-income);">✓ ${data.message}</span>`;
      setTimeout(() => {
        document.getElementById('modalGeminiSettings').classList.remove('open');
      }, 1500);
    }
  } catch (err) {
    statusMsg.innerHTML = '<span style="color: var(--accent-expense);">Failed to update key</span>';
  }
}
