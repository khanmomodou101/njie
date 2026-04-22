# Copyright (c) 2025, royalsmb and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt


class DailyRecordSales(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		self.total = 0
		self.total_cash = 0
		self.total_wave = 0
		self.total_aps = 0
		self.total_qmoney = 0
		self.total_expenses = 0

		for row in self.records:
			amt = flt(row.amount)
			self.total += amt

			if row.payment_method == "Cash":
				self.total_cash += amt
			elif row.payment_method == "Wave":
				self.total_wave += amt
			elif row.payment_method == "APS":
				self.total_aps += amt
			elif row.payment_method == "QMoney":
				self.total_qmoney += amt

		for row in self.expenses:
			self.total_expenses += flt(row.amount)

		self.remaining_balance = self.total - self.total_expenses
