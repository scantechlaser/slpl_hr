// Copyright (c) 2019, it@scantechlaser.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Log",{
	"attendance_date":function(frm){
		console.log(frm.doc.attendance_date);
		var ymd = frm.doc.attendance_date;
		var yy = ymd.split("-");
		var series = yy[1]+''+yy[2]+''+yy[0];
		frm.set_value("series", series);

	}

});
