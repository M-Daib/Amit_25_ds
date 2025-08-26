# UI.py
import sys, json, uuid, csv, os
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QLabel, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QPlainTextEdit, QPushButton, QMessageBox, QTabWidget, QCheckBox,
    QInputDialog, QDialog, QDialogButtonBox, QFileDialog, QComboBox,
    QDateTimeEdit, QDateEdit, QToolBar, QStyle, QMenu, QAbstractItemView,
    QTableView, QHeaderView, QStatusBar, QRadioButton, QGridLayout
)
from PySide6.QtCore import (
    Qt, QDateTime, QDate, QObject, Signal, QSettings, QAbstractTableModel,
    QModelIndex, QSortFilterProxyModel, QByteArray, QMimeData, QLocale, QTimer, QUrl
)
from PySide6.QtGui import (
    QFont, QPalette, QColor, QBrush, QAction, QShortcut, QKeySequence, QIcon, QTextDocument, QDesktopServices
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# Charts (optional)
try:
    from PySide6.QtCharts import (
        QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    )
    HAS_QTCHARTS = True
except Exception:
    HAS_QTCHARTS = False

# Domain
from hospital import Hospital
from department import Department
from patient import Patient
from staff import Staff


APP_VERSION = "1.1.0"


# ================= I18N =================
class I18nManager(QObject):
    language_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("HospitalApp", "UI")
        self.lang = self.settings.value("language", "ar")
        self.strings: Dict[str, Dict[str, str]] = {
            # App / Menu
            "app.title": {"ar": "إدارة المستشفى - {name}", "en": "Hospital Management - {name}"},
            "menu.file": {"ar": "ملف", "en": "File"},
            "menu.file.new": {"ar": "جديد", "en": "New"},
            "menu.file.open": {"ar": "فتح...", "en": "Open..."},
            "menu.file.save": {"ar": "حفظ", "en": "Save"},
            "menu.file.saveas": {"ar": "حفظ باسم...", "en": "Save As..."},
            "menu.file.export": {"ar": "تصدير", "en": "Export"},
            "menu.file.export.patients_current": {"ar": "المرضى (القسم الحالي) CSV", "en": "Patients (current department) CSV"},
            "menu.file.export.patients_all": {"ar": "المرضى (كل الأقسام) CSV", "en": "Patients (all departments) CSV"},
            "menu.file.export.staff_current": {"ar": "الطاقم (القسم الحالي) CSV", "en": "Staff (current department) CSV"},
            "menu.file.export.staff_all": {"ar": "الطاقم (كل الأقسام) CSV", "en": "Staff (all departments) CSV"},
            "menu.file.export.appts_filtered": {"ar": "المواعيد (حسب التصفية) CSV", "en": "Appointments (filtered) CSV"},
            "menu.help": {"ar": "مساعدة", "en": "Help"},
            "menu.help.about": {"ar": "حول التطبيق", "en": "About"},

            "menu.language": {"ar": "اللغة", "en": "Language"},
            "menu.language.ar": {"ar": "العربية", "en": "Arabic"},
            "menu.language.en": {"ar": "الإنجليزية", "en": "English"},
            "menu.theme": {"ar": "المظهر", "en": "Theme"},
            "menu.theme.light": {"ar": "فاتح", "en": "Light"},
            "menu.theme.dark": {"ar": "داكن", "en": "Dark"},
            "filter.all": {"ar": "الكل", "en": "All"},

            # Toolbar
            "toolbar.save": {"ar": "حفظ", "en": "Save"},
            "toolbar.add_patient": {"ar": "مريض جديد", "en": "Add Patient"},
            "toolbar.add_appt": {"ar": "موعد جديد", "en": "Add Appointment"},
            "toolbar.refresh": {"ar": "تحديث", "en": "Refresh"},
            "toolbar.search.ph": {"ar": "ابحث (اسم/ID)...", "en": "Search (name/ID)..."},

            # Tabs
            "tab.dashboard": {"ar": "لوحة المعلومات", "en": "Dashboard"},
            "tab.patients": {"ar": "المرضى", "en": "Patients"},
            "tab.staff": {"ar": "الطاقم", "en": "Staff"},
            "tab.search": {"ar": "بحث", "en": "Search"},
            "tab.appointments": {"ar": "المواعيد", "en": "Appointments"},

            # Left panel (Departments)
            "label.departments": {"ar": "الأقسام", "en": "Departments"},
            "group.add_dept": {"ar": "إضافة قسم", "en": "Add Department"},
            "field.name": {"ar": "الاسم", "en": "Name"},
            "field.capacity": {"ar": "السعة", "en": "Capacity"},
            "btn.add": {"ar": "إضافة", "en": "Add"},

            # Info panel
            "group.dept_info": {"ar": "معلومات القسم", "en": "Department Info"},
            "label.name:": {"ar": "الاسم:", "en": "Name:"},
            "label.code:": {"ar": "الكود:", "en": "Code:"},
            "label.capacity:": {"ar": "السعة:", "en": "Capacity:"},
            "label.patients_count:": {"ar": "عدد المرضى:", "en": "Patients:"},
            "label.staff_count:": {"ar": "عدد الطاقم:", "en": "Staff:"},
            "unit.years": {"ar": "سنة", "en": "yr"},

            # Patients/Staff forms
            "group.add_patient": {"ar": "إضافة بيانات المريض", "en": "Add patient info"},
            "field.age": {"ar": "العمر", "en": "Age"},
            "field.medical_record": {"ar": "السجل الطبي", "en": "Medical Record"},
            "btn.add_patient": {"ar": "إضافة مريض", "en": "Add Patient"},
            "group.add_staff": {"ar": "إضافة موظف", "en": "Add Staff"},
            "field.position": {"ar": "المنصب", "en": "Position"},
            "btn.add_staff": {"ar": "إضافة موظف", "en": "Add Staff"},
            "ph.medical_record": {"ar": "اكتب الملاحظات الطبية...", "en": "Enter medical notes..."},
            "ph.position_hint": {"ar": "مثل: طبيب قلب، ممرضة، فني", "en": "e.g., Cardiologist, Nurse, Technician"},
            "ph.patient_name": {"ar": "أدخل الاسم الكامل", "en": "Enter full name"},
            "ph.staff_name": {"ar": "أدخل الاسم الكامل", "en": "Enter full name"},
            "ph.dept_name": {"ar": "اسم القسم...", "en": "Department name..."},
            "ph.appt_notes": {"ar": "ملاحظات (اختياري)...", "en": "Notes (optional)..."},

            # Patient details dialog
            "dialog.patient_details.title": {"ar": "تفاصيل المريض - {id}", "en": "Patient details - {id}"},
            "label.patient_id:": {"ar": "رقم المريض:", "en": "Patient ID:"},
            "label.state:": {"ar": "الحالة:", "en": "Status:"},
            "label.admission_date:": {"ar": "تاريخ الدخول:", "en": "Admission date:"},
            "label.discharge_date:": {"ar": "تاريخ الخروج:", "en": "Discharge date:"},
            "btn.discharge": {"ar": "إخراج", "en": "Discharge"},
            "btn.save": {"ar": "حفظ", "en": "Save"},
            "btn.close": {"ar": "إغلاق", "en": "Close"},
            "btn.print": {"ar": "طباعة", "en": "Print"},
            "btn.export_pdf": {"ar": "تصدير PDF", "en": "Export PDF"},
            "btn.discharge_selected": {"ar": "إخراج المحددين", "en": "Discharge selected"},
            "chk.only_active": {"ar": "النشطون", "en": "Active"},
            "btn.refresh": {"ar": "تحديث", "en": "Refresh"},

            # Patients columns/ctx
            "col.pat.pid": {"ar": "Patient ID", "en": "Patient ID"},
            "col.pat.name": {"ar": "الاسم", "en": "Name"},
            "col.pat.age": {"ar": "السن", "en": "Age"},
            "col.pat.status": {"ar": "الحالة", "en": "Status"},
            "col.pat.adm": {"ar": "الدخول", "en": "Admission"},
            "status.admitted": {"ar": "مقيم", "en": "Admitted"},
            "status.discharged": {"ar": "مخروج", "en": "Discharged"},
            "ctx.p.details": {"ar": "تفاصيل", "en": "Details"},
            "ctx.p.discharge": {"ar": "خروج", "en": "Discharge"},
            "ctx.p.move": {"ar": "نقل إلى قسم...", "en": "Move to department..."},
            "ctx.p.copyid": {"ar": "نسخ Patient ID", "en": "Copy Patient ID"},
            "ctx.p.discharge_sel": {"ar": "خروج المحددين", "en": "Discharge selected"},
            "ctx.p.move_sel": {"ar": "نقل المحددين إلى قسم...", "en": "Move selected to department..."},
            "ctx.p.print": {"ar": "طباعة السجل", "en": "Print record"},
            "ctx.p.export_pdf": {"ar": "تصدير السجل PDF", "en": "Export record PDF"},

            # Staff columns/ctx
            "col.stf.sid": {"ar": "Staff ID", "en": "Staff ID"},
            "col.stf.name": {"ar": "الاسم", "en": "Name"},
            "col.stf.pos": {"ar": "المنصب", "en": "Position"},
            "col.stf.status": {"ar": "الحالة", "en": "Status"},
            "col.stf.age": {"ar": "السن", "en": "Age"},
            "ctx.s.toggle": {"ar": "تبديل تفعيل", "en": "Toggle active"},
            "ctx.s.copyid": {"ar": "نسخ Staff ID", "en": "Copy Staff ID"},
            "staff.active": {"ar": "نشط", "en": "Active"},
            "staff.inactive": {"ar": "موقّف", "en": "Inactive"},

            # Search tab
            "group.search": {"ar": "بحث متقدم", "en": "Advanced search"},
            "search.field.label": {"ar": "كلمة البحث", "en": "Search term"},
            "ph.search_all": {"ar": "اكتب اسم أو ID ...", "en": "Type a name or ID ..."},
            "search.mode.patients": {"ar": "مرضى", "en": "Patients"},
            "search.mode.staff": {"ar": "طاقم", "en": "Staff"},
            "filter.pat_status": {"ar": "حالة المريض", "en": "Patient status"},
            "filter.staff_status": {"ar": "حالة الموظف", "en": "Staff status"},
            "filter.age_min": {"ar": "العمر الأدنى", "en": "Min age"},
            "filter.age_max": {"ar": "العمر الأقصى", "en": "Max age"},
            "label.results_count": {"ar": "النتائج: {n}", "en": "Results: {n}"},

            # Appointments tab
            "group.create_appt": {"ar": "إنشاء موعد", "en": "Create appointment"},
            "field.dept": {"ar": "القسم", "en": "Department"},
            "field.patient": {"ar": "المريض", "en": "Patient"},
            "field.staff": {"ar": "الموظف", "en": "Staff"},
            "field.start": {"ar": "بداية", "en": "Start"},
            "field.end": {"ar": "نهاية", "en": "End"},
            "field.notes": {"ar": "ملاحظات", "en": "Notes"},
            "btn.add_appt": {"ar": "إضافة موعد", "en": "Add appointment"},
            "group.appt_list": {"ar": "قائمة المواعيد", "en": "Appointments List"},
            "filter.date": {"ar": "التاريخ:", "en": "Date:"},
            "filter.dept": {"ar": "القسم:", "en": "Department:"},
            "filter.status": {"ar": "الحالة:", "en": "Status:"},

            "col.ap.id": {"ar": "#", "en": "#"},
            "col.ap.dept": {"ar": "القسم", "en": "Department"},
            "col.ap.patient": {"ar": "المريض", "en": "Patient"},
            "col.ap.staff": {"ar": "الموظف", "en": "Staff"},
            "col.ap.start": {"ar": "بداية", "en": "Start"},
            "col.ap.end": {"ar": "نهاية", "en": "End"},
            "col.ap.status": {"ar": "الحالة", "en": "Status"},
            "col.ap.notes": {"ar": "ملاحظات", "en": "Notes"},
            "col.ap.conflict": {"ar": "تعارض", "en": "Conflict"},

            "btn.change_status": {"ar": "تغيير حالة الموعد", "en": "Change appointment status"},
            "btn.delete_appt": {"ar": "حذف الموعد المحدد", "en": "Delete selected appointment"},

            "appt.status.scheduled": {"ar": "مجدول", "en": "Scheduled"},
            "appt.status.checked_in": {"ar": "حضر", "en": "Checked-in"},
            "appt.status.completed": {"ar": "مكتمل", "en": "Completed"},
            "appt.status.cancelled": {"ar": "ملغي", "en": "Cancelled"},

            # Dashboard
            "dash.stats": {"ar": "إحصائيات", "en": "Statistics"},
            "dash.total_depts": {"ar": "عدد الأقسام", "en": "Departments"},
            "dash.total_patients": {"ar": "إجمالي المرضى", "en": "Total patients"},
            "dash.active_patients": {"ar": "مرضى مقيمون", "en": "Active (admitted)"},
            "dash.total_staff": {"ar": "عدد الطاقم", "en": "Staff"},
            "dash.appts_today": {"ar": "مواعيد اليوم", "en": "Appointments today"},
            "dash.refresh": {"ar": "تحديث", "en": "Refresh"},
            "dash.chart.appts_by_status": {"ar": "مواعيد اليوم حسب الحالة", "en": "Today's appointments by status"},
            "dash.no_qtcharts": {"ar": "QtCharts غير متاحة - لا يمكن عرض الرسم", "en": "QtCharts not available - cannot display chart"},

            # Messages (titles)
            "msg.info.title": {"ar": "تم", "en": "Info"},
            "msg.warning.title": {"ar": "تنبيه", "en": "Warning"},
            "msg.error.title": {"ar": "خطأ", "en": "Error"},
            "msg.confirm.title": {"ar": "تأكيد", "en": "Confirm"},
            "msg.about.title": {"ar": "حول التطبيق", "en": "About"},

            # Messages (content)
            "msg.new.confirm": {"ar": "بدء ملف جديد؟ قد تفقد تغييرات غير محفوظة.", "en": "Start new file? Unsaved changes may be lost."},
            "dialog.open.title": {"ar": "فتح ملف بيانات", "en": "Open data file"},
            "dialog.save.title": {"ar": "حفظ الملف", "en": "Save file"},
            "dialog.export.csv.title": {"ar": "تصدير CSV", "en": "Export CSV"},
            "dialog.export.pdf.title": {"ar": "تصدير PDF", "en": "Export PDF"},
            "dialog.json.filter": {"ar": "JSON (*.json)", "en": "JSON (*.json)"},
            "dialog.csv.filter": {"ar": "CSV (*.csv)", "en": "CSV (*.csv)"},
            "dialog.pdf.filter": {"ar": "PDF (*.pdf)", "en": "PDF (*.pdf)"},
            "msg.loaded_ok": {"ar": "تم تحميل البيانات بنجاح", "en": "Data loaded successfully"},
            "msg.open.fail": {"ar": "فشل التحميل:\n{err}", "en": "Failed to load:\n{err}"},
            "msg.save.ok": {"ar": "تم الحفظ", "en": "Saved"},
            "msg.save.fail": {"ar": "فشل الحفظ:\n{err}", "en": "Failed to save:\n{err}"},
            "msg.export.ok": {"ar": "تم التصدير", "en": "Exported"},
            "msg.export.fail": {"ar": "فشل التصدير:\n{err}", "en": "Failed to export:\n{err}"},

            "msg.select_department_first": {"ar": "اختار قسم أولًا", "en": "Select a department first"},
            "msg.patient.name_required": {"ar": "اسم المريض مطلوب", "en": "Patient name is required"},
            "msg.dept.name_required": {"ar": "اسم القسم مطلوب", "en": "Department name is required"},
            "msg.validation.fix_fields": {"ar": "يرجى تصحيح الحقول المظللة", "en": "Please fix the highlighted fields"},
            "msg.dept.full": {"ar": "لا يمكن إدخال {name}، القسم ممتلئ", "en": "Cannot admit {name}, department is full"},
            "msg.patient.added": {"ar": "تم إدخال المريض: {pid}", "en": "Patient admitted: {pid}"},
            "msg.select_patient": {"ar": "اختار مريض من القائمة", "en": "Select a patient from the list"},
            "msg.patient.already_discharged": {"ar": "المريض مخروج بالفعل", "en": "Patient already discharged"},
            "dialog.discharge.notes_title": {"ar": "ملاحظات الخروج", "en": "Discharge notes"},
            "dialog.discharge.notes_prompt": {"ar": "أدخل ملاحظات الخروج (اختياري):", "en": "Enter discharge notes (optional):"},
            "msg.patient.discharged": {"ar": "تم خروج المريض {name}", "en": "Patient {name} discharged"},

            "msg.no_other_departments": {"ar": "لا يوجد أقسام أخرى", "en": "No other departments available"},
            "dialog.move_patient.title": {"ar": "نقل مريض", "en": "Move patient"},
            "dialog.move_patient.prompt": {"ar": "اختر القسم الهدف:", "en": "Select target department:"},
            "msg.dept.full_with_name": {"ar": "القسم {name} ممتلئ", "en": "Department {name} is full"},
            "msg.patient.moved_to": {"ar": "تم نقل {pname} إلى {dname}", "en": "{pname} moved to {dname}"},

            "msg.staff.name_position_required": {"ar": "الاسم والمنصب مطلوبان", "en": "Name and position are required"},
            "msg.staff.added": {"ar": "تمت إضافة الموظف: {sid}", "en": "Staff added: {sid}"},

            "msg.select_dept": {"ar": "اختر قسم", "en": "Select department"},
            "msg.select_patient_for_appt": {"ar": "اختر مريض", "en": "Select a patient"},
            "msg.end_after_start": {"ar": "وقت النهاية يجب أن يكون بعد البداية", "en": "End time must be after start"},
            "msg.appt.created": {"ar": "تم إنشاء الموعد #{id}", "en": "Appointment #{id} created"},
            "msg.select_appt": {"ar": "اختر موعدًا من الجدول", "en": "Select an appointment from the table"},
            "dialog.change_status.title": {"ar": "تغيير الحالة", "en": "Change status"},
            "dialog.change_status.prompt": {"ar": "اختر الحالة:", "en": "Pick a status:"},
            "dialog.delete_appt.confirm": {"ar": "حذف الموعد #{id}؟", "en": "Delete appointment #{id}?"},
            "msg.appt.conflict.title": {"ar": "تعارض مواعيد", "en": "Appointment conflict"},
            "msg.appt.conflict.body": {"ar": "يوجد تعارض مع المواعيد:\n{details}", "en": "Conflicts with existing appointments:\n{details}"},
            "msg.appt.conflict.row": {"ar": "- #{id} | {dept} | {start}-{end} | {who}", "en": "- #{id} | {dept} | {start}-{end} | {who}"},
            "who.patient": {"ar": "نفس المريض", "en": "same patient"},
            "who.staff": {"ar": "نفس الموظف", "en": "same staff"},

            # Confirmations
            "confirm.discharge.title": {"ar": "تأكيد الخروج", "en": "Confirm discharge"},
            "confirm.discharge.body": {"ar": "هل تريد إخراج {n} مريض(ة)؟", "en": "Discharge {n} patient(s)?"},
            "confirm.delete_appt.title": {"ar": "تأكيد الحذف", "en": "Confirm delete"},
            "confirm.delete_appt.body": {"ar": "حذف {n} موعد(ًا)؟", "en": "Delete {n} appointment(s)?"},
            "chk.dont_ask_again": {"ar": "لا تسألني مرة أخرى", "en": "Don't ask again"},

            # About
            "about.body": {
                "ar": "<b>إدارة المستشفى</b><br/>الإصدار {ver}<br/><br/>مشروع تعليمي يعتمد على PySide6.<br/>المصدر: <a href='https://qt.io'>Qt</a>",
                "en": "<b>Hospital Management</b><br/>Version {ver}<br/><br/>A learning project built with PySide6.<br/>Powered by <a href='https://qt.io'>Qt</a>"
            },

            # Empty states
            "empty.no_dept": {"ar": "اختر قسمًا للبدء", "en": "Select a department to begin"},
            "empty.patients": {"ar": "لا يوجد مرضى في هذا القسم", "en": "No patients in this department"},
            "empty.staff": {"ar": "لا يوجد طاقم في هذا القسم", "en": "No staff in this department"},
            "empty.appts": {"ar": "لا توجد مواعيد مطابقة للتصفية", "en": "No appointments match your filters"},
        }

    def t(self, key: str, **kwargs) -> str:
        data = self.strings.get(key, {})
        text = data.get(self.lang) or data.get("en") or key
        return text.format(**kwargs)

    def set_language(self, lang: str):
        if lang not in ("ar", "en"): return
        if lang == self.lang: return
        self.lang = lang
        self.settings.setValue("language", lang)
        self.language_changed.emit(lang)


I18N = I18nManager()


# ================= Theme Manager (Dark/Light) =================
DARK_QSS = """
QWidget { background-color: #121212; color: #eaeaea; }
QMenuBar, QMenu { background-color: #1b1b1b; color: #eaeaea; }
QMenu { border: 1px solid #2d2d2d; }
QMenu::item:selected { background-color: #2c2c2c; }
QStatusBar { background: #121212; color: #bbbbbb; }
QToolTip { color: #000; background: #ffffdd; border: 1px solid #bfbf7f; }
QGroupBox { border: 1px solid #2a2a2a; border-radius: 6px; margin-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top right; padding: 3px 8px; }
QLineEdit, QPlainTextEdit, QSpinBox, QDateTimeEdit, QDateEdit, QComboBox {
    background-color: #1e1e1e; border: 1px solid #3a3a3a; padding: 6px 8px; border-radius: 4px; color: #eaeaea;
}
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDateTimeEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid #4a90e2;
}
QPushButton { background-color: #2b2b2b; border: 1px solid #3a3a3a; padding: 7px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #343434; }
QPushButton:pressed { background-color: #3c3c3c; }
QTableView { gridline-color: #333; alternate-background-color: #161616; }
QHeaderView::section { background: #1f1f1f; color: #ddd; border: 1px solid #3a3a3a; padding: 6px; }
QTabBar::tab { background: #1e1e1e; padding: 8px 14px; border: 1px solid #3a3a3a; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-left: 2px; }
QTabBar::tab:selected { background: #2a2a2a; }
"""

LIGHT_QSS = """
QWidget { background-color: #ffffff; color: #111; }
QMenuBar, QMenu { background-color: #ffffff; color: #111; }
QMenu { border: 1px solid #cfcfcf; }
QMenu::item:selected { background-color: #e6f0ff; color: #111; }
QStatusBar { background: #ffffff; color: #666; }
QToolTip { color: #111; background: #ffffdd; border: 1px solid #bfbf7f; }
QGroupBox { border: 1px solid #e0e0e0; border-radius: 6px; margin-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top right; padding: 3px 8px; }
QLineEdit, QPlainTextEdit, QSpinBox, QDateTimeEdit, QDateEdit, QComboBox {
    background-color: #ffffff; border: 1px solid #cfcfcf; padding: 6px 8px; border-radius: 4px; color: #111;
}
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDateTimeEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid #4a90e2;
}
QPushButton { background-color: #f6f6f6; border: 1px solid #cfcfcf; padding: 7px 12px; border-radius: 4px; color: #111; }
QPushButton:hover { background-color: #efefef; }
QPushButton:pressed { background-color: #e8e8e8; }
QTableView { gridline-color: #ddd; alternate-background-color: #fafafa; }
QHeaderView::section { background: #f4f4f4; color: #222; border: 1px solid #e0e0e0; padding: 6px; }
QTabBar::tab { background: #f7f7f7; padding: 8px 14px; border: 1px solid #e0e0e0; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-left: 2px; }
QTabBar::tab:selected { background: #ffffff; }
"""

def make_dark_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(18,18,18))
    p.setColor(QPalette.WindowText, QColor(234,234,234))
    p.setColor(QPalette.Base, QColor(30,30,30))
    p.setColor(QPalette.AlternateBase, QColor(25,25,25))
    p.setColor(QPalette.ToolTipBase, QColor(255,255,220))
    p.setColor(QPalette.ToolTipText, QColor(0,0,0))
    p.setColor(QPalette.Text, QColor(230,230,230))
    p.setColor(QPalette.Button, QColor(43,43,43))
    p.setColor(QPalette.ButtonText, QColor(230,230,230))
    p.setColor(QPalette.Link, QColor(42,130,218))
    p.setColor(QPalette.Highlight, QColor(56,120,217))
    p.setColor(QPalette.HighlightedText, QColor(0,0,0))
    return p

