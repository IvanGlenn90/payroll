import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton,
                             QTextEdit, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

import Dashboard
import index
from Employees import EmployeeWindow
from Attendance import AttendanceWindow
from Payroll import PayrollWindow
from Deduction import DeductionWindow


class MainPage_window(QWidget):
    def __init__(self, role, passkey, companyName):
        super().__init__()
        self.setWindowTitle('LooTech')
        self.setWindowIcon(QIcon('stylesAndPic/lootechIcon.png'))
        self.resize(900, 600)
        self.__role = role
        self.__passkey = passkey
        self.__companyName = companyName

        layout = QGridLayout()
        self.setLayout(layout)
        self.setObjectName('Window')
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation sidebar
        navigation = QWidget()
        navigation.setMinimumSize(QSize(150, 150))
        navigation_layout = QVBoxLayout()
        navigation.setObjectName('navigation')
        navigation.setLayout(navigation_layout)
        navigation.setContentsMargins(0, 10, 0, 0)
        navigation_layout.setContentsMargins(0, 0, 0, 0)
        navigation_layout.setSpacing(0)

        navigation_label = QLabel('Menu')
        navigation_label.setProperty('class', 'navigation_label')
        navigation_layout.addWidget(navigation_label)

        # Menu items
        menu_items = ['Dashboard', 'Employee', 'Deductions', 'Attendance', 'Payroll']
        for menu_item in menu_items:
            menu_btn = QPushButton(menu_item)
            menu_btn.setProperty('class', 'menuItems')
            menu_btn.clicked.connect(lambda checked, item=menu_item: self.handle_menu(item))
            menu_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            navigation_layout.addWidget(menu_btn)

        navigation_layout.addStretch(1)

        # Logout button
        log_out_btn = QPushButton('Log Out')
        log_out_btn.setProperty('class', 'log_out_btn')
        log_out_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        log_out_btn.clicked.connect(self.logout)
        navigation_layout.addWidget(log_out_btn)

        layout.addWidget(navigation, 0, 0)

        # Body container
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.body, 0, 1)

        # Load dashboard by default
        self.load_dashboard()

    def clear_body(self):
        """Remove the current widget inside body"""
        while self.body_layout.count():
            child = self.body_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def handle_menu(self, item):
        print(f"Menu clicked: {item}")
        if item == "Dashboard":
            self.load_dashboard()
        elif item == "Employee":
            self.load_employee()
        elif item == "Deductions":
            self.load_deductions()
        elif item == "Attendance":
            self.load_attendance()
        elif item == "Payroll":
            self.load_payroll()

    def load_dashboard(self):
        self.clear_body()
        dashboard = Dashboard.DashboardWindow(self.__role, self.__passkey, self.__companyName)
        self.body_layout.addWidget(dashboard)

    def load_employee(self):
        self.clear_body()
        employee = EmployeeWindow(self.__role, self.__companyName)
        self.body_layout.addWidget(employee)

    def load_deductions(self):
        self.clear_body()
        deductions = DeductionWindow(self.__role, self.__companyName)
        self.body_layout.addWidget(deductions)

    def load_attendance(self):
        self.clear_body()
        attendance = AttendanceWindow(self.__role, self.__companyName)
        self.body_layout.addWidget(attendance)

    def load_payroll(self):
        self.clear_body()
        payroll = PayrollWindow(self.__role, self.__companyName)
        self.body_layout.addWidget(payroll)

    def logout(self):
        self.next_window = index.LogInWindow()
        self.close()
        self.next_window.show()