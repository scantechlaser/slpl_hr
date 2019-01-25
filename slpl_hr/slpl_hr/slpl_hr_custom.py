import json
import frappe
import pprint
from frappe import _
from frappe.utils.response import build_response
import requests
import time as t
from datetime import *
import calendar
import re
import sys
import traceback
from datetime import datetime
from math import *
from frappe.auth import LoginManager
import frappe.utils.user
# import mysql.connector as mariadb
# mariadb.connect(user='it@scantechlaser.com', password='Dinudins@123', database='1bd3e0294da19198')
# cursor = mariadb_connection.cursor()
# return cursor
# import MySQLdb
# conn=MySQLdb.connect(host='35.237.255.109',user='root',passwd='laser123')
# cursor = conn.cursor()

def validate_date(doc,method):

	role = frappe.get_roles(frappe.session.user)

	if 'HR Manager' not in role:

		from_date = str(doc.from_date).split("-")
		to_date = str(doc.from_date).split("-")
		posting_date = str(doc.posting_date).split("-")
		if posting_date[1] != to_date[1]:

			frappe.throw(_("You Cannot save Previous date Application, Please contact to HR Department"))
	else:

		frappe.msgprint("Continue")

