/**
 * Charts Engine using Chart.js
 */
let incomeExpenseChart = null;
let categoryDoughnutChart = null;

function initCharts() {
  const ctxIE = document.getElementById('incomeExpenseChart');
  const ctxCat = document.getElementById('categoryDoughnutChart');

  if (ctxIE) {
    incomeExpenseChart = new Chart(ctxIE, {
      type: 'bar',
      data: {
        labels: ['Total Inflows', 'Total Outflows', 'Net Savings'],
        datasets: [{
          data: [0, 0, 0],
          backgroundColor: [
            'rgba(16, 185, 129, 0.75)', // Income
            'rgba(244, 63, 94, 0.75)',  // Expense
            'rgba(6, 182, 212, 0.75)'   // Savings
          ],
          borderColor: [
            '#10b981',
            '#f43f5e',
            '#06b6d4'
          ],
          borderWidth: 1.5,
          borderRadius: 8,
          barThickness: 38
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1f2937',
            titleColor: '#fff',
            bodyColor: '#9ca3af',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                const curr = window.currentCurrency || '₹';
                return ` ${curr}${context.parsed.y.toLocaleString()}`;
              }
            }
          }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#9ca3af',
              callback: function(val) {
                const curr = window.currentCurrency || '₹';
                return `${curr}${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`;
              }
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#9ca3af', font: { weight: '600' } }
          }
        }
      }
    });
  }

  if (ctxCat) {
    categoryDoughnutChart = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: [],
        datasets: [{
          data: [],
          backgroundColor: [
            '#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4',
            '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#64748b'
          ],
          borderWidth: 2,
          borderColor: '#111827'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#d1d5db',
              font: { size: 11, weight: '500' },
              padding: 12,
              boxWidth: 12,
              boxHeight: 12,
              useBorderRadius: true,
              borderRadius: 4
            }
          },
          tooltip: {
            backgroundColor: '#1f2937',
            titleColor: '#fff',
            bodyColor: '#9ca3af',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                const curr = window.currentCurrency || '₹';
                return ` ${context.label}: ${curr}${context.parsed.toLocaleString()}`;
              }
            }
          }
        }
      }
    });
  }
}

function updateCharts(metrics, topExpenses, currency) {
  window.currentCurrency = currency;

  if (incomeExpenseChart) {
    incomeExpenseChart.data.datasets[0].data = [
      metrics.total_income || 0,
      metrics.total_expense || 0,
      metrics.net_savings || 0
    ];
    incomeExpenseChart.update();
  }

  if (categoryDoughnutChart) {
    if (topExpenses && topExpenses.length > 0) {
      categoryDoughnutChart.data.labels = topExpenses.map(item => item.category);
      categoryDoughnutChart.data.datasets[0].data = topExpenses.map(item => item.amount);
    } else {
      categoryDoughnutChart.data.labels = ['No Expenses Yet'];
      categoryDoughnutChart.data.datasets[0].data = [1];
    }
    categoryDoughnutChart.update();
  }
}
