# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "slpl_hr"
app_title = "slpl_hr"
app_publisher = "it@scantechlaser.com"
app_description = "slpl_hr"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "it@scantechlaser.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/slpl_hr/css/slpl_hr.css"
# app_include_js = "/assets/slpl_hr/js/slpl_hr.js"

# include js, css files in header of web template
# web_include_css = "/assets/slpl_hr/css/slpl_hr.css"
# web_include_js = "/assets/slpl_hr/js/slpl_hr.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "slpl_hr.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "slpl_hr.install.before_install"
# after_install = "slpl_hr.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "slpl_hr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }


doc_events = {
	
	"Leave Application" : {
		"validate" : "slpl_hr.slpl_hr.slpl_hr_custom.validate_date"
		
	}

}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"slpl_hr.tasks.all"
# 	],
# 	"daily": [
# 		"slpl_hr.tasks.daily"
# 	],
# 	"hourly": [
# 		"slpl_hr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"slpl_hr.tasks.weekly"
# 	]
# 	"monthly": [
# 		"slpl_hr.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "slpl_hr.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "slpl_hr.event.get_events"
# }

