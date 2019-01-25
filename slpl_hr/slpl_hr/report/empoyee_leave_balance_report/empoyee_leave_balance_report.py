from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.leave_application.leave_application \
	import get_leave_allocation_records, get_leave_balance_on
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, add_days, nowdate

from erpnext.hr.utils import set_employee_name, get_leave_period
from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange


def execute(filters=None):
	leave_types = frappe.db.sql_list("select name from `tabLeave Type` order by name asc")
	
	columns = get_columns(leave_types)
	data = get_data(filters, leave_types)
	
	return columns, data
	
def get_columns(leave_types):
	columns = [
		_("Employee") + ":Link/Employee:150", 
		_("Employee Name") + "::200", 
		_("Department") +"::150"
	]

	for leave_type in leave_types:
		columns.append(_(leave_type) + " " + _("Opening") + ":Float:160")
		columns.append(_(leave_type) + " " + _("Taken") + ":Float:160")
		columns.append(_(leave_type) + " " + _("Balance") + ":Float:160")
	
	return columns
	
def get_data(filters, leave_types):
	user = frappe.session.user
	allocation_records_based_on_to_date = get_leave_allocation_records(filters.to_date)
	allocation_records_based_on_from_date = get_leave_allocation_records(filters.from_date)

	active_employees = frappe.get_all("Employee", 
		filters = { "status": "Active", "company": filters.company}, 
		fields = ["name", "employee_name", "department", "user_id"])
	
	data = []
	for employee in active_employees:
		leave_approvers = get_approvers(employee.department)
		if (len(leave_approvers) and user in leave_approvers) or (user in ["Administrator", employee.user_id]) or ("HR Manager" in frappe.get_roles(user)):
			row = [employee.name, employee.employee_name, employee.department]

			for leave_type in leave_types:
				# leaves taken
				leaves_taken = get_approved_leaves_for_period(employee.name, leave_type,
					filters.from_date, filters.to_date)

				# opening balance
				opening = 0
				closing = 0

				conditions = (" and leave_type= '"+str(leave_type)+"' and employee='%s' " % employee.name) if employee else ""

				leave_allocation_records = frappe.db.sql("""select employee, leave_type, total_leaves_allocated, total_leaves_encashed, from_date, to_date from `tabLeave Allocation` where from_date >= %s and to_date <= %s and docstatus=1 {0}""".format(conditions), (filters.from_date, filters.to_date), as_dict=1)
				allocated_leaves = frappe._dict()
				for d in leave_allocation_records:

					opening = d.total_leaves_allocated
					# allocated_leaves.setdefault(d.employee, frappe._dict()).setdefault(d.leave_type, frappe._dict({
					# 	"from_date": d.from_date,
					# 	"to_date": d.to_date,
					# 	"total_leaves_allocated": d.total_leaves_allocated,
					# 	"total_leaves_encashed":d.total_leaves_encashed
					# }))

					# opening = get_leave_balance_on(employee.name, leave_type, filters.from_date,allocation_records_based_on_from_date.get(employee.name, frappe._dict()))

				# closing balance
				closing = float(opening) - float(leaves_taken)
				# closing = get_leave_balance_on(employee.name, leave_type, filters.to_date,
				# 	allocation_records_based_on_to_date.get(employee.name, frappe._dict()))

				row += [opening, leaves_taken, closing]

			data.append(row)
		
	return data

def get_approvers(department):
	if not department:
		return []

	approvers = []
	# get current department and all its child
	department_details = frappe.db.get_value("Department", {"name": department}, ["lft", "rgt"], as_dict=True)
	department_list = frappe.db.sql("""select name from `tabDepartment`
		where lft >= %s and rgt <= %s order by lft desc
		""", (department_details.lft, department_details.rgt), as_list = True)

	# retrieve approvers list from current department and from its subsequent child departments
	for d in department_list:
		approvers.extend([l.leave_approver for l in frappe.db.sql("""select approver from `tabDepartment Approver` \
			where parent = %s and parentfield = 'leave_approvers'""", (d), as_dict=True)])

	return approvers



def get_approved_leaves_for_period(employee, leave_type, from_date, to_date):
	query = """
		select employee, leave_type, from_date, to_date, total_leave_days
		from `tabLeave Application`
		where employee=%(employee)s
			and docstatus='1' and status='Approved'
			and (from_date between %(from_date)s and %(to_date)s
				or to_date between %(from_date)s and %(to_date)s
				or (from_date < %(from_date)s and to_date > %(to_date)s))
	"""
	if leave_type:
		query += "and leave_type=%(leave_type)s"

	leave_applications = frappe.db.sql(query,{
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		"leave_type": leave_type
	}, as_dict=1)

	leave_days = 0
	for leave_app in leave_applications:
		if leave_app.from_date >= getdate(from_date) and leave_app.to_date <= getdate(to_date):
			leave_days += leave_app.total_leave_days
		else:
			if leave_app.from_date < getdate(from_date):
				leave_app.from_date = from_date
			if leave_app.to_date > getdate(to_date):
				leave_app.to_date = to_date

			leave_days += get_number_of_leave_days(employee, leave_type,
				leave_app.from_date, leave_app.to_date)

	return leave_days


@frappe.whitelist()
def get_number_of_leave_days(employee, leave_type, from_date, to_date, half_day = None, half_day_date = None):
	number_of_days = 0
	if cint(half_day) == 1:
		if from_date == to_date:
			number_of_days = 0.5
		else:
			number_of_days = date_diff(to_date, from_date) + .5
	else:
		number_of_days = date_diff(to_date, from_date) + 1

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		number_of_days = flt(number_of_days) - flt(get_holidays(employee, from_date, to_date))
	return number_of_days