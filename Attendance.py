import sys
from datetime import timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout,
    QHBoxLayout, QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QColor

import mainsyslogics


# ---------------- Date Picker Dialog ----------------
class DatePickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Week Start Date")
        self.resize(320, 180)

        self.setStyleSheet("""
            QDialog {
                background-color: rgb(31, 158, 37);
            }
            QLabel {
                color: aliceblue;
                font-size: 13px;
            }
            QDateEdit {
                background-color: #43B64D;
                color: aliceblue;
                border: 1px solid #43B64D;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton {
                background-color: #43B64D;
                color: aliceblue;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #53E15F;
                color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Select the start date for this attendance week:")
        layout.addWidget(label)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_edit)

        self.end_date_label = QLabel()
        layout.addWidget(self.end_date_label)
        self.date_edit.dateChanged.connect(self.update_end_date)
        self.update_end_date(self.date_edit.date())

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def update_end_date(self, start_date: QDate):
        end_date = start_date.addDays(6)
        self.end_date_label.setText(
            f"<b>Week Period:</b> {start_date.toString('yyyy-MM-dd')} → {end_date.toString('yyyy-MM-dd')}"
        )

    def get_selected_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")


# ---------------- Attendance Detail Window ----------------
class AttendanceDetailWindow(QDialog):
    def __init__(self, week_start, week_end, companyName, role, status='draft', parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Attendance for {week_start}")
        self.setModal(True)
        self.resize(1200, 650)

        self.week_start = week_start
        self.week_end = week_end
        self.companyName = companyName
        self.status = status
        self.role = role

        self.setStyleSheet("""
            QDialog {
                background-color: #2A7230;
            }
            QLabel {
                color: white;
            }
            QTableWidget {
                background-color: #345e3d;
                color: white;
                gridline-color: #7f8c8d;
                border: 1px solid #7f8c8d;
            }
            QTableWidget::item {
                color: white;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: white;
                padding: 8px;
                border: 1px solid #16a085;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel(f"<h2>Attendance for Week: {week_start} → {week_end}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        if status == 'approved':
            status_label = QLabel("<b style='color: #2ecc71;'>✓ APPROVED (Read-Only)</b>")
        elif status == 'pending':
            status_label = QLabel("<b style='color: #f39c12;'>⏳ PENDING APPROVAL</b>")
        else:
            status_label = QLabel("<b style='color: #f1c40f;'>DRAFT (Editable)</b>")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        self.table = QTableWidget()
        if status in ['approved', 'pending']:
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        # Staff buttons (draft status)
        if status == 'draft' and role == 'staff':
            self.save_draft_btn = QPushButton("Save as Draft")
            self.save_draft_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #7f8c8d; }
            """)

            self.submit_btn = QPushButton("Submit for Approval")
            self.submit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #229954; }
            """)

            self.save_draft_btn.clicked.connect(lambda: self.save_attendance('draft'))
            self.submit_btn.clicked.connect(lambda: self.save_attendance('pending'))

            button_layout.addWidget(self.save_draft_btn)
            button_layout.addWidget(self.submit_btn)

        # Admin buttons (pending status)
        elif status == 'pending' and role == 'admin':
            self.approve_btn = QPushButton("✓ Approve Attendance")
            self.approve_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #229954; }
            """)

            self.reject_btn = QPushButton("✗ Reject Attendance")
            self.reject_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #d35400; }
            """)

            self.approve_btn.clicked.connect(self.approve_attendance)
            self.reject_btn.clicked.connect(self.reject_attendance)

            button_layout.addWidget(self.approve_btn)
            button_layout.addWidget(self.reject_btn)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.load_employee_attendance()

    def load_employee_attendance(self):
        """Load attendance data from database"""
        try:
            attendance_data = mainsyslogics.Connectdb.get_attendance_for_week(
                self.companyName, self.week_start, self.week_end
            )

            if not attendance_data:
                QMessageBox.warning(self, "No Data", "No employees found or attendance not initialized.")
                return

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Total", "Deductions"]
            self.table.setColumnCount(len(days) + 2)
            self.table.setHorizontalHeaderLabels(["ID", "Employee Name"] + days)
            self.table.setColumnHidden(0, True)
            self.table.setRowCount(len(attendance_data))

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

            for row_idx, emp_data in enumerate(attendance_data):
                employee_id = emp_data['employee_id']
                employee_name = emp_data['employee_name']

                id_item = QTableWidgetItem(str(employee_id))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 0, id_item)

                name_item = QTableWidgetItem(employee_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 1, name_item)

                day_keys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for col_idx, day_key in enumerate(day_keys):
                    value = float(emp_data.get(day_key, 0) or 0)
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx + 2, item)

                total = sum(float(emp_data.get(d, 0) or 0) for d in day_keys)
                total_item = QTableWidgetItem(str(total))
                total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                total_item.setBackground(QColor(52, 73, 94))
                self.table.setItem(row_idx, 9, total_item)

                deductions = mainsyslogics.Connectdb.get_employee_deductions_summary(employee_id)
                deductions_item = QTableWidgetItem(f"₱{deductions:,.2f}")
                deductions_item.setFlags(deductions_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                deductions_item.setBackground(QColor(231, 76, 60))
                self.table.setItem(row_idx, 10, deductions_item)

            self.table.cellChanged.connect(self.update_row_total)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load attendance data: {e}")
            print(f"❌ Error loading attendance: {e}")

    def update_row_total(self, row, col):
        """Recalculate total when a day cell is edited"""
        if 2 <= col <= 8:
            total = 0
            for c in range(2, 9):
                try:
                    value = float(self.table.item(row, c).text() or 0)
                    total += value
                except (ValueError, AttributeError):
                    pass

            total_item = self.table.item(row, 9)
            if total_item:
                total_item.setText(str(total))

    def save_attendance(self, status):
        """Save attendance data to database"""
        try:
            attendance_data = {}

            for row in range(self.table.rowCount()):
                employee_id = int(self.table.item(row, 0).text())

                hours = {
                    'monday': float(self.table.item(row, 2).text() or 0),
                    'tuesday': float(self.table.item(row, 3).text() or 0),
                    'wednesday': float(self.table.item(row, 4).text() or 0),
                    'thursday': float(self.table.item(row, 5).text() or 0),
                    'friday': float(self.table.item(row, 6).text() or 0),
                    'saturday': float(self.table.item(row, 7).text() or 0),
                    'sunday': float(self.table.item(row, 8).text() or 0)
                }

                attendance_data[employee_id] = hours

            success = mainsyslogics.Connectdb.save_attendance_for_week(
                self.companyName,
                self.week_start,
                self.week_end,
                attendance_data,
                status
            )

            if success:
                status_text = "Draft saved" if status == 'draft' else "Submitted for approval"
                QMessageBox.information(self, "Success", f"{status_text} successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save attendance.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving attendance: {e}")
            print(f"❌ Error saving attendance: {e}")

    def approve_attendance(self):
        """Admin approves attendance and creates payroll"""
        reply = QMessageBox.question(
            self,
            "Approve Attendance",
            "Are you sure you want to approve this attendance?\n\nThis will generate payroll for this week.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Update attendance status to approved
                success = mainsyslogics.Connectdb.approve_attendance(
                    self.companyName,
                    self.week_start,
                    self.week_end
                )

                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        "Attendance approved successfully!\nPayroll has been generated."
                    )
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to approve attendance.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error approving attendance: {e}")
                print(f"❌ Error approving: {e}")

    def reject_attendance(self):
        """Admin rejects attendance and sends it back to draft"""
        reply = QMessageBox.question(
            self,
            "Reject Attendance",
            "Are you sure you want to reject this attendance?\n\nIt will be sent back to draft status.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = mainsyslogics.Connectdb.reject_attendance(
                    self.companyName,
                    self.week_start,
                    self.week_end
                )

                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        "Attendance rejected. Status changed to draft."
                    )
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to reject attendance.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error rejecting attendance: {e}")


