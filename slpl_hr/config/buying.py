from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Purchasing"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Vendor Payment Advice Setting",
					"description": _("For Vendor Payment Advice Setting"),
				},
				{
					"type": "doctype",
					"name": "Vendor Payment Advice",
					"description": _("Vendor Payment Advice"),
				}
			]
		}
	]