def make_light_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor("#ffffff"))
    p.setColor(QPalette.WindowText, QColor("#111111"))
    p.setColor(QPalette.Base, QColor("#ffffff"))
    p.setColor(QPalette.AlternateBase, QColor("#fafafa"))
    p.setColor(QPalette.ToolTipBase, QColor("#ffffdd"))
    p.setColor(QPalette.ToolTipText, QColor("#111111"))
    p.setColor(QPalette.Text, QColor("#111111"))
    p.setColor(QPalette.Button, QColor("#f6f6f6"))
    p.setColor(QPalette.ButtonText, QColor("#111111"))
    p.setColor(QPalette.Link, QColor("#2a82da"))
    p.setColor(QPalette.Highlight, QColor("#cde2ff"))
    p.setColor(QPalette.HighlightedText, QColor("#111111"))
    return p

class ThemeManager(QObject):
    theme_changed = Signal(str)
    def __init__(self):
        super().__init__()
        self.settings = QSettings("HospitalApp", "UI")
        self.theme = self.settings.value("theme", "light")
    def set_theme(self, theme: str):
        theme = "dark" if str(theme).lower().startswith("d") else "light"
        if theme == self.theme: return
        self.theme = theme
        self.settings.setValue("theme", self.theme)
        self.apply(QApplication.instance())
        self.theme_changed.emit(theme)
    def apply(self, app: QApplication | None):
        if not app: return
        if self.theme == "dark":
            app.setPalette(make_dark_palette())
            app.setStyleSheet(DARK_QSS)
        else:
            app.setPalette(make_light_palette())
            app.setStyleSheet(LIGHT_QSS)

THEME = ThemeManager()


