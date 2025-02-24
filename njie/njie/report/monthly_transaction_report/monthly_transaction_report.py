# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, nowdate, add_days, add_months


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			"fieldname": "date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 150
		
		},
		{
			"fieldname": "withdrawal",
			"label": "Withdrawal",
			"fieldtype": "Currency",
			"width": 200
		},
		# deposit
		{
			"fieldname": "deposit",
			"label": "Deposit",
			"fieldtype": "Currency",
			"width": 200
		},
		# payment
		{
			"fieldname": "payment",
			"label": "Payment",
			"fieldtype": "Currency",
			"width": 200
		},
		# credit 
		{
			"fieldname": "credit",
			"label": "Credit",
			"fieldtype": "Currency",
			"width": 200
		},
		# balance
		{
			"fieldname": "balance",
			"label": "Balance",
			"fieldtype": "Currency",
			"width": 200
		}
	]

	return columns




@frappe.whitelist()
def get_data(filters=None):
    from frappe.utils import get_first_day, get_last_day, today, add_days, flt
    
    # Get the first and last day of the current month
    if filters.get("month") == "All":
            first_day = getdate(filters.get("year") + "-01-01")
            last_day = getdate(filters.get("year") + "-12-31")
    else:
            first_day = get_first_day(filters.get("month") + "," + filters.get("year"))
            last_day = get_last_day(filters.get("month") + "," +  filters.get("year"))
    
    # Fetch all transactions for the current month
    transactions = frappe.get_list(
        "Transactions",
        fields=["date", "amount", "transaction_type", "branch"],
        filters={"date": ["between", [first_day, last_day]]},
        order_by="date asc"
    )
    
    # Initialize a dictionary to store totals by date
    daily_totals = {}

    # Process each transaction
    for transaction in transactions:
        if filters.get("branch") and transaction.branch != filters.get("branch"):
              continue
        date = transaction.date
        amount = flt(transaction.amount)  # Ensure the amount is a float
        transaction_type = transaction.transaction_type.lower()  
        if transaction_type == "credit payment":
              transaction_type = "payment"
        
        # Initialize the date's structure if it doesn't exist
        if date not in daily_totals:
            daily_totals[date] = {
                "date": str(date),  # Include the date as a string
                "deposit": 0,
                "credit": 0,
                "withdrawal": 0,
                "payment": 0,
                "credit_payment": 0,  # Default to 0
                "balance": 0         # Default to 0
            }
        
        # Add amounts to the corresponding transaction type
        if transaction_type in daily_totals[date]:
            daily_totals[date][transaction_type] += amount
        else:
            # Optional: Handle unexpected transaction types dynamically
            daily_totals[date][transaction_type] = amount
    
    # Calculate "balance" and "credit payment" for each date
    for date, totals in daily_totals.items():
        totals["balance"] = totals["credit"] - totals["payment"]

    # Return the result as a list of objects
    return list(daily_totals.values())

