// Copyright (c) 2025, royalsmb and contributors
// For license information, please see license.txt

function calculate_totals(frm) {
	let total = 0, total_cash = 0, total_wave = 0, total_aps = 0, total_qmoney = 0, total_expenses = 0;

	(frm.doc.records || []).forEach(row => {
		let amt = flt(row.amount);
		total += amt;
		if (row.payment_method === "Cash") total_cash += amt;
		else if (row.payment_method === "Wave") total_wave += amt;
		else if (row.payment_method === "APS") total_aps += amt;
		else if (row.payment_method === "QMoney") total_qmoney += amt;
	});

	(frm.doc.expenses || []).forEach(row => {
		total_expenses += flt(row.amount);
	});

	frm.set_value("total", total);
	frm.set_value("total_cash", total_cash);
	frm.set_value("total_wave", total_wave);
	frm.set_value("total_aps", total_aps);
	frm.set_value("total_qmoney", total_qmoney);
	frm.set_value("total_expenses", total_expenses);
	frm.set_value("remaining_balance", total - total_expenses);
}

frappe.ui.form.on("Daily Record Sales", {
	refresh(frm) {
		calculate_totals(frm);
	}
});

frappe.ui.form.on("Daily Record Table", {
	amount(frm) { calculate_totals(frm); },
	payment_method(frm) { calculate_totals(frm); },
	records_add(frm) { calculate_totals(frm); },
	records_remove(frm) { calculate_totals(frm); }
});

frappe.ui.form.on("Daily Expenses Table", {
	amount(frm) { calculate_totals(frm); },
	expenses_add(frm) { calculate_totals(frm); },
	expenses_remove(frm) { calculate_totals(frm); }
});