# ================= Helpers: Date/Time JSON =================
def dt_to_str(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat(timespec="seconds") if dt else None

def dt_from_str(s: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(s) if s else None

def fmt_dt(dt: Optional[datetime], time_only: bool = False) -> str:
    if not dt:
        return "-"
    qdt = QDateTime.fromSecsSinceEpoch(int(dt.timestamp()))
    loc = QLocale()
    if time_only:
        return loc.toString(qdt.time(), QLocale.ShortFormat)
    return loc.toString(qdt, QLocale.ShortFormat)


# ================= JSON Serializer =================
def hospital_to_dict(h: Hospital) -> dict:
    return {
        "name": h.name,
        "location": h.location,
        "departments": [
            {
                "name": d.name,
                "capacity": d.capacity,
                "patients": [
                    {
                        "id": p.id,
                        "patient_id": p.patient_id,
                        "name": p.name,
                        "age": p.age,
                        "created_at": dt_to_str(getattr(p, "created_at", None)),
                        "medical_record": p.medical_record,
                        "admission_date": dt_to_str(getattr(p, "admission_date", None)),
                        "is_discharged": p.is_discharged,
                        "discharge_date": dt_to_str(getattr(p, "discharge_date", None)),
                    } for p in d.patients
                ],
                "staff": [
                    {
                        "id": s.id,
                        "staff_id": s.staff_id,
                        "name": s.name,
                        "age": s.age,
                        "position": s.position,
                        "department": s.department,
                        "is_active": s.is_active,
                        "created_at": dt_to_str(getattr(s, "created_at", None)),
                    } for s in d.staff
                ],
            } for d in h.departments.values()
        ],
    }

def hospital_from_dict(data: dict) -> Hospital:
    h = Hospital(data["name"], data["location"])
    h.departments = {}
    for d in data.get("departments", []):
        dept = Department(d["name"], int(d.get("capacity", 50)))
        dept.patients = []
        dept.staff = []

        for pd in d.get("patients", []):
            p = Patient(pd["name"], int(pd["age"]), pd.get("medical_record", ""))
            p.id = pd.get("id", p.id)
            p.patient_id = pd.get("patient_id", p.patient_id)
            p.created_at = dt_from_str(pd.get("created_at"))
            p.admission_date = dt_from_str(pd.get("admission_date"))
            p.is_discharged = bool(pd.get("is_discharged", False))
            p.discharge_date = dt_from_str(pd.get("discharge_date"))
            dept.patients.append(p)

        for sd in d.get("staff", []):
            s = Staff(sd["name"], int(sd["age"]), sd["position"], dept.name)
            s.id = sd.get("id", s.id)
            s.staff_id = sd.get("staff_id", s.staff_id)
            s.created_at = dt_from_str(sd.get("created_at"))
            s.is_active = bool(sd.get("is_active", True))
            s.department = dept.name
            dept.staff.append(s)

        h.departments[dept.name] = dept
    return h


# ================= Appointments =================
class AppointmentStatus:
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked-in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @staticmethod
    def all():
        return [AppointmentStatus.SCHEDULED, AppointmentStatus.CHECKED_IN,
                AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]

    @staticmethod
    def label(status: str) -> str:
        key = {
            AppointmentStatus.SCHEDULED: "appt.status.scheduled",
            AppointmentStatus.CHECKED_IN: "appt.status.checked_in",
            AppointmentStatus.COMPLETED: "appt.status.completed",
            AppointmentStatus.CANCELLED: "appt.status.cancelled",
        }.get(status, status)
        return I18N.t(key) if isinstance(key, str) else key

    @staticmethod
    def from_label(label: str) -> str:
        reverse = {AppointmentStatus.label(s): s for s in AppointmentStatus.all()}
        return reverse.get(label, label)

    @staticmethod
    def is_active(status: str) -> bool:
        return status in (AppointmentStatus.SCHEDULED, AppointmentStatus.CHECKED_IN)


class Appointment:
    def __init__(self, patient_person_id: str, staff_person_id: Optional[str],
                 dept_name: str, start: datetime, end: datetime,
                 status: str = AppointmentStatus.SCHEDULED, notes: str = "",
                 appt_id: Optional[str] = None):
        self.id = appt_id or uuid.uuid4().hex[:10]
        self.patient_person_id = patient_person_id
        self.staff_person_id = staff_person_id
        self.dept_name = dept_name
        self.start = start
        self.end = end
        self.status = status
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "patient_person_id": self.patient_person_id,
            "staff_person_id": self.staff_person_id,
            "dept_name": self.dept_name,
            "start": dt_to_str(self.start),
            "end": dt_to_str(self.end),
            "status": self.status,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(d: dict) -> "Appointment":
        return Appointment(
            patient_person_id=d["patient_person_id"],
            staff_person_id=d.get("staff_person_id"),
            dept_name=d["dept_name"],
            start=dt_from_str(d["start"]),
            end=dt_from_str(d["end"]),
            status=d.get("status", AppointmentStatus.SCHEDULED),
            notes=d.get("notes", ""),
            appt_id=d.get("id"),
        )


class AppointmentManager:
    def __init__(self, hospital: Hospital):
        self.hospital = hospital
        self.items: List[Appointment] = []
        self._patient_index: Dict[str, Patient] = {}
        self._staff_index: Dict[str, Staff] = {}
        self.rebuild_indexes()

    def bind_hospital(self, hospital: Hospital):
        self.hospital = hospital
        self.rebuild_indexes()

    def rebuild_indexes(self):
        self._patient_index.clear()
        self._staff_index.clear()
        for d in self.hospital.departments.values():
            for p in d.patients:
                self._patient_index[p.id] = p
            for s in d.staff:
                self._staff_index[s.id] = s

    @staticmethod
    def _overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
        return (a_start < b_end) and (a_end > b_start)

    def find_conflicts(self, patient_id: str, staff_id: Optional[str],
                       start: datetime, end: datetime, ignore_id: Optional[str] = None
                       ) -> List[Tuple[Appointment, List[str]]]:
        conflicts: List[Tuple[Appointment, List[str]]] = []
        for a in self.items:
            if ignore_id and a.id == ignore_id:
                continue
            if not AppointmentStatus.is_active(a.status):
                continue
            if not self._overlap(start, end, a.start, a.end):
                continue
            reasons: List[str] = []
            if patient_id == a.patient_person_id:
                reasons.append("patient")
            if staff_id and a.staff_person_id and staff_id == a.staff_person_id:
                reasons.append("staff")
            if reasons:
                conflicts.append((a, reasons))
        return conflicts

    def add(self, patient: Patient, dept: Department, start: datetime,
            end: datetime, staff: Optional[Staff] = None, notes: str = "") -> Appointment:
        appt = Appointment(
            patient_person_id=patient.id,
            staff_person_id=(staff.id if staff else None),
            dept_name=dept.name,
            start=start, end=end,
            status=AppointmentStatus.SCHEDULED,
            notes=notes
        )
        self.items.append(appt)
        return appt

    def remove(self, appt_id: str):
        self.items = [a for a in self.items if a.id != appt_id]

    def update_status(self, appt_id: str, status: str):
        for a in self.items:
            if a.id == appt_id:
                a.status = status
                return a
        return None

    def list_filtered(self, day: Optional[date] = None,
                      dept_name: Optional[str] = None,
                      status: Optional[str] = None) -> List[Appointment]:
        out = self.items
        if day:
            out = [a for a in out if a.start.date() == day]
        if dept_name and dept_name != "__ALL__":
            out = [a for a in out if a.dept_name == dept_name]
        if status and status != "__ALL__":
            out = [a for a in out if a.status == status]
        return sorted(out, key=lambda a: a.start)

    def patient_of(self, a: Appointment) -> Optional[Patient]:
        return self._patient_index.get(a.patient_person_id)
    def staff_of(self, a: Appointment) -> Optional[Staff]:
        return self._staff_index.get(a.staff_person_id) if a.staff_person_id else None

    def to_dict(self) -> dict:
        return {"items": [a.to_dict() for a in self.items]}
    def from_dict(self, d: dict):
        self.items = [Appointment.from_dict(x) for x in d.get("items", [])]


# ================= Filter Proxy (multi-column contains) =================
class ContainsFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setRecursiveFilteringEnabled(True)

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        pattern = self.filterRegularExpression()
        if not pattern.pattern():
            return True
        model = self.sourceModel()
        cols = model.columnCount()
        for c in range(cols):
            idx = model.index(source_row, c, source_parent)
            text = str(model.data(idx, Qt.DisplayRole) or "")
            if pattern.match(text):
                return True
        return False


# ================= Table Models =================
class PatientTableModel(QAbstractTableModel):
    COLS = ["pid", "name", "age", "status", "adm"]

    def __init__(self, dept: Optional[Department] = None, parent=None):
        super().__init__(parent)
        self.dept = dept
        I18N.language_changed.connect(self._on_lang)

    def set_department(self, dept: Optional[Department]):
        self.beginResetModel()
        self.dept = dept
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if (parent.isValid() or self.dept is None) else len(self.dept.patients)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or self.dept is None:
            return None
        p: Patient = self.dept.patients[index.row()]
        col = self.COLS[index.column()]
        if role == Qt.DisplayRole:
            if col == "pid": return p.patient_id
            if col == "name": return p.name
            if col == "age": return str(p.age)
            if col == "status": return I18N.t("status.discharged") if p.is_discharged else I18N.t("status.admitted")
            if col == "adm": return fmt_dt(getattr(p, "admission_date", None))
        if role == Qt.UserRole:
            return p
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        if orientation == Qt.Horizontal:
            mapping = {
                "pid": I18N.t("col.pat.pid"),
                "name": I18N.t("col.pat.name"),
                "age": I18N.t("col.pat.age"),
                "status": I18N.t("col.pat.status"),
                "adm": I18N.t("col.pat.adm"),
            }
            return mapping[self.COLS[section]]
        return section + 1

    def flags(self, index):
        fl = super().flags(index)
        return fl | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def mimeTypes(self):
        return ["application/x-patient-ids"]

    def mimeData(self, indexes):
        rows = sorted(set(idx.row() for idx in indexes))
        ids = []
        if self.dept:
            for r in rows:
                ids.append(self.dept.patients[r].id)
        md = QMimeData()
        md.setData("application/x-patient-ids", QByteArray(("\n".join(ids)).encode("utf-8")))
        return md

    def _on_lang(self, lang: str):
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount()-1)


class StaffTableModel(QAbstractTableModel):
    COLS = ["sid", "name", "pos", "status", "age"]

    def __init__(self, dept: Optional[Department] = None, parent=None):
        super().__init__(parent)
        self.dept = dept
        I18N.language_changed.connect(self._on_lang)

    def set_department(self, dept: Optional[Department]):
        self.beginResetModel()
        self.dept = dept
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if (parent.isValid() or self.dept is None) else len(self.dept.staff)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or self.dept is None:
            return None
        s: Staff = self.dept.staff[index.row()]
        col = self.COLS[index.column()]
        if role == Qt.DisplayRole:
            if col == "sid": return s.staff_id
            if col == "name": return s.name
            if col == "pos": return s.position
            if col == "status": return I18N.t("staff.active") if s.is_active else I18N.t("staff.inactive")
            if col == "age": return str(s.age)
        if role == Qt.UserRole:
            return s
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        if orientation == Qt.Horizontal:
            mapping = {
                "sid": I18N.t("col.stf.sid"),
                "name": I18N.t("col.stf.name"),
                "pos": I18N.t("col.stf.pos"),
                "status": I18N.t("col.stf.status"),
                "age": I18N.t("col.stf.age"),
            }
            return mapping[self.COLS[section]]
        return section + 1

    def flags(self, index):
        fl = super().flags(index)
        return fl | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def _on_lang(self, lang: str):
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount()-1)


class AppointmentsTableModel(QAbstractTableModel):
    COLS = ["id", "dept", "patient", "staff", "start", "end", "status", "notes", "conflict"]

    def __init__(self, appts: 'AppointmentManager', parent=None):
        super().__init__(parent)
        self.appts = appts
        self.items: List[Appointment] = []
        I18N.language_changed.connect(self._on_lang)

    def set_items(self, items: List[Appointment]):
        self.beginResetModel()
        self.items = items
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        a = self.items[index.row()]
        col = self.COLS[index.column()]
        if role == Qt.DisplayRole:
            if col == "id": return a.id
            if col == "dept": return a.dept_name
            if col == "patient":
                p = self.appts.patient_of(a)
                return f"{getattr(p, 'patient_id', '')} - {getattr(p, 'name', '(N/A)')}" if p else "(N/A)"
            if col == "staff":
                s = self.appts.staff_of(a)
                return f"{s.staff_id} - {s.name}" if s else I18N.t("filter.all")
            if col == "start": return fmt_dt(a.start)
            if col == "end": return fmt_dt(a.end)
            if col == "status": return AppointmentStatus.label(a.status)
            if col == "notes": return a.notes or ""
            if col == "conflict":
                has_conflict = AppointmentStatus.is_active(a.status) and \
                               len(self.appts.find_conflicts(a.patient_person_id, a.staff_person_id, a.start, a.end, ignore_id=a.id)) > 0
                return "⚠" if has_conflict else ""
        if role == Qt.UserRole:
            return a
        if role == Qt.ToolTipRole and col == "conflict":
            conflicts = self.appts.find_conflicts(a.patient_person_id, a.staff_person_id, a.start, a.end, ignore_id=a.id)
            if conflicts:
                lines = []
                for c, reasons in conflicts:
                    who = []
                    if "patient" in reasons: who.append(I18N.t("who.patient"))
                    if "staff" in reasons: who.append(I18N.t("who.staff"))
                    joiner = " & " if I18N.lang == "en" else " و "
                    who_s = joiner.join(who)
                    lines.append(f"#{c.id} | {c.dept_name} | {fmt_dt(c.start, time_only=True)}-{fmt_dt(c.end, time_only=True)} | {who_s}")
                return "\n".join(lines)
        if role == Qt.BackgroundRole:
            if self.data(index.siblingAtColumn(self.COLS.index("conflict")), Qt.DisplayRole) == "⚠":
                return QBrush(QColor(255, 235, 205))
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        if orientation == Qt.Horizontal:
            mapping = {
                "id": I18N.t("col.ap.id"),
                "dept": I18N.t("col.ap.dept"),
                "patient": I18N.t("col.ap.patient"),
                "staff": I18N.t("col.ap.staff"),
                "start": I18N.t("col.ap.start"),
                "end": I18N.t("col.ap.end"),
                "status": I18N.t("col.ap.status"),
                "notes": I18N.t("col.ap.notes"),
                "conflict": I18N.t("col.ap.conflict"),
            }
            return mapping[self.COLS[section]]
        return section + 1

    def _on_lang(self, lang: str):
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount()-1)


