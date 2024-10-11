# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CreditPayment(Document):
	def validate(self):
		if self.amount > self.credit_value:
			frappe.throw('Insufficient credit balance in customer account')
	
	def on_submit(self):
		self.update_customer_credit_balance()
		self.add_credit_payment_transaction()
		frappe.msgprint('Credit Payment added successfully')

	def update_customer_credit_balance(self):
		balance = float(frappe.db.get_value('Customer', self.customer, 'custom_credit_value')) - self.amount
		frappe.db.set_value('Customer', self.customer, 'custom_credit_value', balance)

	def add_credit_payment_transaction(self):
		doc = frappe.get_doc('Customer', self.customer)
		doc.append('custom_transactions', {
			'date': self.posting_date,
			'reference': self.name,
			'transaction_type': 'Credit Payment',
			'amount': self.amount,
		})
		doc.save()

		frappe.get_doc({
			'doctype': 'Transactions',
			'date': self.posting_date,
			'transaction_type': 'Credit Payment',
			'amount': self.amount,
			'customer_name': self.customer_name,
			"branch": doc.custom_branch
		}).insert()