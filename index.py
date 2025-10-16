import secrets
import string
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import pymysql
import mainsyslogics
import mainpage


class LogInWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LooTech')
        self.setWindowIcon(QIcon('stylesAndPic/lootechIcon.png'))
        self.resize(900, 600)

        # Main Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Left Container (logo / title)
        self.container1 = QWidget()
        self.container1.setObjectName("container1")
        container1_layout = QVBoxLayout()
        container1_layout.setContentsMargins(0, 0, 0, 0)
        container1_layout.setSpacing(0)
        self.container1.setLayout(container1_layout)

        self.logo_label = QLabel()
        pixmap = QPixmap('stylesAndPic/lootechIcon.png')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(200, 200)
        self.logo_label.setProperty("class", "logo")
        container1_layout.addStretch(1)
        container1_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("<h1>Partnering for Your Success </h1>")
        self.title.setProperty("class", "title")
        container1_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        container1_layout.addStretch(1)

        # Right Container (form area)
        self.container2 = QWidget()
        self.container2.setObjectName("container2")
        self.container2_layout = QVBoxLayout()
        self.container2_layout.setContentsMargins(10, 0, 0, 0)
        self.container2_layout.setSpacing(0)
        self.container2.setLayout(self.container2_layout)

        # Form widget inside right container
        self.form_widget = QWidget()
        self.form_widget.setObjectName("VBox")
        self.form_layout = QGridLayout()
        self.form_widget.setLayout(self.form_layout)
        self.form_layout.setSpacing(10)
        self.form_layout.setContentsMargins(50, 10, 50, 50)

        self.container2_layout.addWidget(self.form_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add containers to main layout
        self.layout.addWidget(self.container1, 0, 0)
        self.layout.addWidget(self.container2, 0, 1)

        # dynamic widgets tracker (used for signup field swapping)
        self.dynamic_widgets = []

        # Show login form first
        self.show_login_form()

    # --------------------------
    # Clear current form area
    # --------------------------
    def clear_form(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.dynamic_widgets = []

    # login
    def show_login_form(self):
        self.clear_form()

        form_title = QLabel("<h2>Log In</h2>")
        form_title.setProperty("class", "form_labels")
        self.form_layout.addWidget(form_title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addWidget(self.username_input, 1, 0, 1, 3)
        username_label = QLabel("<h3> Username </h3>")
        username_label.setProperty("class", "form_labels")
        self.form_layout.addWidget(username_label, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # Password with eye icon
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.eye_button = QPushButton()
        self.eye_button.setIcon(QIcon("stylesAndPic/eye.png"))
        self.eye_button.setFixedSize(30, 30)
        self.eye_button.setCheckable(True)
        self.eye_button.setStyleSheet("border: none;")
        self.eye_button.clicked.connect(lambda: self.toggle_password_visibility(self.password_input, self.eye_button))

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.eye_button)
        self.form_layout.addWidget(password_container, 3, 0, 1, 3)

        password_label = QLabel("<h3> Password</h3>")
        password_label.setProperty("class", "form_labels")
        self.form_layout.addWidget(password_label, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        logIn_button = QPushButton("Log In")
        logIn_button.setProperty("class", "loginButton")
        logIn_button.clicked.connect(self.login)
        self.form_layout.addWidget(logIn_button, 5, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        signUP_button = QPushButton("Sign Up")
        signUP_button.setProperty("class", "signupbutton")
        signUP_button.clicked.connect(self.show_signup_form)
        self.form_layout.addWidget(signUP_button, 6, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

    # sign up form
    def show_signup_form(self):
        self.clear_form()

        form_title = QLabel("<h2>Sign In</h2>")
        form_title.setProperty("class", "form_labels")
        self.form_layout.addWidget(form_title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.role_choice = QComboBox()
        self.role_choice.addItems(["Admin", "Staff"])
        self.role_choice.setProperty("class", "role_choice")
        self.role_choice.currentTextChanged.connect(self.update_signup_fields)
        self.form_layout.addWidget(self.role_choice, 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.dynamic_widgets = []
        self.update_signup_fields(self.role_choice.currentText())

    def update_signup_fields(self, role):
        for w in self.dynamic_widgets:
            try:
                w.deleteLater()
            except Exception:
                pass
        self.dynamic_widgets = []

        row = 2

        # Username
        username_input = QLineEdit()
        username_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addWidget(username_input, row, 0, 1, 3)
        username_label = QLabel("<h3>Username</h3>")
        username_label.setProperty("class", "form_labels")
        self.form_layout.addWidget(username_label, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dynamic_widgets += [username_input, username_label]
        row += 2

        if role == "Admin":
            # Company Name
            company_input = QLineEdit()
            company_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.form_layout.addWidget(company_input, row, 0, 1, 3)
            company_label = QLabel("<h3>Company Name</h3>")
            company_label.setProperty("class", "form_labels")
            self.form_layout.addWidget(company_label, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
            self.dynamic_widgets += [company_input, company_label]
            row += 2

            # Password with eye
            admin_password_container = QWidget()
            admin_password_layout = QHBoxLayout(admin_password_container)
            admin_password_layout.setContentsMargins(0, 0, 0, 0)
            admin_password_layout.setSpacing(0)

            admin_password = QLineEdit()
            admin_password.setEchoMode(QLineEdit.EchoMode.Password)
            admin_password.setAlignment(Qt.AlignmentFlag.AlignCenter)

            admin_eye_button = QPushButton()
            admin_eye_button.setIcon(QIcon("stylesAndPic/eye.png"))
            admin_eye_button.setFixedSize(30, 30)
            admin_eye_button.setCheckable(True)
            admin_eye_button.setStyleSheet("border: none;")
            admin_eye_button.clicked.connect(lambda: self.toggle_password_visibility(admin_password, admin_eye_button))

            admin_password_layout.addWidget(admin_password)
            admin_password_layout.addWidget(admin_eye_button)
            self.form_layout.addWidget(admin_password_container, row, 0, 1, 3)

            admin_password_label = QLabel("<h3>Password</h3>")
            admin_password_label.setProperty("class", "form_labels")
            self.form_layout.addWidget(admin_password_label, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
            self.dynamic_widgets += [admin_password_container, admin_password_label]
            row += 2

            self._signup_refs = {
                "username": username_input,
                "company": company_input,
                "password": admin_password
            }

        else:
            # Staff passkey
            passkey_input = QLineEdit()
            passkey_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.form_layout.addWidget(passkey_input, row, 0, 1, 3)
            passkey_label = QLabel("<h3>Passkey</h3>")
            passkey_label.setProperty("class", "form_labels")
            self.form_layout.addWidget(passkey_label, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
            self.dynamic_widgets += [passkey_input, passkey_label]
            row += 2

            # Password with eye
            staff_password_container = QWidget()
            staff_password_layout = QHBoxLayout(staff_password_container)
            staff_password_layout.setContentsMargins(0, 0, 0, 0)
            staff_password_layout.setSpacing(0)

            staff_password = QLineEdit()
            staff_password.setEchoMode(QLineEdit.EchoMode.Password)
            staff_password.setAlignment(Qt.AlignmentFlag.AlignCenter)

            staff_eye_button = QPushButton()
            staff_eye_button.setIcon(QIcon("stylesAndPic/eye.png"))
            staff_eye_button.setFixedSize(30, 30)
            staff_eye_button.setCheckable(True)
            staff_eye_button.setStyleSheet("border: none;")
            staff_eye_button.clicked.connect(lambda: self.toggle_password_visibility(staff_password, staff_eye_button))

            staff_password_layout.addWidget(staff_password)
            staff_password_layout.addWidget(staff_eye_button)
            self.form_layout.addWidget(staff_password_container, row, 0, 1, 3)

            staff_password_label = QLabel("<h3>Password</h3>")
            staff_password_label.setProperty("class", "form_labels")
            self.form_layout.addWidget(staff_password_label, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
            self.dynamic_widgets += [staff_password_container, staff_password_label]
            row += 2

            self._signup_refs = {
                "username": username_input,
                "passkey": passkey_input,
                "password": staff_password
            }

        signup_btn = QPushButton(f"Sign Up as {role}")
        signup_btn.setProperty("class", "signupbutton")
        signup_btn.clicked.connect(lambda: self.signup_action(role))
        self.form_layout.addWidget(signup_btn, row, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dynamic_widgets.append(signup_btn)
        signup_btn.setProperty('class', 'loginButton')
        row += 1

        self.back_btn = QPushButton("Back to Log In")
        self.back_btn.setProperty("class", "signupbutton")
        self.back_btn.clicked.connect(self.show_login_form)
        self.form_layout.addWidget(self.back_btn, row, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dynamic_widgets.append(self.back_btn)

    # Toggle password visibility
    def toggle_password_visibility(self, password_input, eye_button):
        if eye_button.isChecked():
            password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            eye_button.setIcon(QIcon("stylesAndPic/eye-slash.png"))
        else:
            password_input.setEchoMode(QLineEdit.EchoMode.Password)
            eye_button.setIcon(QIcon("stylesAndPic/eye.png"))

    # Perform signup
    def signup_action(self, role):
        try:
            if role == "Admin":
                username = self._signup_refs["username"].text().strip()
                company = self._signup_refs["company"].text().strip()
                password = self._signup_refs["password"].text().strip()

                print(f"Admin SignUp → Username: {username}, Company: {company}, Password: {password}")

                result, message_or_passkey = mainsyslogics.Connectdb.insert_user(
                    username, password, company, role)

                if result == "success":
                    passkey = message_or_passkey or "(no passkey returned)"
                    QMessageBox.information(
                        self,
                        "Admin Created ✅",
                        f"Admin account created successfully!\n\n🔑 Staff Passkey:\n{passkey}\n\nShare this key with your staff."
                    )
                    self.show_login_form()

                elif result == "duplicate":
                    QMessageBox.warning(self, "Signup Failed", "Username already exists!")

                else:
                    QMessageBox.warning(self, "Signup Failed", f"Something went wrong: {message_or_passkey}")

            else:  # Staff
                username = self._signup_refs["username"].text().strip()
                passkey = self._signup_refs["passkey"].text().strip()
                password = self._signup_refs["password"].text().strip()

                print(f"Staff SignUp → Username: {username}, Passkey: {passkey}, Password: {password}")

                valid_key, company_name = mainsyslogics.Connectdb.verify_passkey(passkey)

                if valid_key:
                    result, message = mainsyslogics.Connectdb.insert_user(
                        username, password, None, role, passkey
                    )
                    if result == "success":
                        QMessageBox.information(self, "Signup Success ✅", "Staff account created successfully!")
                        self.show_login_form()
                    elif result == "duplicate":
                        QMessageBox.warning(self, "Signup Failed", "Username already exists!")
                    else:
                        QMessageBox.warning(self, "Signup Failed", f"Something went wrong: {message}")
                else:
                    QMessageBox.warning(self, "Invalid Passkey", "That passkey does not exist or is invalid.")

        except pymysql.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {e}")

    # LOGIN FUNCTION
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        try:
            # create a Connectdb instance
            db = mainsyslogics.Connectdb()
            result = db.login_user(username, password)

            if not result or result == "invalid":
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            else:
                role, passkey, companyName = result
                self.next_window = mainpage.MainPage_window(role, passkey, companyName)
                self.next_window.show()
                self.hide()

        except pymysql.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {e}")


if __name__ == "__main__":
    testdb = mainsyslogics.Connectdb()
    print(testdb)
    app = QApplication(sys.argv)
    window = LogInWindow()
    window.show()
    with open("stylesAndPic/style.css", "r") as file:
        app.setStyleSheet(file.read())
    sys.exit(app.exec())