# ================= Patient Details Dialog =================
class PatientDetailsDialog(QDialog):
    def __init__(self, patient: Patient, parent=None):
        super().__init__(parent)
        self.patient = patient
        self.setLayoutDirection(Qt.RightToLeft if I18N.lang == "ar" else Qt.LeftToRight)
        try:
            self.setFont(QFont("Cairo", 11))
        except Exception:
            pass

        form = QFormLayout(self)

        self.lbl_patient_id_label = QLabel("")
        self.lbl_state_label = QLabel("")
        self.lbl_name_label = QLabel("")
        self.lbl_age_label = QLabel("")
        self.lbl_med_label = QLabel("")

        self.id_val = QLabel(patient.patient_id)
        self.state_val = QLabel("")
        self.name_in = QLineEdit(patient.name)
        self.age_in = QSpinBox(); self.age_in.setRange(1, 120); self.age_in.setValue(int(patient.age))
        self.med_in = QPlainTextEdit(patient.medical_record)

        form.addRow(self.lbl_patient_id_label, self.id_val)
        form.addRow(self.lbl_state_label, self.state_val)
        form.addRow(self.lbl_name_label, self.name_in)
        form.addRow(self.lbl_age_label, self.age_in)
        form.addRow(self.lbl_med_label, self.med_in)

        info_box = QGroupBox("")
        info_form = QFormLayout(info_box)
        self.lbl_adm_label = QLabel("")
        self.lbl_dis_label = QLabel("")
        self.adm_val = QLabel(fmt_dt(getattr(patient, "admission_date", None)))
        self.dis_val = QLabel(fmt_dt(getattr(patient, "discharge_date", None)) if patient.is_discharged else "-")
        info_form.addRow(self.lbl_adm_label, self.adm_val)
        info_form.addRow(self.lbl_dis_label, self.dis_val)
        form.addRow(info_box)

        buttons = QDialogButtonBox()
        self.btn_save = buttons.addButton("", QDialogButtonBox.AcceptRole)
        self.btn_close = buttons.addButton("", QDialogButtonBox.RejectRole)
        self.btn_print = buttons.addButton("", QDialogButtonBox.ActionRole)
        self.btn_export_pdf = buttons.addButton("", QDialogButtonBox.ActionRole)
        self.btn_discharge = None
        if not patient.is_discharged:
            self.btn_discharge = buttons.addButton("", QDialogButtonBox.DestructiveRole)

        self.btn_save.clicked.connect(self.handle_save)
        self.btn_close.clicked.connect(self.reject)
        self.btn_print.clicked.connect(self.handle_print)
        self.btn_export_pdf.clicked.connect(self.handle_export_pdf)
        if self.btn_discharge:
            self.btn_discharge.clicked.connect(self.handle_discharge)

        form.addRow(buttons)

        I18N.language_changed.connect(self._on_lang)
        self.retranslate_ui()

    def _on_lang(self, lang: str):
        self.setLayoutDirection(Qt.RightToLeft if lang == "ar" else Qt.LeftToRight)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(I18N.t("dialog.patient_details.title", id=self.patient.patient_id))
        self.lbl_patient_id_label.setText(I18N.t("label.patient_id:"))
        self.lbl_state_label.setText(I18N.t("label.state:"))
        self.lbl_name_label.setText(I18N.t("field.name"))
        self.lbl_age_label.setText(I18N.t("field.age"))
        self.lbl_med_label.setText(I18N.t("field.medical_record"))
        self.state_val.setText(I18N.t("status.discharged") if self.patient.is_discharged else I18N.t("status.admitted"))
        self.lbl_adm_label.setText(I18N.t("label.admission_date:"))
        self.lbl_dis_label.setText(I18N.t("label.discharge_date:"))
        if self.btn_discharge:
            self.btn_discharge.setText(I18N.t("btn.discharge"))
        self.btn_save.setText(I18N.t("btn.save"))
        self.btn_close.setText(I18N.t("btn.close"))
        self.btn_print.setText(I18N.t("btn.print"))
        self.btn_export_pdf.setText(I18N.t("btn.export_pdf"))

    def handle_save(self):
        name = self.name_in.text().strip()
        age = int(self.age_in.value())
        if not name:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.patient.name_required"))
            return
        try:
            self.patient.name = name
            self.patient.age = age
            self.patient.medical_record = self.med_in.toPlainText().strip()
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.save.ok"))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), str(e))

    def _confirm_discharge_if_needed(self, count: int) -> bool:
        s = QSettings("HospitalApp", "UI")
        ask = s.value("confirm_discharge", "yes")
        if str(ask) != "no":
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(I18N.t("confirm.discharge.title"))
            box.setText(I18N.t("confirm.discharge.body", n=count))
            cb = QCheckBox(I18N.t("chk.dont_ask_again"), box)
            box.setCheckBox(cb)
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            res = box.exec()
            if res != QMessageBox.Yes:
                return False
            if cb.isChecked():
                s.setValue("confirm_discharge", "no")
        return True

    def handle_discharge(self):
        if not self._confirm_discharge_if_needed(1):
            return
        notes, ok = QInputDialog.getMultiLineText(self, I18N.t("dialog.discharge.notes_title"),
                                                  I18N.t("dialog.discharge.notes_prompt"), "")
        if not ok:
            return
        try:
            self.patient.discharge(notes)
            self.state_val.setText(I18N.t("status.discharged"))
            QMessageBox.information(self, I18N.t("msg.info.title"),
                                    I18N.t("msg.patient.discharged", name=self.patient.name))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), str(e))

    def _build_patient_html(self) -> str:
        p = self.patient
        return f"""
        <html><head><meta charset="utf-8"></head>
        <body>
        <h2>Patient Record</h2>
        <p><b>ID:</b> {p.patient_id}<br/>
        <b>Name:</b> {p.name}<br/>
        <b>Age:</b> {p.age}<br/>
        <b>Status:</b> {"Discharged" if p.is_discharged else "Admitted"}<br/>
        <b>Admission:</b> {fmt_dt(getattr(p,"admission_date", None))}<br/>
        <b>Discharge:</b> {fmt_dt(getattr(p,"discharge_date", None)) if p.is_discharged else "-"}</p>
        <h3>Medical Record</h3>
        <pre>{p.medical_record}</pre>
        </body></html>
        """

    def handle_print(self):
        doc = QTextDocument()
        doc.setHtml(self._build_patient_html())
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec():
            doc.print(printer)

    def handle_export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, I18N.t("dialog.export.pdf.title"),
                                              f"{self.patient.patient_id}.pdf",
                                              I18N.t("dialog.pdf.filter"))
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            doc = QTextDocument()
            doc.setHtml(self._build_patient_html())
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc.print(printer)
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.export.ok"))
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.export.fail", err=e))


# ================= Dept list drop target =================
class DepartmentListWidget(QListWidget):
    patients_dropped = Signal(list, object)  # list[patient_id], Department target

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat("application/x-patient-ids"):
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasFormat("application/x-patient-ids"):
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e):
        item = self.itemAt(e.position().toPoint())
        if item and e.mimeData().hasFormat("application/x-patient-ids"):
            data = bytes(e.mimeData().data("application/x-patient-ids")).decode("utf-8")
            ids = [x for x in data.split("\n") if x]
            dept = item.data(Qt.UserRole)
            self.patients_dropped.emit(ids, dept)
            e.acceptProposedAction()
        else:
            super().dropEvent(e)


# ================= Main Window =================
class HospitalWindow(QMainWindow):
    def __init__(self, hospital: Hospital):
        super().__init__()
        self.hospital = hospital
        self.appts = AppointmentManager(self.hospital)
        self.current_file_path: Optional[str] = None

        self.setLayoutDirection(Qt.RightToLeft if I18N.lang == "ar" else Qt.LeftToRight)
        self.setMinimumSize(1350, 820)
        try:
            self.setFont(QFont("Cairo", 11))
        except Exception:
            pass

        self.page = MainPage(self.hospital, self.appts, self)
        self.setCentralWidget(self.page)

        self._build_menu()
        self._build_toolbar()
        self._build_shortcuts()
        self._apply_app_icon()

        I18N.language_changed.connect(self._on_lang)
        THEME.theme_changed.connect(self._on_theme_changed)
        self.retranslate_ui()
        self._on_theme_changed(THEME.theme)
        self.setStatusBar(QStatusBar())

        # Restore window geometry/state
        self._restore_window_state()

    def _apply_app_icon(self):
        # Try custom icon, fallback to standard
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

    def _build_menu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("")
        self.act_new = self.file_menu.addAction("")
        self.act_open = self.file_menu.addAction("")
        self.act_save = self.file_menu.addAction("")
        self.act_save_as = self.file_menu.addAction("")
        self.file_menu.addSeparator()
        self.export_menu = self.file_menu.addMenu("")
        self.act_export_pat_cur = self.export_menu.addAction("")
        self.act_export_pat_all = self.export_menu.addAction("")
        self.act_export_stf_cur = self.export_menu.addAction("")
        self.act_export_stf_all = self.export_menu.addAction("")
        self.export_menu.addSeparator()
        self.act_export_appts = self.export_menu.addAction("")

        self.act_new.triggered.connect(self.handle_new)
        self.act_open.triggered.connect(self.handle_open)
        self.act_save.triggered.connect(self.handle_save)
        self.act_save_as.triggered.connect(self.handle_save_as)
        self.act_export_pat_cur.triggered.connect(lambda: self.page.export_patients_csv(all_depts=False))
        self.act_export_pat_all.triggered.connect(lambda: self.page.export_patients_csv(all_depts=True))
        self.act_export_stf_cur.triggered.connect(lambda: self.page.export_staff_csv(all_depts=False))
        self.act_export_stf_all.triggered.connect(lambda: self.page.export_staff_csv(all_depts=True))
        self.act_export_appts.triggered.connect(self.page.export_appts_csv_filtered)

        self.lang_menu = menubar.addMenu("")
        self.act_lang_ar = self.lang_menu.addAction("")
        self.act_lang_en = self.lang_menu.addAction("")
        self.act_lang_ar.triggered.connect(lambda: I18N.set_language("ar"))
        self.act_lang_en.triggered.connect(lambda: I18N.set_language("en"))

        self.theme_menu = menubar.addMenu("")
        self.act_theme_light = self.theme_menu.addAction("")
        self.act_theme_dark = self.theme_menu.addAction("")
        self.act_theme_light.setCheckable(True)
        self.act_theme_dark.setCheckable(True)
        self.act_theme_light.triggered.connect(lambda: THEME.set_theme("light"))
        self.act_theme_dark.triggered.connect(lambda: THEME.set_theme("dark"))

        self.help_menu = menubar.addMenu("")
        self.act_about = self.help_menu.addAction("")
        self.act_about.triggered.connect(self.show_about_dialog)

    def _build_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)

        self.tb_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), I18N.t("toolbar.save"), self)
        self.tb_add_patient = QAction(self.style().standardIcon(QStyle.SP_FileIcon), I18N.t("toolbar.add_patient"), self)
        self.tb_add_appt = QAction(self.style().standardIcon(QStyle.SP_FileDialogNewFolder), I18N.t("toolbar.add_appt"), self)
        self.tb_refresh = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), I18N.t("toolbar.refresh"), self)

        self.tb_save.triggered.connect(self.handle_save)
        self.tb_add_patient.triggered.connect(self.page.quick_add_patient)
        self.tb_add_appt.triggered.connect(self.page.quick_add_appointment)
        self.tb_refresh.triggered.connect(self.page.refresh_all)

        tb.addAction(self.tb_save)
        tb.addAction(self.tb_add_patient)
        tb.addAction(self.tb_add_appt)
        tb.addAction(self.tb_refresh)
        tb.addSeparator()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(I18N.t("toolbar.search.ph"))
        self.search_box.textChanged.connect(self.page.set_global_filter)
        tb.addWidget(self.search_box)

    def _build_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.handle_save)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.page.quick_add_patient)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search_box.setFocus())
        QShortcut(QKeySequence("F5"), self, activated=self.page.refresh_all)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: I18N.set_language("en" if I18N.lang=="ar" else "ar"))
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: THEME.set_theme("dark" if THEME.theme=="light" else "light"))

    def _on_lang(self, lang: str):
        # Locale update
        if lang == "ar":
            QLocale.setDefault(QLocale(QLocale.Arabic))
        else:
            QLocale.setDefault(QLocale(QLocale.English))
        self.setLayoutDirection(Qt.RightToLeft if lang == "ar" else Qt.LeftToRight)
        self.retranslate_ui()
        self.page.retranslate_ui()
        self.search_box.setPlaceholderText(I18N.t("toolbar.search.ph"))
        self.statusBar().showMessage("Language changed" if lang=="en" else "تم تغيير اللغة", 2000)

    def _on_theme_changed(self, theme: str):
        if hasattr(self, "act_theme_light"):
            self.act_theme_light.setChecked(theme == "light")
            self.act_theme_dark.setChecked(theme == "dark")
        self.statusBar().showMessage("Dark theme applied" if theme=="dark" else "Light theme applied", 2000)

    def retranslate_ui(self):
        self.setWindowTitle(I18N.t("app.title", name=self.hospital.name))
        self.file_menu.setTitle(I18N.t("menu.file"))
        self.act_new.setText(I18N.t("menu.file.new"))
        self.act_open.setText(I18N.t("menu.file.open"))
        self.act_save.setText(I18N.t("menu.file.save"))
        self.act_save_as.setText(I18N.t("menu.file.saveas"))
        self.export_menu.setTitle(I18N.t("menu.file.export"))
        self.act_export_pat_cur.setText(I18N.t("menu.file.export.patients_current"))
        self.act_export_pat_all.setText(I18N.t("menu.file.export.patients_all"))
        self.act_export_stf_cur.setText(I18N.t("menu.file.export.staff_current"))
        self.act_export_stf_all.setText(I18N.t("menu.file.export.staff_all"))
        self.act_export_appts.setText(I18N.t("menu.file.export.appts_filtered"))

        self.lang_menu.setTitle(I18N.t("menu.language"))
        self.act_lang_ar.setText(I18N.t("menu.language.ar"))
        self.act_lang_en.setText(I18N.t("menu.language.en"))
        self.theme_menu.setTitle(I18N.t("menu.theme"))
        self.act_theme_light.setText(I18N.t("menu.theme.light"))
        self.act_theme_dark.setText(I18N.t("menu.theme.dark"))
        self.help_menu.setTitle(I18N.t("menu.help"))
        self.act_about.setText(I18N.t("menu.help.about"))
        
        self.tb_save.setText(I18N.t("toolbar.save"))
        self.tb_add_patient.setText(I18N.t("toolbar.add_patient"))
        self.tb_add_appt.setText(I18N.t("toolbar.add_appt"))
        self.tb_refresh.setText(I18N.t("toolbar.refresh"))

    def show_about_dialog(self):
        # Simple About dialog using QMessageBox with rich text
        text = I18N.t("about.body", ver=APP_VERSION)
        QMessageBox.about(self, I18N.t("msg.about.title"), text)
        # Allow links to open
        QDesktopServices.openUrl(QUrl("https://qt.io"))

    # ----- File ops -----
    def handle_new(self):
        if QMessageBox.question(self, I18N.t("msg.confirm.title"), I18N.t("msg.new.confirm")) != QMessageBox.Yes:
            return
        self.hospital = Hospital("New Hospital", "Unknown")
        self.appts = AppointmentManager(self.hospital)
        self.current_file_path = None
        self._reload_page()

    def handle_open(self):
        path, _ = QFileDialog.getOpenFileName(self, I18N.t("dialog.open.title"), "", I18N.t("dialog.json.filter"))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            h = hospital_from_dict(data["hospital"])
            ap = AppointmentManager(h)
            ap.from_dict(data.get("appointments", {}))
            ap.bind_hospital(h)
            self.hospital = h
            self.appts = ap
            self.current_file_path = path
            self._reload_page()
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.loaded_ok"))
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.open.fail", err=e))

    def handle_save(self):
        if not self.current_file_path:
            return self.handle_save_as()
        try:
            data = {"version": 1, "hospital": hospital_to_dict(self.hospital), "appointments": self.appts.to_dict()}
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.statusBar().showMessage(I18N.t("msg.save.ok"), 3000)
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.save.fail", err=e))

    def handle_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, I18N.t("dialog.save.title"), "hospital_data.json", I18N.t("dialog.json.filter"))
        if not path:
            return
        self.current_file_path = path
        self.handle_save()

    def _reload_page(self):
        self.page.save_layouts()
        self.page.setParent(None)
        self.page = MainPage(self.hospital, self.appts, self)
        self.setCentralWidget(self.page)
        self.retranslate_ui()

    def _restore_window_state(self):
        s = QSettings("HospitalApp", "UI")
        geom = s.value("window_geometry")
        st = s.value("window_state")
        if isinstance(geom, QByteArray):
            self.restoreGeometry(geom)
        if isinstance(st, QByteArray):
            self.restoreState(st)

    def _save_window_state(self):
        s = QSettings("HospitalApp", "UI")
        s.setValue("window_geometry", self.saveGeometry())
        s.setValue("window_state", self.saveState())

    def closeEvent(self, e):
        try:
            self.page.save_layouts()
            self._save_window_state()
        except Exception:
            pass
        super().closeEvent(e)


