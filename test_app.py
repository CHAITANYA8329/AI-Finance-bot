import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:5000'
session = requests.Session()

# 1. Test Home page
r1 = session.get(BASE + '/')
assert r1.status_code == 200, f'Status {r1.status_code}'
assert 'Personal Finance Advisor Bot' in r1.text, 'Title missing'
print('Test 1: Home page loaded successfully!')

# 2. Test Dashboard API
r2 = session.get(BASE + '/api/dashboard')
assert r2.status_code == 200
data2 = r2.json()
assert 'user' in data2 and 'metrics' in data2 and 'health' in data2
user_name = data2['user']['full_name']
health_score = data2['health']['score']
savings = data2['metrics']['net_savings']
print(f'Test 2: Dashboard API loaded for {user_name} (Health: {health_score}/100, Savings: {savings})')

# 3. Test Chatbot API
r3 = session.post(BASE + '/api/chat', json={'message': 'Where am I overspending?'})
assert r3.status_code == 200
data3 = r3.json()
assert 'reply' in data3 and len(data3['reply']) > 10
print('Test 3: AI Chatbot replied:\n' + data3['reply'][:140] + '...')

# 4. Test Persona Switching (Switch to Ananya Verma - Student)
r4 = session.post(BASE + '/api/users/switch', json={'user_id': 2})
assert r4.status_code == 200
r4_dash = session.get(BASE + '/api/dashboard').json()
student_name = r4_dash['user']['full_name']
student_income = r4_dash['metrics']['total_income']
print(f'Test 4: Switched to Student persona: {student_name} (Allowance: {student_income})')

# 5. Test Monthly Report Generation
r5 = session.get(BASE + '/api/reports/monthly')
assert r5.status_code == 200
data5 = r5.json()
period = data5['report']['period']
cats_count = len(data5['report']['category_spending'])
print(f'Test 5: Monthly Report generated for period: {period} with {cats_count} categories')

# 6. Test Auto-Budget AI generation
r6 = session.post(BASE + '/api/budgets/auto-generate')
assert r6.status_code == 200
data6 = r6.json()
alloc_count = len(data6['plan']['allocations'])
print(f'Test 6: AI Auto-Budget generated with {alloc_count} category allocations!')

print('ALL 6 END-TO-END VERIFICATION TESTS PASSED!')
