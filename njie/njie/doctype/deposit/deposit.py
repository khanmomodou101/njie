# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Deposit(Document):
    def on_submit(self):
        self.update_customer_balance()
        self.add_deposit_transaction()
	#update customer balance
    def update_customer_balance(self):
            balance = float(frappe.db.get_value('Customer', self.customer, 'custom_balance')) + self.amount
            frappe.db.set_value('Customer', self.customer, 'custom_balance', balance)
            frappe.msgprint('Deposit added successfully')
    
	#add deposit transacion to customer transactions
    def add_deposit_transaction(self):
         doc = frappe.get_doc('Customer', self.customer)
         doc.append('custom_transactions', {
			 'date': self.posting_date,
            'reference': self.name,
			 'transaction_type': 'Deposit',
			 'amount': self.amount,
		 })
         doc.save()
	