import argparse
import json
import os
from datetime import datetime

EXPENSES_FILE = "expenses.json"


def load_expenses():
    if not os.path.exists(EXPENSES_FILE):
        return []
    with open(EXPENSES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def summary_expenses(expenses, month=None):
    filtered = expenses
    if month:
        current_year = datetime.now().year
        filtered = [e for e in expenses if
                    datetime.strptime(e['date'], '%Y-%m-%d').year == current_year and
                    datetime.strptime(e['date'], '%Y-%m-%d').month == month]
        month_name = datetime(1900, month, 1).strftime('%B')
        total = sum(e['amount'] for e in filtered)
        print(f"Total expenses for {month_name}: ${total:.2f}")
    else:
        total = sum(e['amount'] for e in filtered)
        print(f"Total expenses: ${total:.2f}")
        
def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=4)


def generate_expense_id(expenses):
    if not expenses:
        return 1
    return max(expense["id"] for expense in expenses) + 1


def delete_expense(expenses, expense_id):
    for i, exp in enumerate(expenses):
        if exp['id'] == expense_id:
            del expenses[i]
            save_expenses(expenses)
            print(f"Expense ID {expense_id} deleted successfully.")
            return
    print(f"Expense ID {expense_id} not found.")

def update_expense(expenses, expense_id, new_description=None, new_amount=None):
    for exp in expenses:
        if exp['id'] == expense_id:
            if new_description is not None:
                exp['description'] = new_description
            if new_amount is not None:
                exp['amount'] = new_amount
            save_expenses(expenses)
            print(f"Expense ID {expense_id} updated successfully.")
            return
    print(f"Expense ID {expense_id} not found.")

parser = argparse.ArgumentParser(description="Expense Tracker CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser('add', help='Add a new expense')
add_parser.add_argument('--description', required=True, help='Description of the expense')
add_parser.add_argument('--amount', type=float, required=True, help='Amount of the expense')

list_parser = subparsers.add_parser('list', help='List all expenses')

delete_parser = subparsers.add_parser('delete', help='Delete an expense by ID')
delete_parser.add_argument('--id', type=int, required=True, help='ID of the expense to delete')

update_parser = subparsers.add_parser('update', help='Update an existing expense')
update_parser.add_argument('--id', type=int, required=True, help='ID of the expense to update')
update_parser.add_argument('--description', help='New description of the expense')
update_parser.add_argument('--amount', type=float, help='New amount of the expense')

args = parser.parse_args()

expenses = load_expenses()

if args.command == "add":
    new_expense = {
        "id": generate_expense_id(expenses),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": args.description,
        "amount": args.amount 
    }
    expenses.append(new_expense)
    save_expenses(expenses)
    print(f"Expense added successfully (ID: {new_expense['id']})")

elif args.command == "list":
    if not expenses:
        print("No expenses found.")
    else:
        print(f"{'ID':<5} {'Date':<12} {'Description':<20} {'Amount':<10}")
        for exp in expenses:
            print(f"{exp['id']:<5} {exp['date']:<12} {exp['description']:<20} ${exp['amount']:<10.2f}")

elif args.command == "delete":
    delete_expense(expenses, args.id)

elif args.command == "update":
    update_expense(expenses, args.id, args.description, args.amount)
    
elif args.command == "summary":
    summary_expenses(expenses, args.month)

else:
    print("Unknown command")
