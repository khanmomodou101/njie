import frappe
from frappe.model.document import Document

def autoname(doc, method=None):
    doc.name = doc.phone_number