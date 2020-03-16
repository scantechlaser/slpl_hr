# -*- coding: utf-8 -*-
# Copyright (c) 2019, it@scantechlaser.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, cint, getdate, now_datetime, formatdate, strip,time_diff_in_hours
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from frappe.utils import getdate
import calendar
import datetime
import datetime
from datetime import *

class AttendanceLog(Document):
	def validate(self):
		self.employee=str(self.employee_id)[0:1]+'/'+str(self.employee_id)[1:5]+'/'+str(self.employee_id)[5:9]
		self.validate_attendance()
		self.validate_employee()
		self.total_working_hours = diff(self.in_time, self.out_time)
		self.validate_latemark()
		self.validate_time()

	def on_submit(self):

		Event_doc=frappe.new_doc("Attendance")
		Event_doc.naming_series="ATT-"
		Event_doc.employee=self.employee
		Event_doc.employee_name=self.employee_name
		Event_doc.status=self.attendance_mark
		Event_doc.attendance_date=self.attendance_date
		Event_doc.company='Scantech Laser Private Limited'
		Event_doc.department=self.department
		Event_doc.attendance_log=self.name
		Event_doc.flags.ignore_mandatory = True
		Event_doc.submit()

	def on_cancel(self):
		get_attendance = frappe.db.sql("SELECT name FROM `tabAttendance` WHERE attendance_log='"+str(self.name)+"' ", as_dict=True)
		doc = frappe.get_doc('Attendance', get_attendance[0].name)
		doc.cancel()

	def validate_attendance(self):
		
		get_attendance = frappe.db.sql("SELECT * FROM `tabAttendance Log` WHERE employee='"+str(self.employee)+"' and attendance_date='"+str(self.attendance_date)+"' and docstatus !=2 and name!='"+str(self.name)+"' ")
		if get_attendance:

			frappe.throw(_("Attendance Already Mark"))

	def validate_employee(self):
		self.department = frappe.db.get_value('Employee', self.employee, 'department')
		self.designation = frappe.db.get_value('Employee', self.employee, 'designation')
		self.employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')

	def validate_latemark(self):
		data = self.get_global()
		late_balance = check_late_balance(self.attendance_date,self.employee, data.max_late_in, self.name)		
		if self.in_time:
			if  time_compare(self.in_time, data.grace_in_time) and time_compare(data.max_late_in_time,self.in_time) and late_balance <= data.max_late_in:
				# frappe.msgprint("late"+str(late_balance))
				# frappe.msgprint(900)
				self.late_mark_balance = late_balance
				

	def validate_time(self):

		data = self.get_global()

		if self.in_time and self.out_time:
			late_balance = check_late_balance(self.attendance_date,self.employee, data.max_late_in, self.name)

			if self.late_mark_balance>0 and time_compare(data.max_late_in_time,self.in_time):


				if time_compare(data.grace_in_time, self.in_time):
					late_balance = check_late_balance(self.attendance_date,self.employee, data.max_late_in, self.name)
					self.late_mark_balance = late_balance
					

				if time_compare(self.in_time , data.grace_in_time) and time_compare(data.max_late_in_time, self.in_time):
					late_balance = check_late_balance(self.attendance_date,self.employee, data.max_late_in, self.name)
					self.late_mark_balance = late_balance - 1
				if time_compare(self.out_time,data.out_time):

					self.attendance_mark = 'Present'
					

				if time_compare(data.out_time,self.out_time):
					self.attendance_mark = 'Half Day'

				if time_compare(data.first_half_end,self.out_time):
					late_balance = check_late_balance(self.attendance_date,self.employee, data.max_late_in, self.name)
					self.late_mark_balance = late_balance
					
					self.attendance_mark = 'Absent'

				if check_ealry_leave_balance(self.attendance_date,self.employee,data.max_late_in, self.name)>0 and time_compare(data.max_late_in_time,self.in_time):
					self.attendance_mark = 'Present'
					
			else:

				if time_compare(self.in_time, data.grace_in_time):

					if time_compare(data.max_late_in_time, self.in_time) and time_compare(self.total_working_hours, data.min_working_hours):

						self.adjust_balance = check_adjustable_balance(self.attendance_date,self.employee, data.max_late_in, self.name, self.total_working_hours)
						if self.adjust_balance>0:
							self.attendance_mark='Present'
						else:
							self.attendance_mark='Half Day'
					else:
						self.late_mark_balance = check_late_balance(self.attendance_date,self.employee,data.max_late_in, self.name)
						self.attendance_mark='Half Day'

				if time_compare(data.out_time, self.out_time):
					self.late_mark_balance = check_late_balance(self.attendance_date,self.employee,data.max_late_in, self.name)
					self.attendance_mark = 'Absent'
				if time_compare(data.grace_in_time, self.in_time) and time_compare(self.out_time, data.out_time):
					self.attendance_mark = 'Present'

				if check_ealry_leave_balance(self.attendance_date,self.employee,data.max_late_in, self.name)>0 and time_compare(data.max_late_in_time,self.in_time) and time_compare(data.out_time, self.out_time) and time_compare(self.out_time, data.early_leave_time) :
					self.attendance_mark = 'Present'



	def get_global(self):
		# doc = frappe.get_doc("Attendance Setting", 'Attendance Setting')
		doc = frappe.get_single('Attendance Setting')
		return doc

