# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Leaves and Holiday"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Empoyee Leave Balance Report",
					"doctype": "Empoyee"
				}
			]
		}
	]
