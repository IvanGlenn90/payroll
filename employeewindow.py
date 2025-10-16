from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QRegion
from mainsyslogics import Connectdb
import os
import shutil

# ==========================================================
# 🟩 ADD EMPLOYEE FORM
# ==========================================================
class AddEmployeeForm(QWidget):
    employee_added = pyqtSignal()

    def __init__(self, companyName, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Employee")
        self.setObjectName("EmployeeForm")
        self.__companyName = companyName
        self.photo_path = None

        # --- Avatar Section ---
        self.avatar_label = QLabel("No Photo")
        self.avatar_label.setObjectName("addEmlabel")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(120, 120)
        self.avatar_label.setProperty('class', 'addEmavatars')

        choose_btn = QPushButton("Choose Photo")
        choose_btn.clicked.connect(self.choose_photo)

        avatar_vbox = QVBoxLayout()
        avatar_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_vbox.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        avatar_vbox.addWidget(choose_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        avatar_hbox = QHBoxLayout()
        avatar_hbox.addStretch()
        avatar_hbox.addLayout(avatar_vbox)
        avatar_hbox.addStretch()

        # --- Grid Fields ---
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setContentsMargins(40, 10, 40, 10)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()
        self.position = QLineEdit()
        self.salary = QLineEdit()
        self.status = QComboBox()  # Added status
        self.status.addItems(["Active", "Inactive"])  # Default options

        for le in [self.first_name, self.last_name, self.email, self.phone,
                   self.address, self.position, self.salary]:
            le.setProperty('class', 'addEmlineedit')

        def create_field(label_text, widget):
            v = QVBoxLayout()
            v.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            return v

        row1 = [("First Name", self.first_name), ("Last Name", self.last_name), ("Email", self.email)]
        row2 = [("Phone", self.phone), ("Address", self.address), ("Position", self.position)]
        for i, (lbl, le) in enumerate(row1):
            grid.addLayout(create_field(lbl, le), 0, i)
        for i, (lbl, le) in enumerate(row2):
            grid.addLayout(create_field(lbl, le), 1, i)
        grid.addLayout(create_field("Salary (by Hour)", self.salary), 2, 1)
        grid.addLayout(create_field("Status", self.status), 2, 2)  # Add status field

        # --- Save Button ---
        save_btn = QPushButton("Save")
        save_btn.setProperty('class', 'addEMbutton')
        save_btn.clicked.connect(lambda: self.save_employee(self.__companyName))

        save_hbox = QHBoxLayout()
        save_hbox.addStretch()
        save_hbox.addWidget(save_btn)
        save_hbox.addStretch()

        # --- Main Layout ---
        main = QVBoxLayout(self)
        main.addLayout(avatar_hbox)
        main.addLayout(grid)
        main.addLayout(save_hbox)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # Load default avatar
        self.load_photo()

    # ---------- PHOTO HANDLING ----------
    def load_photo(self, path=None):
        if path and os.path.exists(path):
            pix = QPixmap(path)
        else:
            pix = QPixmap("default_avatar.png")
        pix = pix.scaled(self.avatar_label.width(), self.avatar_label.height(),
                         Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                         Qt.TransformationMode.SmoothTransformation)
        self.avatar_label.setPixmap(pix)
        mask = QRegion(0, 0, self.avatar_label.width(), self.avatar_label.height(), QRegion.RegionType.Ellipse)
        self.avatar_label.setMask(mask)
        self.photo_path = path

    def choose_photo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select photo", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            self.load_photo(fname)

    # ---------- SAVE EMPLOYEE ----------
    def save_employee(self, companyName):
        try:
            try:
                salary_val = float(self.salary.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid salary amount.")
                return

            dest_path = None
            if self.photo_path:
                os.makedirs("employeePic", exist_ok=True)
                photo_filename = os.path.basename(self.photo_path)
                dest_path = os.path.join("employeePic", photo_filename)
                shutil.copy2(self.photo_path, dest_path)

            db = Connectdb()
            result = db.add_employee(
                first_name=self.first_name.text(),
                last_name=self.last_name.text(),
                email=self.email.text(),
                contact=self.phone.text(),
                address=self.address.text(),
                job_title=self.position.text(),
                salary=salary_val,
                employment_status=self.status.currentText(),
                company=companyName,
                photo_path=dest_path
            )

            if result == "success":
                QMessageBox.information(self, "Success", "Employee saved successfully!")
                self.employee_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Error", f"Failed to save employee: {result}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")


# ==========================================================
# 🟦 EMPLOYEE DETAIL WINDOW
# ==========================================================
class EmployeeDetailWindow(QDialog):
    def __init__(self, employee_id, companyName, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Employee Details")
        self.setObjectName("EmployeeForm")
        self.resize(520, 680)
        self.employee_id = employee_id
        self.companyName = companyName
        self.role = role
        self.photo_path = None
        self.original_photo_path = None

        # Load employee data
        self.load_employee_data()

        # --- Avatar ---
        self.avatar_label = QLabel("No Photo")
        self.avatar_label.setObjectName("addEmlabel")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(120, 120)
        self.avatar_label.setProperty('class', 'addEmavatars')

        self.load_photo(self.original_photo_path)

        avatar_vbox = QVBoxLayout()
        avatar_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_vbox.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        if self.role == 'staff':
            change_btn = QPushButton("Change Photo")
            change_btn.clicked.connect(self.choose_photo)
            avatar_vbox.addWidget(change_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        avatar_hbox = QHBoxLayout()
        avatar_hbox.addStretch()
        avatar_hbox.addLayout(avatar_vbox)
        avatar_hbox.addStretch()

        # --- Fields ---
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setContentsMargins(40, 10, 40, 10)

        self.first_name = QLineEdit(self.employee_data.get('first_name', ''))
        self.last_name = QLineEdit(self.employee_data.get('last_name', ''))
        self.email = QLineEdit(self.employee_data.get('email', ''))
        self.phone = QLineEdit(self.employee_data.get('contact', ''))
        self.address = QLineEdit(self.employee_data.get('address', ''))
        self.position = QLineEdit(self.employee_data.get('job_title', ''))
        self.salary = QLineEdit(str(self.employee_data.get('salary', '')))

        self.status = QComboBox()
        status_options = ["Active", "Inactive"]  # your possible statuses
        self.status.addItems(status_options)

        # Get the value from the database
        current_status = self.employee_data.get("employment_status", "Active")

        # Ensure the combo box shows the actual database value
        if current_status.capitalize() in status_options:
            self.status.setCurrentText(current_status.capitalize())
        else:
            self.status.setCurrentText("Active")

        for le in [self.first_name, self.last_name, self.email, self.phone,
                   self.address, self.position, self.salary, self.status]:
            le.setProperty('class', 'addEmlineedit')

        if self.role != 'staff':
            for le in [self.first_name, self.last_name, self.email,
                       self.phone, self.address, self.position, self.salary, self.status]:
                if isinstance(le, QLineEdit):
                    le.setReadOnly(True)
                else:
                    le.setEnabled(False)

        def create_field(label_text, widget):
            v = QVBoxLayout()
            v.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            return v

        row1 = [("First Name", self.first_name), ("Last Name", self.last_name), ("Email", self.email)]
        row2 = [("Phone", self.phone), ("Address", self.address), ("Position", self.position)]
        for i, (lbl, le) in enumerate(row1):
            grid.addLayout(create_field(lbl, le), 0, i)
        for i, (lbl, le) in enumerate(row2):
            grid.addLayout(create_field(lbl, le), 1, i)
        grid.addLayout(create_field("Salary (by Hour)", self.salary), 2, 1)
        grid.addLayout(create_field("Status", self.status), 2, 2)  # status

        # --- Buttons ---
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        if self.role == 'staff':
            save_btn = QPushButton("Save Changes")
            save_btn.setProperty('class', 'addEMbutton')
            save_btn.clicked.connect(self.save_employee)
            button_hbox.addWidget(save_btn)
        close_btn = QPushButton("Close")
        close_btn.setProperty('class', 'addEMbutton')
        close_btn.clicked.connect(self.close)
        button_hbox.addWidget(close_btn)
        button_hbox.addStretch()

        # --- Main Layout ---
        main = QVBoxLayout(self)
        main.addLayout(avatar_hbox)
        main.addLayout(grid)
        main.addLayout(button_hbox)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

    # ---------- LOAD EMPLOYEE ----------
    def load_employee_data(self):
        try:
            db = Connectdb()
            row = db.get_employee_by_id(self.employee_id, self.companyName)
            if not row:
                QMessageBox.warning(self, "Error", "Employee not found!")
                self.employee_data = {}
                return
            self.employee_data = row
            self.original_photo_path = self.employee_data.get('photo_path')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading employee: {e}")
            self.employee_data = {}

    # ---------- PHOTO HANDLING ----------
    def load_photo(self, path=None):
        if path and os.path.exists(path):
            pix = QPixmap(path)
        else:
            pix = QPixmap("default_avatar.png")
        pix = pix.scaled(self.avatar_label.width(), self.avatar_label.height(),
                         Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                         Qt.TransformationMode.SmoothTransformation)
        self.avatar_label.setPixmap(pix)
        mask = QRegion(0, 0, self.avatar_label.width(), self.avatar_label.height(), QRegion.RegionType.Ellipse)
        self.avatar_label.setMask(mask)
        self.photo_path = path

    def choose_photo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select photo", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            self.load_photo(fname)

    # ---------- SAVE CHANGES ----------
    def save_employee(self):
        try:
            salary_val = float(self.salary.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid salary amount.")
            return

        dest_path = self.original_photo_path
        if self.photo_path and self.photo_path != self.original_photo_path:
            os.makedirs("employeePic", exist_ok=True)
            photo_filename = f"{self.first_name.text()}_{self.last_name.text()}{os.path.splitext(self.photo_path)[1]}"
            dest_path = os.path.join("employeePic", photo_filename)
            shutil.copy2(self.photo_path, dest_path)

        db = Connectdb()
        success = db.update_employee(
            employee_id=self.employee_id,
            first_name=self.first_name.text(),
            last_name=self.last_name.text(),
            email=self.email.text(),
            contact=self.phone.text(),
            address=self.address.text(),
            job_title=self.position.text(),
            salary=salary_val,
            employment_status=self.status.currentText(),
            photo_path=dest_path
        )

        if success:
            QMessageBox.information(self, "Success", "Employee updated successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to update employee")