# ================= Main Page =================
class MainPage(QWidget):
    def __init__(self, hospital: Hospital, appts: AppointmentManager, win: HospitalWindow):
        super().__init__()
        self.hospital = hospital
        self.appts = appts
        self.win = win
        self._build_ui()
        I18N.language_changed.connect(self._on_lang)
        THEME.theme_changed.connect(lambda _: self.refresh_dashboard())
        self.retranslate_ui()

    # ---------- UI build ----------
    def _build_ui(self):
        root = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        root.addWidget(self.splitter)

        # Left: Departments
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.lbl_depts = QLabel("")
        self.dept_list = DepartmentListWidget()
        self.dept_list.currentItemChanged.connect(self.on_dept_changed)
        self.dept_list.patients_dropped.connect(self.on_patients_dropped_to_dept)

        self.add_dept_group = QGroupBox("")
        self.add_dept_form = QFormLayout(self.add_dept_group)
        self.dept_name_in = QLineEdit()
        self.dept_name_in.setPlaceholderText(I18N.t("ph.dept_name"))
        self.dept_cap_in = QSpinBox(); self.dept_cap_in.setRange(10, 2000); self.dept_cap_in.setValue(50)
        self.btn_add_dept = QPushButton("")
        self.btn_add_dept.clicked.connect(self.handle_add_department)
        self.add_dept_form_label_name = QLabel("")
        self.add_dept_form_label_cap = QLabel("")
        self.add_dept_form.addRow(self.add_dept_form_label_name, self.dept_name_in)
        self.add_dept_form.addRow(self.add_dept_form_label_cap, self.dept_cap_in)
        self.add_dept_form.addRow(self.btn_add_dept)

        # live clear invalid on typing
        self.dept_name_in.textChanged.connect(lambda _: self.clear_invalid(self.dept_name_in))

        left_layout.addWidget(self.lbl_depts)
        left_layout.addWidget(self.dept_list, 1)
        left_layout.addWidget(self.add_dept_group, 0)

        # Right: Info + Tabs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.info_group = QGroupBox("")
        info_layout = QFormLayout(self.info_group)
        self.lbl_dept_name = QLabel("-")
        self.lbl_dept_code = QLabel("-")
        self.lbl_dept_capacity = QLabel("-")
        self.lbl_patients_count = QLabel("-")
        self.lbl_staff_count = QLabel("-")
        self.info_label_name = QLabel("")
        self.info_label_code = QLabel("")
        self.info_label_cap = QLabel("")
        self.info_label_patcnt = QLabel("")
        self.info_label_staffcnt = QLabel("")
        info_layout.addRow(self.info_label_name, self.lbl_dept_name)
        info_layout.addRow(self.info_label_code, self.lbl_dept_code)
        info_layout.addRow(self.info_label_cap, self.lbl_dept_capacity)
        info_layout.addRow(self.info_label_patcnt, self.lbl_patients_count)
        info_layout.addRow(self.info_label_staffcnt, self.lbl_staff_count)

        self.tabs = QTabWidget()
        self._build_dashboard_tab()
        self._build_patients_tab()
        self._build_staff_tab()
        self._build_search_tab()
        self._build_appointments_tab()

        right_layout.addWidget(self.info_group)
        right_layout.addWidget(self.tabs, 1)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([320, 1030])

        self.refresh_department_list()
        # Restore splitter state if saved
        self.restore_splitter_state(self.splitter, "main_splitter_state")

    # ---------- Dashboard ----------
    def _build_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.dash_group_stats = QGroupBox("")
        stats_form = QFormLayout(self.dash_group_stats)
        self.dash_label_total_depts = QLabel("")
        self.dash_label_total_patients = QLabel("")
        self.dash_label_active_patients = QLabel("")
        self.dash_label_total_staff = QLabel("")
        self.dash_label_appts_today = QLabel("")
        self.dash_val_total_depts = QLabel("-")
        self.dash_val_total_patients = QLabel("-")
        self.dash_val_active_patients = QLabel("-")
        self.dash_val_total_staff = QLabel("-")
        self.dash_val_appts_today = QLabel("-")
        stats_form.addRow(self.dash_label_total_depts, self.dash_val_total_depts)
        stats_form.addRow(self.dash_label_total_patients, self.dash_val_total_patients)
        stats_form.addRow(self.dash_label_active_patients, self.dash_val_active_patients)
        stats_form.addRow(self.dash_label_total_staff, self.dash_val_total_staff)
        stats_form.addRow(self.dash_label_appts_today, self.dash_val_appts_today)

        self.dash_group_chart = QGroupBox("")
        v = QVBoxLayout(self.dash_group_chart)
        self.btn_dash_refresh = QPushButton("")
        self.btn_dash_refresh.clicked.connect(self.refresh_dashboard)
        v.addWidget(self.btn_dash_refresh, alignment=Qt.AlignLeft)

        if HAS_QTCHARTS:
            self.chart = QChart()
            self.chart_view = QChartView(self.chart)
            v.addWidget(self.chart_view, 1)
        else:
            self.dash_chart_placeholder = QLabel("")
            self.dash_chart_placeholder.setAlignment(Qt.AlignCenter)
            v.addWidget(self.dash_chart_placeholder, 1)

        layout.addWidget(self.dash_group_stats)
        layout.addWidget(self.dash_group_chart, 1)

        self.tab_idx_dashboard = self.tabs.addTab(tab, "")

    def refresh_dashboard(self):
        total_depts = len(self.hospital.departments)
        total_patients = sum(len(d.patients) for d in self.hospital.departments.values())
        active_patients = sum(len(d.get_active_patients()) for d in self.hospital.departments.values())
        total_staff = sum(len(d.staff) for d in self.hospital.departments.values())
        today = date.today()
        appts_today = sum(1 for a in self.appts.items if a.start.date() == today)
        self.dash_val_total_depts.setText(str(total_depts))
        self.dash_val_total_patients.setText(str(total_patients))
        self.dash_val_active_patients.setText(str(active_patients))
        self.dash_val_total_staff.setText(str(total_staff))
        self.dash_val_appts_today.setText(str(appts_today))

        if not HAS_QTCHARTS:
            return
        statuses = AppointmentStatus.all()
        counts = {s: 0 for s in statuses}
        for a in self.appts.items:
            if a.start.date() == today:
                counts[a.status] = counts.get(a.status, 0) + 1

        series = QBarSeries()
        set0 = QBarSet("")
        set0.append([counts[s] for s in statuses])
        series.append(set0)

        chart = QChart()
        chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append([AppointmentStatus.label(s) for s in statuses])
        axis_y = QValueAxis()
        axis_y.setRange(0, max([0] + list(counts.values())))
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x); series.attachAxis(axis_y)
        chart.setTitle(I18N.t("dash.chart.appts_by_status"))
        try:
            chart.setTheme(QChart.ChartThemeDark if THEME.theme == "dark" else QChart.ChartThemeLight)
        except Exception:
            pass
        self.chart = chart
        self.chart_view.setChart(self.chart)

    # ---------- Patients tab ----------
    def _build_patients_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.add_patient_group = QGroupBox("")
        form = QFormLayout(self.add_patient_group)
        self.p_name_in = QLineEdit()
        self.p_name_in.setPlaceholderText(I18N.t("ph.patient_name"))
        self.p_age_in = QSpinBox(); self.p_age_in.setRange(1, 120)
        self.p_med_rec_in = QPlainTextEdit()
        self.btn_add_patient = QPushButton("")
        self.btn_add_patient.clicked.connect(self.handle_add_patient)
        self.add_patient_label_name = QLabel("")
        self.add_patient_label_age = QLabel("")
        self.add_patient_label_med = QLabel("")
        self.add_patient_label_name.setBuddy(self.p_name_in)
        self.add_patient_label_age.setBuddy(self.p_age_in)
        self.add_patient_label_med.setBuddy(self.p_med_rec_in)
        form.addRow(self.add_patient_label_name, self.p_name_in)
        form.addRow(self.add_patient_label_age, self.p_age_in)
        form.addRow(self.add_patient_label_med, self.p_med_rec_in)
        form.addRow(self.btn_add_patient)

        self.p_name_in.textChanged.connect(lambda _: self.clear_invalid(self.p_name_in))

        self.p_model = PatientTableModel(None, self)
        self.p_proxy = ContainsFilterProxy(self)
        self.p_proxy.setSourceModel(self.p_model)

        self.p_table = QTableView()
        self.p_table.setModel(self.p_proxy)
        self.p_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.p_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.p_table.setAlternatingRowColors(True)
        self.p_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.p_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.p_table.customContextMenuRequested.connect(self.on_patients_context)
        self.p_table.doubleClicked.connect(self.on_patient_double_click)
        self.p_table.setDragEnabled(True)
        self.p_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.p_table.setSortingEnabled(True)
        self.restore_header_state(self.p_table, "patients_header_state")

        layout.addWidget(self.add_patient_group)
        layout.addWidget(self.p_table, 1)

        # Empty overlay for patients table
        self.p_empty = QLabel(self.p_table.viewport())
        self.p_empty.setAlignment(Qt.AlignCenter)
        self.p_empty.setStyleSheet("color: #888;")
        self.p_empty.hide()

        # Keyboard shortcuts for data entry in this tab
        QShortcut(QKeySequence("Alt+N"), tab, activated=lambda: self.p_name_in.setFocus())
        QShortcut(QKeySequence("Alt+A"), tab, activated=lambda: self.p_age_in.setFocus())
        QShortcut(QKeySequence("Alt+M"), tab, activated=lambda: self.p_med_rec_in.setFocus())

        # Tab order
        QWidget.setTabOrder(self.p_name_in, self.p_age_in)
        QWidget.setTabOrder(self.p_age_in, self.p_med_rec_in)
        QWidget.setTabOrder(self.p_med_rec_in, self.btn_add_patient)

        self.tab_idx_patients = self.tabs.addTab(tab, "")

    def on_patient_double_click(self, idx: QModelIndex):
        if not idx.isValid():
            return
        p = self.p_proxy.index(idx.row(), 0).data(Qt.UserRole)
        if p:
            dlg = PatientDetailsDialog(p, self)
            if dlg.exec():
                self.p_model.layoutChanged.emit()
                self.refresh_patients_table_related()

    def on_patients_context(self, pos):
        idxs = self.p_table.selectionModel().selectedRows()
        menu = QMenu(self)
        a_details = menu.addAction(I18N.t("ctx.p.details"))
        a_discharge = menu.addAction(I18N.t("ctx.p.discharge") if len(idxs)==1 else I18N.t("ctx.p.discharge_sel"))
        a_move = menu.addAction(I18N.t("ctx.p.move") if len(idxs)==1 else I18N.t("ctx.p.move_sel"))
        a_copy = None
        a_print = None
        a_pdf = None
        if len(idxs)==1:
            a_copy = menu.addAction(I18N.t("ctx.p.copyid"))
            menu.addSeparator()
            a_print = menu.addAction(I18N.t("ctx.p.print"))
            a_pdf = menu.addAction(I18N.t("ctx.p.export_pdf"))
        act = menu.exec(self.p_table.viewport().mapToGlobal(pos))
        if not act: return
        patients = [self.p_proxy.index(i.row(),0).data(Qt.UserRole) for i in idxs]
        if act == a_details and len(patients)==1:
            dlg = PatientDetailsDialog(patients[0], self)
            if dlg.exec():
                self.p_model.layoutChanged.emit(); self.refresh_patients_table_related()
        elif act == a_discharge:
            self.discharge_patients(patients)
        elif act == a_move:
            self.move_patients_dialog(patients)
        elif a_copy and act == a_copy and len(patients)==1:
            QApplication.clipboard().setText(patients[0].patient_id)
        elif a_print and act == a_print and len(patients)==1:
            dlg = PatientDetailsDialog(patients[0], self)
            dlg.handle_print()
        elif a_pdf and act == a_pdf and len(patients)==1:
            dlg = PatientDetailsDialog(patients[0], self)
            dlg.handle_export_pdf()

    def _confirm_discharge_if_needed(self, count: int) -> bool:
        s = QSettings("HospitalApp", "UI")
        ask = s.value("confirm_discharge", "yes")
        if str(ask) != "no":
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(I18N.t("confirm.discharge.title"))
            box.setText(I18N.t("confirm.discharge.body", n=count))
            cb = QCheckBox(I18N.t("chk.dont_ask_again"), box)
            box.setCheckBox(cb)
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            res = box.exec()
            if res != QMessageBox.Yes:
                return False
            if cb.isChecked():
                s.setValue("confirm_discharge", "no")
        return True

    def discharge_patients(self, patients: List[Patient]):
        if not patients: return
        if not self._confirm_discharge_if_needed(len(patients)):
            return
        for p in patients:
            if not p.is_discharged:
                try:
                    p.discharge("")
                except Exception:
                    pass
        self.refresh_patients_table_related()
        QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("btn.discharge_selected"))

    def move_patients_dialog(self, patients: List[Patient]):
        if not patients: return
        names = [d.name for d in self.hospital.departments.values()]
        name, ok = QInputDialog.getItem(self, I18N.t("dialog.move_patient.title"),
                                        I18N.t("dialog.move_patient.prompt"), names, 0, False)
        if not ok: return
        dept_to = self.hospital.departments.get(name)
        self.move_patients_to_department_by_objs(patients, dept_to)

    def on_patients_dropped_to_dept(self, patient_ids: List[str], dept: Department):
        patients = []
        for d in self.hospital.departments.values():
            for p in d.patients:
                if p.id in patient_ids:
                    patients.append(p)
        self.move_patients_to_department_by_objs(patients, dept)

    def move_patients_to_department_by_objs(self, patients: List[Patient], dept_to: Department):
        for p in patients:
            if p.is_discharged: continue
            dept_from = None
            for d in self.hospital.departments.values():
                if p in d.patients: dept_from = d; break
            if not dept_from or dept_from is dept_to: continue
            if len(dept_to.patients) >= dept_to.capacity:
                QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.dept.full_with_name", name=dept_to.name))
                continue
            dept_from.patients = [x for x in dept_from.patients if x is not p]
            dept_to.patients.append(p)
            for a in self.appts.items:
                if a.patient_person_id == p.id and AppointmentStatus.is_active(a.status):
                    a.dept_name = dept_to.name
        self.refresh_patients_table_related()
        QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("btn.refresh"))

    def refresh_patients_table_related(self):
        self.p_model.layoutChanged.emit()
        self.update_dept_info()
        self.refresh_dashboard()
        self.update_empty_overlays()

    # ---------- Staff tab ----------
    def _build_staff_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.add_staff_group = QGroupBox("")
        form = QFormLayout(self.add_staff_group)
        self.s_name_in = QLineEdit()
        self.s_name_in.setPlaceholderText(I18N.t("ph.staff_name"))
        self.s_age_in = QSpinBox(); self.s_age_in.setRange(18, 100)
        self.s_position_in = QLineEdit()
        self.s_position_in.setPlaceholderText(I18N.t("ph.position_hint"))
        self.btn_add_staff = QPushButton("")
        self.btn_add_staff.clicked.connect(self.handle_add_staff)
        self.add_staff_label_name = QLabel("")
        self.add_staff_label_age = QLabel("")
        self.add_staff_label_pos = QLabel("")
        self.add_staff_label_name.setBuddy(self.s_name_in)
        self.add_staff_label_age.setBuddy(self.s_age_in)
        self.add_staff_label_pos.setBuddy(self.s_position_in)
        form.addRow(self.add_staff_label_name, self.s_name_in)
        form.addRow(self.add_staff_label_age, self.s_age_in)
        form.addRow(self.add_staff_label_pos, self.s_position_in)
        form.addRow(self.btn_add_staff)

        self.s_name_in.textChanged.connect(lambda _: self.clear_invalid(self.s_name_in))
        self.s_position_in.textChanged.connect(lambda _: self.clear_invalid(self.s_position_in))

        self.s_model = StaffTableModel(None, self)
        self.s_proxy = ContainsFilterProxy(self)
        self.s_proxy.setSourceModel(self.s_model)

        self.s_table = QTableView()
        self.s_table.setModel(self.s_proxy)
        self.s_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.s_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.s_table.setAlternatingRowColors(True)
        self.s_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.s_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.s_table.customContextMenuRequested.connect(self.on_staff_context)
        self.s_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.s_table.setSortingEnabled(True)
        self.restore_header_state(self.s_table, "staff_header_state")

        layout.addWidget(self.add_staff_group)
        layout.addWidget(self.s_table, 1)

        # Empty overlay
        self.s_empty = QLabel(self.s_table.viewport())
        self.s_empty.setAlignment(Qt.AlignCenter)
        self.s_empty.setStyleSheet("color: #888;")
        self.s_empty.hide()

        # Shortcuts
        QShortcut(QKeySequence("Alt+N"), tab, activated=lambda: self.s_name_in.setFocus())
        QShortcut(QKeySequence("Alt+A"), tab, activated=lambda: self.s_age_in.setFocus())
        QShortcut(QKeySequence("Alt+P"), tab, activated=lambda: self.s_position_in.setFocus())

        # Tab order
        QWidget.setTabOrder(self.s_name_in, self.s_age_in)
        QWidget.setTabOrder(self.s_age_in, self.s_position_in)
        QWidget.setTabOrder(self.s_position_in, self.btn_add_staff)

        self.tab_idx_staff = self.tabs.addTab(tab, "")

    def on_staff_context(self, pos):
        idxs = self.s_table.selectionModel().selectedRows()
        if not idxs: return
        menu = QMenu(self)
        a_toggle = menu.addAction(I18N.t("ctx.s.toggle"))
        a_copy = None
        if len(idxs)==1:
            a_copy = menu.addAction(I18N.t("ctx.s.copyid"))
        act = menu.exec(self.s_table.viewport().mapToGlobal(pos))
        if not act: return
        staff_list = [self.s_proxy.index(i.row(),0).data(Qt.UserRole) for i in idxs]
        if act == a_toggle:
            for s in staff_list: s.is_active = not s.is_active
            self.s_model.layoutChanged.emit(); self.refresh_dashboard(); self.update_empty_overlays()
        elif a_copy and act == a_copy:
            QApplication.clipboard().setText(staff_list[0].staff_id)

    # ---------- Search tab ----------
    def _build_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.search_group = QGroupBox("")
        grid = QGridLayout(self.search_group)

        # Mode
        self.search_mode_pat = QRadioButton(I18N.t("search.mode.patients"))
        self.search_mode_stf = QRadioButton(I18N.t("search.mode.staff"))
        self.search_mode_pat.setChecked(True)
        grid.addWidget(self.search_mode_pat, 0, 0)
        grid.addWidget(self.search_mode_stf, 0, 1)

        # Common term
        self.search_label_term = QLabel("")
        self.search_all_in = QLineEdit()
        self.search_all_in.setPlaceholderText(I18N.t("ph.search_all"))
        grid.addWidget(self.search_label_term, 1, 0)
        grid.addWidget(self.search_all_in, 1, 1, 1, 3)

        # Patient filters
        self.lbl_pat_status = QLabel("")
        self.cb_pat_status = QComboBox()
        self.cb_pat_status.addItem(I18N.t("filter.all"), "__ALL__")
        self.cb_pat_status.addItem(I18N.t("status.admitted"), "admitted")
        self.cb_pat_status.addItem(I18N.t("status.discharged"), "discharged")

        self.lbl_age_min = QLabel("")
        self.lbl_age_max = QLabel("")
        self.spin_age_min = QSpinBox(); self.spin_age_min.setRange(0, 120); self.spin_age_min.setValue(0)
        self.spin_age_max = QSpinBox(); self.spin_age_max.setRange(0, 120); self.spin_age_max.setValue(120)

        grid.addWidget(self.lbl_pat_status, 2, 0)
        grid.addWidget(self.cb_pat_status, 2, 1)
        grid.addWidget(self.lbl_age_min, 2, 2)
        grid.addWidget(self.spin_age_min, 2, 3)
        grid.addWidget(self.lbl_age_max, 2, 4)
        grid.addWidget(self.spin_age_max, 2, 5)

        # Staff filters
        self.lbl_staff_status = QLabel("")
        self.cb_staff_status = QComboBox()
        self.cb_staff_status.addItem(I18N.t("filter.all"), "__ALL__")
        self.cb_staff_status.addItem(I18N.t("staff.active"), "active")
        self.cb_staff_status.addItem(I18N.t("staff.inactive"), "inactive")
        self.lbl_staff_pos = QLabel(I18N.t("field.position"))
        self.in_staff_pos = QLineEdit(); self.in_staff_pos.setPlaceholderText(I18N.t("ph.position_hint"))

        grid.addWidget(self.lbl_staff_status, 3, 0)
        grid.addWidget(self.cb_staff_status, 3, 1)
        grid.addWidget(self.lbl_staff_pos, 3, 2)
        grid.addWidget(self.in_staff_pos, 3, 3, 1, 3)

        # Results list
        self.search_results = QListWidget()
        self.search_results.setAlternatingRowColors(True)
        self.search_results.itemDoubleClicked.connect(self.handle_search_navigate)
        self.lbl_results_count = QLabel(I18N.t("label.results_count", n=0))

        layout.addWidget(self.search_group)
        layout.addWidget(self.lbl_results_count)
        layout.addWidget(self.search_results, 1)

        # Reactions
        self.search_all_in.textChanged.connect(lambda _: self.handle_search_all())
        self.cb_pat_status.currentIndexChanged.connect(lambda _: self.handle_search_all())
        self.spin_age_min.valueChanged.connect(lambda _: self.handle_search_all())
        self.spin_age_max.valueChanged.connect(lambda _: self.handle_search_all())
        self.cb_staff_status.currentIndexChanged.connect(lambda _: self.handle_search_all())
        self.in_staff_pos.textChanged.connect(lambda _: self.handle_search_all())
        self.search_mode_pat.toggled.connect(lambda _: self.handle_search_all())

        self.tab_idx_search = self.tabs.addTab(tab, "")

    # ---------- Appointments tab ----------
    def _build_appointments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.create_appt_group = QGroupBox("")
        form = QFormLayout(self.create_appt_group)

        self.ap_dept_combo = QComboBox()
        self.ap_dept_combo.currentIndexChanged.connect(self._ap_on_dept_changed)
        self.ap_patient_combo = QComboBox()
        self.ap_staff_combo = QComboBox()
        self.ap_start_dt = QDateTimeEdit(QDateTime.currentDateTime()); self.ap_start_dt.setCalendarPopup(True)
        self.ap_end_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(1800)); self.ap_end_dt.setCalendarPopup(True)
        self.ap_notes_in = QLineEdit()
        self.ap_notes_in.setPlaceholderText(I18N.t("ph.appt_notes"))
        self.btn_add_appt = QPushButton("")
        self.btn_add_appt.clicked.connect(self.handle_add_appointment)
        self.ap_label_dept = QLabel("")
        self.ap_label_patient = QLabel("")
        self.ap_label_staff = QLabel("")
        self.ap_label_start = QLabel("")
        self.ap_label_end = QLabel("")
        self.ap_label_notes = QLabel("")
        self.ap_label_dept.setBuddy(self.ap_dept_combo)
        self.ap_label_patient.setBuddy(self.ap_patient_combo)
        self.ap_label_staff.setBuddy(self.ap_staff_combo)
        self.ap_label_start.setBuddy(self.ap_start_dt)
        self.ap_label_end.setBuddy(self.ap_end_dt)
        self.ap_label_notes.setBuddy(self.ap_notes_in)

        form.addRow(self.ap_label_dept, self.ap_dept_combo)
        form.addRow(self.ap_label_patient, self.ap_patient_combo)
        form.addRow(self.ap_label_staff, self.ap_staff_combo)
        form.addRow(self.ap_label_start, self.ap_start_dt)
        form.addRow(self.ap_label_end, self.ap_end_dt)
        form.addRow(self.ap_label_notes, self.ap_notes_in)
        form.addRow(self.btn_add_appt)

        self.appt_list_group = QGroupBox("")
        v = QVBoxLayout(self.appt_list_group)
        filters = QHBoxLayout()
        self.ap_filter_label_date = QLabel("")
        self.ap_filter_date = QDateEdit(QDate.currentDate()); self.ap_filter_date.setCalendarPopup(True)
        self.ap_filter_date.dateChanged.connect(self.refresh_appt_table)
        self.ap_filter_label_dept = QLabel("")
        self.ap_filter_dept = QComboBox(); self.ap_filter_dept.currentIndexChanged.connect(self.refresh_appt_table)
        self.ap_filter_label_status = QLabel("")
        self.ap_filter_status = QComboBox(); self.ap_filter_status.currentIndexChanged.connect(self.refresh_appt_table)

        filters.addWidget(self.ap_filter_label_date); filters.addWidget(self.ap_filter_date)
        filters.addWidget(self.ap_filter_label_dept); filters.addWidget(self.ap_filter_dept)
        filters.addWidget(self.ap_filter_label_status); filters.addWidget(self.ap_filter_status)
        filters.addStretch()

        self.ap_model = AppointmentsTableModel(self.appts, self)
        self.ap_proxy = ContainsFilterProxy(self)
        self.ap_proxy.setSourceModel(self.ap_model)

        self.ap_table = QTableView()
        self.ap_table.setModel(self.ap_proxy)
        self.ap_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ap_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ap_table.setAlternatingRowColors(True)
        self.ap_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ap_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ap_table.customContextMenuRequested.connect(self.on_appt_context)
        self.ap_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ap_table.setSortingEnabled(True)
        self.restore_header_state(self.ap_table, "appts_header_state")

        buttons_row = QHBoxLayout()
        self.btn_appt_status = QPushButton("")
        self.btn_appt_status.clicked.connect(self.handle_change_appt_status)
        self.btn_appt_delete = QPushButton("")
        self.btn_appt_delete.clicked.connect(self.handle_delete_appt)
        self.btn_a_refresh = QPushButton("")
        self.btn_a_refresh.clicked.connect(self.refresh_appt_table)
        buttons_row.addWidget(self.btn_appt_status); buttons_row.addWidget(self.btn_appt_delete); buttons_row.addWidget(self.btn_a_refresh); buttons_row.addStretch()

        v.addLayout(filters)
        v.addWidget(self.ap_table, 1)
        v.addLayout(buttons_row)

        layout.addWidget(self.create_appt_group)
        layout.addWidget(self.appt_list_group, 1)

        # Empty overlay for appointments table
        self.ap_empty = QLabel(self.ap_table.viewport())
        self.ap_empty.setAlignment(Qt.AlignCenter)
        self.ap_empty.setStyleSheet("color: #888;")
        self.ap_empty.hide()

        self.tab_idx_appts = self.tabs.addTab(tab, "")

        self._fill_dept_combos()
        self._ap_on_dept_changed()
        self._fill_appt_filter_combos()
        self.refresh_appt_table()

    # ---------- Context: appointments ----------
    def on_appt_context(self, pos):
        idxs = self.ap_table.selectionModel().selectedRows()
        if not idxs: return
        menu = QMenu(self)
        a_status = menu.addAction(I18N.t("btn.change_status"))
        a_delete = menu.addAction(I18N.t("btn.delete_appt"))
        a_copy_id = menu.addAction("Copy ID")
        a_copy_time = menu.addAction("Copy timeslot")
        act = menu.exec(self.ap_table.viewport().mapToGlobal(pos))
        if not act: return
        appts = [self.ap_proxy.index(i.row(),0).data(Qt.UserRole) for i in idxs]
        if act == a_status and len(appts)==1:
            self.handle_change_appt_status()
        elif act == a_delete:
            self.handle_delete_appt()
        elif act == a_copy_id and len(appts)==1:
            QApplication.clipboard().setText(appts[0].id)
        elif act == a_copy_time and len(appts)==1:
            a = appts[0]
            QApplication.clipboard().setText(f"{fmt_dt(a.start)} -> {fmt_dt(a.end)}")

    # ---------- General helpers ----------
    def retranslate_ui(self):
        # Tabs
        self.tabs.setTabText(self.tab_idx_dashboard, I18N.t("tab.dashboard"))
        self.tabs.setTabText(self.tab_idx_patients, I18N.t("tab.patients"))
        self.tabs.setTabText(self.tab_idx_staff, I18N.t("tab.staff"))
        self.tabs.setTabText(self.tab_idx_search, I18N.t("tab.search"))
        self.tabs.setTabText(self.tab_idx_appts, I18N.t("tab.appointments"))
        # Left
        self.lbl_depts.setText(I18N.t("label.departments"))
        self.add_dept_group.setTitle(I18N.t("group.add_dept"))
        self.add_dept_form_label_name.setText(I18N.t("field.name"))
        self.add_dept_form_label_cap.setText(I18N.t("field.capacity"))
        self.btn_add_dept.setText(I18N.t("btn.add"))
        # Info
        self.info_group.setTitle(I18N.t("group.dept_info"))
        self.info_label_name.setText(I18N.t("label.name:"))
        self.info_label_code.setText(I18N.t("label.code:"))
        self.info_label_cap.setText(I18N.t("label.capacity:"))
        self.info_label_patcnt.setText(I18N.t("label.patients_count:"))
        self.info_label_staffcnt.setText(I18N.t("label.staff_count:"))
        # Patients tab
        self.add_patient_group.setTitle(I18N.t("group.add_patient"))
        self.add_patient_label_name.setText(I18N.t("field.name"))
        self.add_patient_label_age.setText(I18N.t("field.age"))
        self.add_patient_label_med.setText(I18N.t("field.medical_record"))
        self.p_med_rec_in.setPlaceholderText(I18N.t("ph.medical_record"))
        self.btn_add_patient.setText(I18N.t("btn.add_patient"))
        # Staff tab
        self.add_staff_group.setTitle(I18N.t("group.add_staff"))
        self.add_staff_label_name.setText(I18N.t("field.name"))
        self.add_staff_label_age.setText(I18N.t("field.age"))
        self.add_staff_label_pos.setText(I18N.t("field.position"))
        self.s_position_in.setPlaceholderText(I18N.t("ph.position_hint"))
        self.btn_add_staff.setText(I18N.t("btn.add_staff"))
        # Search tab
        self.search_group.setTitle(I18N.t("group.search"))
        self.search_label_term.setText(I18N.t("search.field.label"))
        self.search_all_in.setPlaceholderText(I18N.t("ph.search_all"))
        self.search_mode_pat.setText(I18N.t("search.mode.patients"))
        self.search_mode_stf.setText(I18N.t("search.mode.staff"))
        self.lbl_pat_status.setText(I18N.t("filter.pat_status"))
        self.lbl_age_min.setText(I18N.t("filter.age_min"))
        self.lbl_age_max.setText(I18N.t("filter.age_max"))
        self.lbl_staff_status.setText(I18N.t("filter.staff_status"))
        self.lbl_staff_pos.setText(I18N.t("field.position"))
        self.lbl_results_count.setText(I18N.t("label.results_count", n=self.search_results.count()))
        # Appointments tab
        self.create_appt_group.setTitle(I18N.t("group.create_appt"))
        self.ap_label_dept.setText(I18N.t("field.dept"))
        self.ap_label_patient.setText(I18N.t("field.patient"))
        self.ap_label_staff.setText(I18N.t("field.staff"))
        self.ap_label_start.setText(I18N.t("field.start"))
        self.ap_label_end.setText(I18N.t("field.end"))
        self.ap_label_notes.setText(I18N.t("field.notes"))
        self.btn_add_appt.setText(I18N.t("btn.add_appt"))
        # Appt list
        self.appt_list_group.setTitle(I18N.t("group.appt_list"))
        self.ap_filter_label_date.setText(I18N.t("filter.date"))
        self.ap_filter_label_dept.setText(I18N.t("filter.dept"))
        self.ap_filter_label_status.setText(I18N.t("filter.status"))
        self.btn_appt_status.setText(I18N.t("btn.change_status"))
        self.btn_appt_delete.setText(I18N.t("btn.delete_appt"))
        self.btn_a_refresh.setText(I18N.t("btn.refresh"))

        # Dashboard
        self.dash_group_stats.setTitle(I18N.t("dash.stats"))
        self.dash_label_total_depts.setText(I18N.t("dash.total_depts"))
        self.dash_label_total_patients.setText(I18N.t("dash.total_patients"))
        self.dash_label_active_patients.setText(I18N.t("dash.active_patients"))
        self.dash_label_total_staff.setText(I18N.t("dash.total_staff"))
        self.dash_label_appts_today.setText(I18N.t("dash.appts_today"))
        self.btn_dash_refresh.setText(I18N.t("dash.refresh"))
        self.dash_group_chart.setTitle(I18N.t("dash.chart.appts_by_status"))
        if not HAS_QTCHARTS:
            self.dash_chart_placeholder.setText(I18N.t("dash.no_qtcharts"))

        # Header updates
        self.p_model.headerDataChanged.emit(Qt.Horizontal, 0, self.p_model.columnCount()-1)
        self.s_model.headerDataChanged.emit(Qt.Horizontal, 0, self.s_model.columnCount()-1)
        self.ap_model.headerDataChanged.emit(Qt.Horizontal, 0, self.ap_model.columnCount()-1)

        # Refresh bound data
        self.refresh_department_list()
        self.refresh_patients_table_related()
        self.s_model.layoutChanged.emit()
        self._fill_dept_combos()
        self._ap_on_dept_changed()
        self._fill_appt_filter_combos()
        self.refresh_appt_table()
        self.refresh_dashboard()
        self.update_empty_overlays()

    def _on_lang(self, lang: str):
        self.setLayoutDirection(Qt.RightToLeft if lang == "ar" else Qt.LeftToRight)
        self.retranslate_ui()

    # ---------- Departments list & info ----------
    def refresh_department_list(self):
        self.dept_list.clear()
        for name, dept in self.hospital.departments.items():
            it = QListWidgetItem(name)
            it.setData(Qt.UserRole, dept)
            self.dept_list.addItem(it)
        if self.dept_list.count() > 0 and self.dept_list.currentRow() == -1:
            self.dept_list.setCurrentRow(0)

    def current_department(self) -> Optional[Department]:
        it = self.dept_list.currentItem()
        return it.data(Qt.UserRole) if it else None

    def on_dept_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        dept = self.current_department()
        self.p_model.set_department(dept)
        self.s_model.set_department(dept)
        self.update_dept_info()
        self._ap_on_dept_changed()
        self.refresh_appt_table()
        self.update_empty_overlays()

    def update_dept_info(self):
        dept = self.current_department()
        if not dept:
            self.lbl_dept_name.setText("-"); self.lbl_dept_code.setText("-")
            self.lbl_dept_capacity.setText("-"); self.lbl_patients_count.setText("-"); self.lbl_staff_count.setText("-")
            return
        self.lbl_dept_name.setText(dept.name)
        self.lbl_dept_code.setText(dept.dept_code)
        self.lbl_dept_capacity.setText(str(dept.capacity))
        self.lbl_patients_count.setText(f"{len(dept.patients)} ({I18N.t('chk.only_active')}: {len(dept.get_active_patients())})")
        self.lbl_staff_count.setText(str(len(dept.staff)))

    # ---------- Toolbar glue ----------
    def set_global_filter(self, text: str):
        re = text
        current = self.tabs.currentIndex()
        if current == self.tab_idx_patients:
            self.p_proxy.setFilterRegularExpression(re)
        elif current == self.tab_idx_staff:
            self.s_proxy.setFilterRegularExpression(re)
        elif current == self.tab_idx_appts:
            self.ap_proxy.setFilterRegularExpression(re)

    def quick_add_patient(self):
        self.tabs.setCurrentIndex(self.tab_idx_patients)
        self.p_name_in.setFocus()

    def quick_add_appointment(self):
        self.tabs.setCurrentIndex(self.tab_idx_appts)
        self.ap_notes_in.setFocus()

    def refresh_all(self):
        self.refresh_department_list()
        self.update_dept_info()
        self.refresh_dashboard()
        self.refresh_appt_table()
        self.p_model.layoutChanged.emit()
        self.s_model.layoutChanged.emit()
        self.update_empty_overlays()

    # ---------- Validation helpers ----------
    def set_invalid(self, widget: QWidget, msg: str):
        widget.setStyleSheet("border: 1px solid #d9534f;")
        widget.setToolTip(msg)

    def clear_invalid(self, widget: QWidget):
        widget.setStyleSheet("")
        widget.setToolTip("")

    # ---------- Export helpers ----------
    def export_patients_csv(self, all_depts: bool):
        path, _ = QFileDialog.getSaveFileName(self, I18N.t("dialog.export.csv.title"),
                                              "patients.csv", I18N.t("dialog.csv.filter"))
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            rows = []
            if all_depts:
                for d in self.hospital.departments.values():
                    for p in d.patients:
                        rows.append([d.name, p.patient_id, p.name, p.age,
                                     I18N.t("status.discharged") if p.is_discharged else I18N.t("status.admitted"),
                                     fmt_dt(getattr(p, "admission_date", None))])
            else:
                d = self.current_department()
                if not d:
                    QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_department_first"))
                    return
                for p in d.patients:
                    rows.append([d.name, p.patient_id, p.name, p.age,
                                 I18N.t("status.discharged") if p.is_discharged else I18N.t("status.admitted"),
                                 fmt_dt(getattr(p, "admission_date", None))])
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Department", "Patient ID", "Name", "Age", "Status", "Admission"])
                w.writerows(rows)
            self.win.statusBar().showMessage(I18N.t("msg.export.ok"), 3000)
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.export.fail", err=e))

    def export_staff_csv(self, all_depts: bool):
        path, _ = QFileDialog.getSaveFileName(self, I18N.t("dialog.export.csv.title"),
                                              "staff.csv", I18N.t("dialog.csv.filter"))
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            rows = []
            if all_depts:
                for d in self.hospital.departments.values():
                    for s in d.staff:
                        rows.append([d.name, s.staff_id, s.name, s.age, s.position,
                                     I18N.t("staff.active") if s.is_active else I18N.t("staff.inactive")])
            else:
                d = self.current_department()
                if not d:
                    QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_department_first"))
                    return
                for s in d.staff:
                    rows.append([d.name, s.staff_id, s.name, s.age, s.position,
                                 I18N.t("staff.active") if s.is_active else I18N.t("staff.inactive")])
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Department", "Staff ID", "Name", "Age", "Position", "Status"])
                w.writerows(rows)
            self.win.statusBar().showMessage(I18N.t("msg.export.ok"), 3000)
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.export.fail", err=e))

    def export_appts_csv_filtered(self):
        path, _ = QFileDialog.getSaveFileName(self, I18N.t("dialog.export.csv.title"),
                                              "appointments.csv", I18N.t("dialog.csv.filter"))
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            rows = []
            for r in range(self.ap_proxy.rowCount()):
                a: Appointment = self.ap_proxy.index(r, 0).data(Qt.UserRole)
                p = self.appts.patient_of(a)
                s = self.appts.staff_of(a)
                rows.append([
                    a.id, a.dept_name,
                    (p.patient_id if p else ""), (p.name if p else ""),
                    (s.staff_id if s else ""), (s.name if s else ""),
                    fmt_dt(a.start), fmt_dt(a.end),
                    AppointmentStatus.label(a.status), a.notes
                ])
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#", "Department", "Patient ID", "Patient Name", "Staff ID", "Staff Name",
                            "Start", "End", "Status", "Notes"])
                w.writerows(rows)
            self.win.statusBar().showMessage(I18N.t("msg.export.ok"), 3000)
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), I18N.t("msg.export.fail", err=e))

    # ---------- Departments ops ----------
    def handle_add_department(self):
        name = self.dept_name_in.text().strip()
        cap = int(self.dept_cap_in.value())
        if not name:
            self.set_invalid(self.dept_name_in, I18N.t("msg.dept.name_required"))
            self.win.statusBar().showMessage(I18N.t("msg.validation.fix_fields"), 3000)
            return
        try:
            if name in self.hospital.departments:
                raise ValueError(f"Department {name} already exists")
            d = Department(name, cap)
            self.hospital.departments[name] = d
            self.dept_name_in.clear(); self.dept_cap_in.setValue(50)
            self.refresh_department_list()
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("btn.add") + " ✓")
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), str(e))

    # ---------- Patients ops ----------
    def handle_add_patient(self):
        dept = self.current_department()
        if not dept:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_department_first")); return
        name = self.p_name_in.text().strip()
        age = int(self.p_age_in.value())
        med = self.p_med_rec_in.toPlainText().strip()
        if not name:
            self.set_invalid(self.p_name_in, I18N.t("msg.patient.name_required"))
            self.win.statusBar().showMessage(I18N.t("msg.validation.fix_fields"), 3000)
            return
        try:
            patient = Patient(name, age, med)
            if len(dept.patients) >= dept.capacity:
                QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.dept.full", name=name)); return
            dept.patients.append(patient)
            self.p_name_in.clear(); self.p_age_in.setValue(1); self.p_med_rec_in.clear()
            self.refresh_patients_table_related()
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.patient.added", pid=patient.patient_id))
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), str(e))

    # ---------- Staff ops ----------
    def handle_add_staff(self):
        dept = self.current_department()
        if not dept:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_department_first")); return
        name = self.s_name_in.text().strip()
        age = int(self.s_age_in.value())
        position = self.s_position_in.text().strip()
        bad = False
        if not name:
            self.set_invalid(self.s_name_in, I18N.t("msg.staff.name_position_required"))
            bad = True
        if not position:
            self.set_invalid(self.s_position_in, I18N.t("msg.staff.name_position_required"))
            bad = True
        if bad:
            self.win.statusBar().showMessage(I18N.t("msg.validation.fix_fields"), 3000)
            return
        try:
            staff = Staff(name, age, position, dept.name)
            dept.staff.append(staff)
            self.s_name_in.clear(); self.s_age_in.setValue(18); self.s_position_in.clear()
            self.s_model.layoutChanged.emit()
            self.refresh_dashboard()
            self.update_empty_overlays()
            QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.staff.added", sid=staff.staff_id))
        except Exception as e:
            QMessageBox.critical(self, I18N.t("msg.error.title"), str(e))

    # ---------- Search ----------
    def handle_search_all(self):
        term = self.search_all_in.text().strip().lower()
        self.search_results.clear()
        mode_patients = self.search_mode_pat.isChecked()
        if mode_patients:
            status_filter = self.cb_pat_status.currentData()
            age_min = self.spin_age_min.value()
            age_max = self.spin_age_max.value()
            for dept in self.hospital.departments.values():
                for p in dept.patients:
                    if term and (term not in f"{p.name} {p.patient_id}".lower()):
                        continue
                    if status_filter == "admitted" and p.is_discharged:
                        continue
                    if status_filter == "discharged" and not p.is_discharged:
                        continue
                    if not (age_min <= p.age <= age_max):
                        continue
                    status = I18N.t("status.admitted") if not p.is_discharged else I18N.t("status.discharged")
                    it = QListWidgetItem(f"[{dept.name}] {p.patient_id} | {p.name} | {status}")
                    it.setData(Qt.UserRole, (dept, p))
                    self.search_results.addItem(it)
        else:
            st_filter = self.cb_staff_status.currentData()
            pos_term = self.in_staff_pos.text().strip().lower()
            for dept in self.hospital.departments.values():
                for s in dept.staff:
                    if term and (term not in f"{s.name} {s.staff_id}".lower()):
                        continue
                    if st_filter == "active" and not s.is_active:
                        continue
                    if st_filter == "inactive" and s.is_active:
                        continue
                    if pos_term and (pos_term not in s.position.lower()):
                        continue
                    it = QListWidgetItem(f"[{dept.name}] {s.staff_id} | {s.name} | {s.position} | " +
                                         (I18N.t("staff.active") if s.is_active else I18N.t("staff.inactive")))
                    it.setData(Qt.UserRole, (dept, s))
                    self.search_results.addItem(it)
        self.lbl_results_count.setText(I18N.t("label.results_count", n=self.search_results.count()))

    def handle_search_navigate(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data: return
        dept, obj = data
        for i in range(self.dept_list.count()):
            if self.dept_list.item(i).data(Qt.UserRole) is dept:
                self.dept_list.setCurrentRow(i)
                break
        if isinstance(obj, Patient):
            self.tabs.setCurrentIndex(self.tab_idx_patients)
            model = self.p_model
            if model.dept is dept:
                for r, p in enumerate(dept.patients):
                    if p is obj:
                        src_idx = self.p_model.index(r, 0)
                        proxy_idx = self.p_proxy.mapFromSource(src_idx)
                        if proxy_idx.isValid():
                            self.p_table.selectRow(proxy_idx.row())
                        break
        else:
            self.tabs.setCurrentIndex(self.tab_idx_staff)
            model = self.s_model
            if model.dept is dept:
                for r, s in enumerate(dept.staff):
                    if s is obj:
                        src_idx = self.s_model.index(r, 0)
                        proxy_idx = self.s_proxy.mapFromSource(src_idx)
                        if proxy_idx.isValid():
                            self.s_table.selectRow(proxy_idx.row())
                        break

    # ---------- Appointments helpers ----------
    def _fill_dept_combos(self):
        self.ap_dept_combo.blockSignals(True)
        self.ap_dept_combo.clear()
        for d in self.hospital.departments.values():
            self.ap_dept_combo.addItem(d.name, d)
        self.ap_dept_combo.blockSignals(False)

    def _ap_on_dept_changed(self):
        dept = self.ap_dept_combo.currentData()
        self.ap_patient_combo.clear(); self.ap_staff_combo.clear()
        if not dept: return
        for p in dept.patients:
            self.ap_patient_combo.addItem(f"{p.patient_id} - {p.name}", p)
        for s in dept.staff:
            if s.is_active:
                self.ap_staff_combo.addItem(f"{s.staff_id} - {s.name} ({s.position})", s)

    def _fill_appt_filter_combos(self):
        self.ap_filter_dept.blockSignals(True)
        self.ap_filter_status.blockSignals(True)
        self.ap_filter_dept.clear(); self.ap_filter_status.clear()
        self.ap_filter_dept.addItem(I18N.t("filter.all"), "__ALL__")
        for d in self.hospital.departments.values():
            self.ap_filter_dept.addItem(d.name, d.name)
        self.ap_filter_status.addItem(I18N.t("filter.all"), "__ALL__")
        for s in AppointmentStatus.all():
            self.ap_filter_status.addItem(AppointmentStatus.label(s), s)
        self.ap_filter_dept.blockSignals(False)
        self.ap_filter_status.blockSignals(False)

    def handle_add_appointment(self):
        dept: Department = self.ap_dept_combo.currentData()
        if not dept:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_dept")); return
        p: Patient = self.ap_patient_combo.currentData()
        s: Optional[Staff] = self.ap_staff_combo.currentData()
        if not p:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_patient_for_appt")); return

        def to_py(dt: QDateTime) -> datetime:
            try:
                return dt.toPython()
            except Exception:
                return datetime.fromtimestamp(dt.toSecsSinceEpoch())

        start = to_py(self.ap_start_dt.dateTime())
        end = to_py(self.ap_end_dt.dateTime())
        if end <= start:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.end_after_start")); return

        conflicts = self.appts.find_conflicts(p.id, (s.id if s else None), start, end)
        if conflicts:
            details = []
            for a, reasons in conflicts:
                who = []
                if "patient" in reasons: who.append(I18N.t("who.patient"))
                if "staff" in reasons: who.append(I18N.t("who.staff"))
                joiner = " & " if I18N.lang=="en" else " و "
                who_s = joiner.join(who)
                details.append(I18N.t("msg.appt.conflict.row", id=a.id, dept=a.dept_name,
                                       start=fmt_dt(a.start, time_only=True), end=fmt_dt(a.end, time_only=True), who=who_s))
            QMessageBox.critical(self, I18N.t("msg.appt.conflict.title"),
                                 I18N.t("msg.appt.conflict.body", details="\n".join(details)))
            return

        a = self.appts.add(p, dept, start, end, s, self.ap_notes_in.text().strip())
        self.ap_notes_in.clear()
        self.refresh_appt_table()
        self.refresh_dashboard()
        QMessageBox.information(self, I18N.t("msg.info.title"), I18N.t("msg.appt.created", id=a.id))

    def refresh_appt_table(self):
        if hasattr(self.ap_filter_date.date(), "toPython"):
            day = self.ap_filter_date.date().toPython()
        else:
            d = self.ap_filter_date.date()
            day = date(d.year(), d.month(), d.day())
        dept_name = self.ap_filter_dept.currentData() if self.ap_filter_dept.count() else "__ALL__"
        status = self.ap_filter_status.currentData() if self.ap_filter_status.count() else "__ALL__"
        items = self.appts.list_filtered(day=day, dept_name=dept_name, status=status)
        self.ap_model.set_items(items)
        self.update_empty_overlays()

    def _current_selected_appt(self) -> Optional[Appointment]:
        idx = self.ap_table.selectionModel().currentIndex()
        if not idx.isValid(): return None
        return self.ap_proxy.index(idx.row(), 0).data(Qt.UserRole)

    def _confirm_delete_appts_if_needed(self, count: int) -> bool:
        s = QSettings("HospitalApp", "UI")
        ask = s.value("confirm_delete_appt", "yes")
        if str(ask) != "no":
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(I18N.t("confirm.delete_appt.title"))
            box.setText(I18N.t("confirm.delete_appt.body", n=count))
            cb = QCheckBox(I18N.t("chk.dont_ask_again"), box)
            box.setCheckBox(cb)
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            res = box.exec()
            if res != QMessageBox.Yes:
                return False
            if cb.isChecked():
                s.setValue("confirm_delete_appt", "no")
        return True

    def handle_change_appt_status(self):
        a = self._current_selected_appt()
        if not a:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_appt")); return
        choices = [AppointmentStatus.label(s) for s in AppointmentStatus.all()]
        current_label = AppointmentStatus.label(a.status)
        label, ok = QInputDialog.getItem(self, I18N.t("dialog.change_status.title"),
                                         I18N.t("dialog.change_status.prompt"),
                                         choices, choices.index(current_label) if current_label in choices else 0, False)
        if not ok: return
        new_status = AppointmentStatus.from_label(label)
        self.appts.update_status(a.id, new_status)
        self.refresh_appt_table()
        self.refresh_dashboard()

    def handle_delete_appt(self):
        idxs = self.ap_table.selectionModel().selectedRows()
        if not idxs:
            QMessageBox.warning(self, I18N.t("msg.warning.title"), I18N.t("msg.select_appt")); return
        if not self._confirm_delete_appts_if_needed(len(idxs)):
            return
        for i in idxs:
            a = self.ap_proxy.index(i.row(), 0).data(Qt.UserRole)
            self.appts.remove(a.id)
        self.refresh_appt_table()
        self.refresh_dashboard()

    # ---------- Empty states ----------
    def update_empty_overlays(self):
        # Patients table
        rect = self.p_table.viewport().rect()
        self.p_empty.setGeometry(rect)
        dept = self.current_department()
        if not dept:
            self.p_empty.setText(I18N.t("empty.no_dept"))
            self.p_empty.show()
        elif self.p_model.rowCount() == 0:
            self.p_empty.setText(I18N.t("empty.patients"))
            self.p_empty.show()
        else:
            self.p_empty.hide()

        # Staff table
        rects = self.s_table.viewport().rect()
        self.s_empty.setGeometry(rects)
        if not dept:
            self.s_empty.setText(I18N.t("empty.no_dept"))
            self.s_empty.show()
        elif self.s_model.rowCount() == 0:
            self.s_empty.setText(I18N.t("empty.staff"))
            self.s_empty.show()
        else:
            self.s_empty.hide()

        # Appointments table
        recta = self.ap_table.viewport().rect()
        self.ap_empty.setGeometry(recta)
        if self.ap_model.rowCount() == 0:
            self.ap_empty.setText(I18N.t("empty.appts"))
            self.ap_empty.show()
        else:
            self.ap_empty.hide()

    # ---------- Layout persistence ----------
    def save_layouts(self):
        self.save_header_state(self.p_table, "patients_header_state")
        self.save_header_state(self.s_table, "staff_header_state")
        self.save_header_state(self.ap_table, "appts_header_state")
        self.save_splitter_state(self.splitter, "main_splitter_state")

    def save_header_state(self, table: QTableView, key: str):
        s = QSettings("HospitalApp", "UI")
        state = table.horizontalHeader().saveState()
        s.setValue(key, state)

    def restore_header_state(self, table: QTableView, key: str):
        s = QSettings("HospitalApp", "UI")
        state = s.value(key)
        if isinstance(state, QByteArray):
            table.horizontalHeader().restoreState(state)

    def save_splitter_state(self, splitter: QSplitter, key: str):
        s = QSettings("HospitalApp", "UI")
        s.setValue(key, splitter.saveState())

    def restore_splitter_state(self, splitter: QSplitter, key: str):
        s = QSettings("HospitalApp", "UI")
        state = s.value(key)
        if isinstance(state, QByteArray):
            splitter.restoreState(state)


# ================= main =================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set initial locale based on stored language
    if I18N.lang == "ar":
        QLocale.setDefault(QLocale(QLocale.Arabic))
    else:
        QLocale.setDefault(QLocale(QLocale.English))

    I18N.set_language(I18N.lang)
    THEME.apply(app)

    hospital = Hospital("City General Hospital", "123 Main St")
    cardio = hospital.find_department("Cardiology")
    if cardio:
        try:
            p1 = Patient("Alice Johnson", 35, "Hypertension monitoring")
            p2 = Patient("Bob Smith", 52, "Post-operative care")
            cardio.patients.extend([p1, p2])
            cardio.staff.append(Staff("Dr. Sarah Miller", 42, "Cardiologist", "Cardiology"))
            cardio.staff.append(Staff("Emma Wilson", 28, "Head Nurse", "Cardiology"))
        except Exception:
            pass

    window = HospitalWindow(hospital)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()