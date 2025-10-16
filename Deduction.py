import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea,
    QFrame, QPushButton, QLineEdit, QComboBox, QFormLayout, QMessageBox,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from mainsyslogics import Connectdb
from collections import defaultdict

# optional pymysql for DictCursor if available
try:
    import pymysql
except Exception:
    pymysql = None


class DeductionWindow(QWidget):
    def __init__(self, role, companyName):
        super().__init__()
        self.setWindowTitle("LooTech - Deductions")
        try:
            self.setWindowIcon(QIcon("stylesAndPic/lootechIcon.png"))
        except Exception:
            pass
        self.resize(900, 600)
        self.__role = role
        self.__companyName = companyName
        self.add_button = None

        # UI root
        root_layout = QGridLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        body = QWidget()
        body_layout = QGridLayout(body)
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.setSpacing(10)

        title = QLabel("<h1>Deductions</h1>")
        title.setProperty('class', 'label')
        body_layout.addWidget(title, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: aliceblue; border: none;")

        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(15)
        scroll.setWidget(scroll_content)
        body_layout.addWidget(scroll, 1, 0, 1, 5)
        root_layout.addWidget(body, 0, 0)

        # floating add button for staff
        if self.__role == "staff":
            self.add_button = QPushButton("+", self)
            self.add_button.setFixedSize(60, 60)
            self.add_button.setStyleSheet("""
                QPushButton {
                    background-color: #43B64D;
                    color: white;
                    font-size: 28px;
                    border-radius: 30px;
                }
                QPushButton:hover { background-color: #2980b9; }
            """)
            self.add_button.clicked.connect(self.open_employee_selection)

        # initial load
        self.refresh_deductions()

    def resizeEvent(self, event):
        if self.add_button:
            self.add_button.move(self.width() - 80, self.height() - 80)
            self.add_button.raise_()
        super().resizeEvent(event)

    # ---------- DB fetching ----------
    def fetch_deductions_from_db(self):
        """
        Fetch only employees who have at least one deduction.
        """
        try:
            all_deductions = Connectdb.get_employees_with_deductions(self.__companyName) or []

            employees = {}
            for d in all_deductions:
                eid = d["employee_id"]
                amount = float(d.get("total_amount") or 0)
                if amount <= 0:
                    continue
                if eid not in employees:
                    employees[eid] = {
                        "employee_id": eid,
                        "name": d["name"],
                        "photo": d.get("photo_path"),
                        "deductions": [{"type": d.get("deduction_type"), "amount": amount}]
                    }
                else:
                    employees[eid]["deductions"].append({"type": d.get("deduction_type"), "amount": amount})

            # Return only employees with at least one deduction
            return list(employees.values())

        except Exception as e:
            print(f"❌ fetch_deductions_from_db failed: {e}")
            return []

    # ---------- refresh UI ----------
    def refresh_deductions(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()

        employees = self.fetch_deductions_from_db()
        cols = 5
        row, col = 0, 0

        for emp in employees:
            # Pick first deduction type to show (or customize)
            first_ded = emp["deductions"][0]
            card = self.create_card(
                emp["name"],
                first_ded["type"],
                sum(d["amount"] for d in emp["deductions"]),
                emp["photo"],
                employee_id=emp["employee_id"]
            )
            self.grid_layout.addWidget(card, row, col, alignment=Qt.AlignmentFlag.AlignTop)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    # ---------- card UI ----------
    def create_card(self, name, deduction_type, amount, photo_path=None, employee_id=None):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(120, 190)
        card.setMaximumSize(150, 220)
        card.setStyleSheet("""
            QFrame#card {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #DAEBDE;
            }
            QFrame#card:hover {
                border: 2px solid #43B64D;
                background-color: #f0f9f0;
            }
        """)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(4)
        outer.setAlignment(Qt.AlignmentFlag.AlignTop)

        pic = QLabel()
        pic.setFixedSize(64, 64)
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
        else:
            pixmap = QPixmap("stylesAndPic/profile-user.png")
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        pic.setPixmap(pixmap)
        pic.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(f"<b>{name}</b>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 13px; background-color: transparent;")

        amount_label = QLabel(f"₱{float(amount):,.2f}")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 15px; background-color: transparent;")

        desc_label = QLabel(deduction_type or "-")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; font-size: 11px; background-color: transparent;")

        outer.addWidget(pic, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(name_label)
        outer.addWidget(amount_label)
        outer.addWidget(desc_label)
        outer.addStretch(1)

        # make the card clickable
        if employee_id:
            card.mousePressEvent = lambda event: self.show_employee_deductions(employee_id)

        return card

    # ---------- popup to show deductions ----------
    def show_employee_deductions(self, employee_id):
        """Show all deductions for an employee with edit/delete options"""
        deductions = Connectdb.get_deductions_for_employee(employee_id)

        self.deduction_popup = QWidget()
        self.deduction_popup.setWindowTitle("Employee Deductions")
        self.deduction_popup.resize(500, 400)
        self.deduction_popup.setStyleSheet("""
            QWidget { 
                background: #2A7230;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton#deleteBtn {
                background-color: #e74c3c;
            }
            QPushButton#deleteBtn:hover {
                background-color: #c0392b;
            }
        """)

        layout = QVBoxLayout(self.deduction_popup)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("<h2>Deductions</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scroll area for deductions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        if not deductions:
            no_ded_label = QLabel("No deductions found for this employee.")
            no_ded_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(no_ded_label)
        else:
            for d in deductions:
                # Deduction frame
                ded_frame = QFrame()
                ded_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.1);
                        border-radius: 8px;
                        padding: 10px;
                    }
                """)
                ded_layout = QVBoxLayout(ded_frame)
                ded_layout.setSpacing(5)

                type_label = QLabel(f"<b>Type:</b> {d['deduction_type']}")
                amount_label = QLabel(f"<b>Amount:</b> ₱{float(d['total_amount']):,.2f}")
                status_label = QLabel(f"<b>Status:</b> {d['status']}")

                # Handle times_to_pay
                times_to_pay = d.get('installment_count', 0) or d.get('times_to_pay', 0)
                payments_made = d.get('payments_made', 0)

                try:
                    payments_made = int(payments_made) if payments_made != 'N/A' else 0
                except (ValueError, TypeError):
                    payments_made = 0

                if times_to_pay == 0:
                    times_text = "every payroll"
                    amount_paid = float(d.get('amount_paid', 0))
                    times_paid = int(amount_paid / float(d['total_amount'])) if float(d['total_amount']) > 0 else 0
                    times_label = QLabel(f"<b>Paid:</b> {times_paid} times ({times_text})")
                else:
                    try:
                        times_to_pay = int(times_to_pay)
                    except (ValueError, TypeError):
                        times_to_pay = 0
                    times_label = QLabel(f"<b>Progress:</b> {payments_made} of {times_to_pay} payments")

                ded_layout.addWidget(type_label)
                ded_layout.addWidget(amount_label)
                ded_layout.addWidget(status_label)
                ded_layout.addWidget(times_label)

                # Edit/Delete buttons (only for staff)
                if self.__role == "staff":
                    button_layout = QHBoxLayout()

                    edit_btn = QPushButton("✏️ Edit")
                    edit_btn.clicked.connect(lambda checked, ded_id=d['deduction_id']: self.edit_deduction(ded_id))

                    delete_btn = QPushButton("🗑️ Delete")
                    delete_btn.setObjectName("deleteBtn")
                    delete_btn.clicked.connect(lambda checked, ded_id=d['deduction_id']: self.delete_deduction(ded_id))

                    button_layout.addWidget(edit_btn)
                    button_layout.addWidget(delete_btn)
                    ded_layout.addLayout(button_layout)

                scroll_layout.addWidget(ded_frame)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.deduction_popup.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.deduction_popup.show()

    # ---------- delete deduction ----------
    def delete_deduction(self, deduction_id):
        """Delete a deduction"""
        reply = QMessageBox.question(
            self.deduction_popup,
            "Confirm Delete",
            "Are you sure you want to delete this deduction?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if Connectdb.delete_deduction(deduction_id):
                QMessageBox.information(self.deduction_popup, "Success", "Deduction deleted successfully!")
                self.deduction_popup.close()
                self.refresh_deductions()
            else:
                QMessageBox.critical(self.deduction_popup, "Error", "Failed to delete deduction.")

    # ---------- edit deduction ----------
    def edit_deduction(self, deduction_id):
        """Open edit form for a deduction"""
        deduction = Connectdb.get_deduction_by_id(deduction_id)
        if not deduction:
            QMessageBox.warning(self, "Error", "Deduction not found!")
            return

        self.edit_form_window = QWidget()
        self.edit_form_window.setWindowTitle("Edit Deduction")
        self.edit_form_window.resize(420, 260)

        self.edit_form_window.setStyleSheet("""
            QWidget { background-color: #2A7230; color: white; font-family: 'Segoe UI'; font-size: 13px; }
            QLineEdit, QComboBox { background-color: #ffffff; color: #2A7230; border-radius: 6px; padding: 4px 6px; border: none; }
            QLabel { color: white; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border-radius: 8px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #45A049; }
        """)

        form_layout = QFormLayout(self.edit_form_window)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        title = QLabel("<h2>Edit Deduction</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addRow(title)

        self.edit_deduction_type = QLineEdit(deduction['deduction_type'])
        self.edit_amount = QLineEdit(str(float(deduction['total_amount'])))
        self.edit_times_to_pay = QComboBox()
        self.edit_times_to_pay.addItems(["every payroll", "1", "2", "3", "4", "5"])

        # Set current value
        installment_count = deduction.get('installment_count', 0)
        if installment_count == 0:
            self.edit_times_to_pay.setCurrentText("every payroll")
        else:
            self.edit_times_to_pay.setCurrentText(str(installment_count))

        form_layout.addRow("Deduction Type:", self.edit_deduction_type)
        form_layout.addRow("Amount:", self.edit_amount)
        form_layout.addRow("Times to Pay:", self.edit_times_to_pay)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(lambda: self.save_edited_deduction(deduction_id))

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.edit_form_window.close)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        form_layout.addRow(button_layout)

        self.edit_form_window.show()

    def save_edited_deduction(self, deduction_id):
        """Save changes to a deduction"""
        deduction_type = self.edit_deduction_type.text().strip()
        amount_text = self.edit_amount.text().strip()

        if not deduction_type:
            QMessageBox.warning(self.edit_form_window, "Input Error", "Deduction type cannot be empty.")
            return

        import re
        try:
            s_clean = re.sub(r"[^0-9\.\-]", "", amount_text.replace(",", "").replace("₱", ""))
            amount = float(s_clean) if s_clean not in ("", "-", ".") else 0.0
        except Exception:
            QMessageBox.warning(self.edit_form_window, "Input Error", "Amount must be a valid number.")
            return

        times_to_pay_text = self.edit_times_to_pay.currentText()
        if times_to_pay_text == "every payroll":
            times_to_pay = 0
        else:
            times_to_pay = int(times_to_pay_text)

        if Connectdb.update_deduction(deduction_id, deduction_type, amount, times_to_pay):
            QMessageBox.information(self.edit_form_window, "Success", "Deduction updated successfully!")
            self.edit_form_window.close()
            if hasattr(self, 'deduction_popup'):
                self.deduction_popup.close()
            self.refresh_deductions()
        else:
            QMessageBox.critical(self.edit_form_window, "Error", "Failed to update deduction.")

    # ---------- employee selection popup ----------
    def open_employee_selection(self):
        self.selection_window = QWidget()
        self.selection_window.setWindowTitle("Select Employee")
        self.selection_window.resize(350, 450)

        self.selection_window.setStyleSheet("""
            QWidget { background-color: #2A7230; color: white; font-family: 'Segoe UI'; }
            QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 10px; padding: 8px; margin: 4px; }
            QPushButton:hover { background-color: #45A049; }
            QLabel { color: white; font-size: 15px; font-weight: bold; }
        """)

        layout = QVBoxLayout(self.selection_window)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Select an Employee")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # use static method
        employees = Connectdb.get_employees_for_selection(self.__companyName)
        for emp in employees:
            emp_id = emp["employee_id"]
            btn = QPushButton(f"{emp['first_name']} {emp['last_name']}")
            btn.clicked.connect(lambda checked, eid=emp_id: self.open_add_deduction_form(eid))
            layout.addWidget(btn)
        layout.addStretch(1)

        self.selection_window.show()

    # ---------- add deduction form ----------
    def open_add_deduction_form(self, employee_id):
        self.form_window = QWidget()
        self.form_window.setWindowTitle("Add Deduction")
        self.form_window.resize(420, 260)

        self.form_window.setStyleSheet("""
            QWidget { background-color: #2A7230; color: white; font-family: 'Segoe UI'; font-size: 13px; }
            QLineEdit, QComboBox { background-color: #ffffff; color: #2A7230; border-radius: 6px; padding: 4px 6px; border: none; }
            QLabel { color: white; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border-radius: 8px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #45A049; }
        """)

        form_layout = QFormLayout(self.form_window)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        self.deduction_type = QLineEdit()
        self.amount = QLineEdit()
        self.times_to_pay = QComboBox()
        self.times_to_pay.addItems(["every payroll", "1", "2", "3", "4", "5"])

        form_layout.addRow("Deduction Type:", self.deduction_type)
        form_layout.addRow("Amount:", self.amount)
        form_layout.addRow("Times to Pay:", self.times_to_pay)

        add_btn = QPushButton("Add Deduction")
        add_btn.clicked.connect(lambda: self.save_deduction(employee_id))
        form_layout.addRow(add_btn)

        self.form_window.show()

    # ---------- save deduction ----------
    def save_deduction(self, employee_id):
        deduction_type = (self.deduction_type.text() or "").strip()
        amount_text = (self.amount.text() or "").strip()
        if not deduction_type:
            QMessageBox.warning(self.form_window, "Input Error", "Deduction type cannot be empty.")
            return

        import re
        try:
            s_clean = re.sub(r"[^0-9\.\-]", "", amount_text.replace(",", "").replace("₱", ""))
            amount = float(s_clean) if s_clean not in ("", "-", ".") else 0.0
        except Exception:
            QMessageBox.warning(self.form_window, "Input Error", "Amount must be a valid number.")
            return

        times_to_pay_text = self.times_to_pay.currentText()
        if times_to_pay_text == "every payroll":
            times_to_pay = 0
        else:
            times_to_pay = int(times_to_pay_text)

        # call static method
        result = Connectdb.add_deduction(employee_id, deduction_type, amount, times_to_pay)
        if result == "success":
            QMessageBox.information(self.form_window, "Success", "Deduction added successfully!")
            self.form_window.close()
            self.refresh_deductions()
        else:
            QMessageBox.critical(self.form_window, "DB Error", "Could not save deduction.")