# ---------------- Attendance Card ----------------
class AttendanceCard(QFrame):
    def __init__(self, week_start, week_end, summary, status, companyName, role, parent=None):
        super().__init__(parent)
        self.week_start = week_start
        self.week_end = week_end
        self.companyName = companyName
        self.status = status
        self.role = role
        self.parent_window = parent
        self.setFixedHeight(80)

        if status == 'approved':
            bg_color = "#27ae60"
            status_text = "APPROVED"
        elif status == 'pending':
            bg_color = "#f39c12"
            status_text = "PENDING"
        else:
            bg_color = "#2A7230"
            status_text = "DRAFT"

        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid #1e4722;
                border-radius: 25px;
                background-color: {bg_color};
                color: white;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        week_label = QLabel(f"<b>{week_start}</b>")
        week_label.setStyleSheet("font-size: 16px; color: white;")

        status_label = QLabel(f"[{status_text}]")
        status_label.setStyleSheet("font-size: 12px; color: white;")

        summary_label = QLabel(summary)
        summary_label.setStyleSheet("font-size: 13px; color: white;")

        layout.addWidget(week_label)
        layout.addWidget(status_label)
        layout.addStretch()
        layout.addWidget(summary_label)

        self.button = QPushButton("", self)
        self.button.setFlat(True)
        self.button.setStyleSheet("background: transparent;")
        self.button.clicked.connect(self.open_detail)

    def resizeEvent(self, event):
        self.button.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def open_detail(self):
        self.detail_window = AttendanceDetailWindow(
            self.week_start,
            self.week_end,
            self.companyName,
            self.role,
            status=self.status,
            parent=self.parent_window
        )
        if self.detail_window.exec() == QDialog.DialogCode.Accepted:
            if self.parent_window:
                self.parent_window.refresh_attendance_list()


