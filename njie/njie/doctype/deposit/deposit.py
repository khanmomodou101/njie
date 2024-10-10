# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Deposit(Document):
    def validate(self):
         pass
    def on_submit(self):
        self.update_customer_balance()
        self.add_deposit_transaction()
        frappe.msgprint('Deposit added successfully')
        self.update_balance()

	#update customer balance
    def update_customer_balance(self):
            balance = float(frappe.db.get_value('Customer', self.customer, 'custom_balance')) + self.amount
            frappe.db.set_value('Customer', self.customer, 'custom_balance', balance)
    
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

        #add to transactions
         frappe.get_doc({
            'doctype': 'Transactions',
            'date': self.posting_date,
            'transaction_type': 'Deposit',
            'amount': self.amount,
            'customer_name': self.customer_name
        }).insert()
    def update_balance(self):
        balance = frappe.db.get_value('Customer', self.customer, 'custom_balance')
        frappe.db.set_value('Deposit', self.name, 'balance', balance)
        frappe.db.commit()
        frappe.reload_doctype('Deposit')

    def validate_date(self):
        if self.posting_date > frappe.utils.nowdate():
            frappe.throw('Posting date cannot be in the future')
        if self.posting_date < frappe.utils.nowdate():
            frappe.throw('Posting date cannot be in the past')
