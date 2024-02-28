# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Withdraw(Document):
    def validate(self):
         if self.amount > float(frappe.db.get_value('Customer', self.customer, 'custom_balance')):
                    frappe.throw('Insufficient balance in customer account')

    def on_submit(self):
        self.update_customer_balance()
        self.add_withdraw_transaction()
        frappe.msgprint('Withdrawal added successfully')
        
    def update_customer_balance(self):
            balance = float(frappe.db.get_value('Customer', self.customer, 'custom_balance')) - self.amount
            frappe.db.set_value('Customer', self.customer, 'custom_balance', balance)
    
	#add deposit transacion to customer transactions
    def add_withdraw_transaction(self):
         doc = frappe.get_doc('Customer', self.customer)
         doc.append('custom_transactions', {
			'date': self.posting_date,
            'reference': self.name,
			 'transaction_type': 'Withdrawal',
			 'amount': self.amount,
		 })
         doc.save()

         frappe.get_doc({
            'doctype': 'Transactions',
            'date': self.posting_date,
            'transaction_type': 'Withdrawal',
            'amount': self.amount,
            'customer_name': self.customer_name
        }).insert()