# ---------------- Attendance Main Window ----------------
class AttendanceWindow(QWidget):
    def __init__(self, role, companyName):
        super().__init__()
        self.setWindowTitle('LooTech - Attendance')
        self.setWindowIcon(QIcon())
        self.resize(900, 600)
        self.__role = role
        self.__companyName = companyName

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.body = QWidget()
        self.body_layout = QGridLayout(self.body)
        self.body.setObjectName('body')
        self.body_layout.setContentsMargins(10, 0, 10, 10)
        self.body_layout.setSpacing(10)

        label = QLabel("<h1>Attendance</h1>")
        label.setProperty('class', 'label')
        self.body_layout.addWidget(label, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.body, 1, 0, 4, 1, alignment=Qt.AlignmentFlag.AlignTop)

        self.refresh_attendance_list()

        if self.__role == 'staff':
            self.add_button = QPushButton("+", self)
            self.add_button.setFixedSize(60, 60)
            self.add_button.setStyleSheet("""
                QPushButton {
                    background-color: #43B64D;
                    color: white;
                    border-radius: 30px;
                    font-size: 28px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #005fa3; }
            """)
            self.add_button.clicked.connect(self.open_add_attendance)
            self.add_button.show()

    def refresh_attendance_list(self):
        """Refresh the list of attendance cards"""
        for i in reversed(range(self.body_layout.count())):
            if i > 0:
                widget = self.body_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

        try:
            attendance_weeks = mainsyslogics.Connectdb.get_attendance_weeks(self.__companyName)

            if not attendance_weeks:
                no_data_label = QLabel("<i>No attendance records yet.<br>Click the + button to add attendance.</i>")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_data_label.setStyleSheet("color: #7f8c8d; padding: 40px;")
                self.body_layout.addWidget(no_data_label, 1, 0, 1, 5)
                return

            row = 1
            for week_data in attendance_weeks:
                week_start = week_data['week_start'].strftime('%Y-%m-%d') if hasattr(week_data['week_start'],
                                                                                     'strftime') else str(
                    week_data['week_start'])
                week_end = week_data['week_end'].strftime('%Y-%m-%d') if hasattr(week_data['week_end'],
                                                                                 'strftime') else str(
                    week_data['week_end'])
                total_hours = float(week_data.get('total_hours', 0) or 0)
                status = week_data.get('status', 'draft')

                summary = f"{total_hours:.1f} hrs"

                card = AttendanceCard(
                    week_start,
                    week_end,
                    summary,
                    status,
                    self.__companyName,
                    self.__role,
                    parent=self
                )
                self.body_layout.addWidget(card, row, 0, 1, 5)
                row += 1

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load attendance: {e}")
            print(f"❌ Error loading attendance list: {e}")

    def open_add_attendance(self):
        """Open dialog to create new attendance week"""
        dialog = DatePickerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            start_date_str = dialog.get_selected_date()
            start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
            end_date = start_date.addDays(6)
            end_date_str = end_date.toString("yyyy-MM-dd")

            try:
                exists = mainsyslogics.Connectdb.check_attendance_week_exists(
                    self.__companyName, start_date_str, end_date_str
                )

                if exists:
                    QMessageBox.warning(
                        self,
                        "Already Exists",
                        f"Attendance for the week ({start_date_str} → {end_date_str}) already exists!"
                    )
                    return

                success = mainsyslogics.Connectdb.create_attendance_for_week(
                    self.__companyName, start_date_str, end_date_str
                )

                if not success:
                    QMessageBox.critical(self, "Error", "Failed to create attendance records.")
                    return

                self.attendance_detail = AttendanceDetailWindow(
                    start_date_str,
                    end_date_str,
                    self.__companyName,
                    self.__role,
                    status='draft',
                    parent=self
                )

                if self.attendance_detail.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_attendance_list()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create new attendance: {e}")
                print(f"❌ Error creating new attendance: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "add_button"):
            self.add_button.move(self.width() - 90, self.height() - 90)