@frappe.whitelist(allow_guest=True)
def diff(t_a = '10:00', t_b = '15:00'):
	in_time = str(t_a).split(':')
	out_time = str(t_b).split(':')
	t1 = timedelta(hours=int(in_time[0]), minutes=int(in_time[1]))
	t2 = timedelta(hours=int(out_time[0]), minutes=int(out_time[1]))

	arrival = t2 - t1
	return arrival

@frappe.whitelist(allow_guest=True)
def time_compare(t_a='00:00', t_b='12:00'):
	in_time = str(t_a).split(':')
	out_time = str(t_b).split(':')
	t1 = timedelta(hours=int(in_time[0]), minutes=int(in_time[1]))
	t2 = timedelta(hours=int(out_time[0]), minutes=int(out_time[1]))
	if t1>t2:
		return True
	else:
		return False


@frappe.whitelist()
def check_late_balance(attendance_date='', employee='', max_latemark=0, name=''):
	count = 0
	doc = frappe.get_single('Attendance Setting')
	data = eomday(int(str(attendance_date).split('-')[0]),int(str(attendance_date).split('-')[1]))
	start_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+'1'
	end_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+str(data)
	mysql="SELECT * FROM `tabAttendance Log` WHERE attendance_date>='"+str(start_date)+"' and attendance_date <='"+str(end_date)+"' and employee = '"+str(employee)+"' and docstatus!=2 "
	frappe.msgprint(mysql)
	getLog = frappe.db.sql(mysql, as_dict=True)
	if getLog:
		for i in getLog:

			if time_compare(doc.max_late_in_time, i.in_time) and time_compare(i.in_time, doc.grace_in_time):
				if i.name!=name:
					count+=1
		# frappe.msgprint(count)		
		count = max_latemark - count
		# frappe.msgprint(str(count)+'-'+'1234')
		if count<0:
			count =0

		return count
	return max_latemark

@frappe.whitelist()
def check_adjustable_balance(attendance_date='', employee='', max_latemark=0, name='', total_working_hours='00:00'):
	count = 0
	doc = frappe.get_single('Attendance Setting')
	data = eomday(int(str(attendance_date).split('-')[0]),int(str(attendance_date).split('-')[1]))
	start_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+'1'
	end_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+str(data)
	mysql="SELECT * FROM `tabAttendance Log` WHERE attendance_date>='"+str(start_date)+"' and attendance_date <='"+str(end_date)+"' and employee = '"+str(employee)+"' and docstatus!=2 "
	getLog = frappe.db.sql(mysql, as_dict=True)
	if getLog:
		for i in getLog:
			if time_compare(doc.max_late_in_time, i.in_time) and time_compare(i.in_time, doc.grace_in_time):

				if i.name!=name and time_compare(total_working_hours, doc.min_working_hours) and i.late_mark_balance==0:
					count+=1

		# frappe.msgprint(count)		
		count = max_latemark - count
		# frappe.msgprint(str(count)+'-'+'1234')
		if count<0:
			count =0

		return count
	return max_latemark

@frappe.whitelist()
def check_ealry_leave_balance(attendance_date='', employee='', max_latemark=0, name=''):
	count = 0
	doc = frappe.get_single('Attendance Setting')
	data = eomday(int(str(attendance_date).split('-')[0]),int(str(attendance_date).split('-')[1]))
	start_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+'1'
	end_date = str(str(attendance_date).split('-')[0])+'-'+str(str(attendance_date).split('-')[1])+'-'+str(data)
	mysql="SELECT * FROM `tabAttendance Log` WHERE attendance_date>='"+str(start_date)+"' and attendance_date <='"+str(end_date)+"' and employee = '"+str(employee)+"' and docstatus!=2 "
	getLog = frappe.db.sql(mysql, as_dict=True)
	if getLog:
		for i in getLog:
			if time_compare(i.out_time, doc.early_leave_time) and time_compare(doc.out_time,i.out_time) and i.name != name:
				count+=1
				break
		# frappe.msgprint(count)		
		count = max_latemark - count
		# frappe.msgprint(str(count)+'-'+'1234')
		if count<0:
			count =0

		return count
	return max_latemark

def eomday(year, month):
	
	"""returns the number of days in a given month"""
	days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	d = days_per_month[month - 1]
	if month == 2 and (year % 4 == 0 and year % 100 != 0 or year % 400 == 0):
		d = 29
	return d