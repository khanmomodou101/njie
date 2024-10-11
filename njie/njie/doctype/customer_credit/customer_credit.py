# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerCredit(Document):
	def validate(self):
		self.get_total_credit()
	def on_submit(self):
		self.add_credit_transaction()
		self.update_credit_balance()
		frappe.msgprint('Credit added successfully')

	def get_total_credit(self):
		total_credit = self.total_amount
		self.total_amount = total_credit

	def add_credit_transaction(self):
		doc = frappe.get_doc('Customer', self.customer)
		doc.append('custom_transactions', {
			'date': self.posting_date,
			'reference': self.name,
			'transaction_type': 'Credit',
			'amount': self.total_amount,
		})
		doc.save()

		frappe.get_doc({
			'doctype': 'Transactions',
			'date': self.posting_date,
			'transaction_type': 'Credit',
			'amount': self.total_amount,
			'customer_name': self.customer_name,
			"branch": doc.custom_branch
		}).insert()
	
	#update customer credit balance
	def update_credit_balance(self):
		balance = float(frappe.db.get_value('Customer', self.customer, 'custom_credit_value')) + self.total_amount
		frappe.db.set_value('Customer', self.customer, 'custom_credit_value', balance)
