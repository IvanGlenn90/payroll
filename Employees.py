# employeewindow.py (fixed, AddEmployeeForm will pop up correctly)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout,
    QScrollArea, QSizePolicy, QFrame, QPushButton, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
import pymysql
import employeewindow
from employeewindow import EmployeeDetailWindow
import mainsyslogics  # ✅ only added this one


# Employee Card Widget
class EmployeeCard(QFrame):
    def __init__(self, employee_id, name, job, image, company, role, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.company = company
        self.role = role
        self.parent_window = parent

        self.setObjectName("employeeCard")
        self.setMinimumSize(100, 150)
        self.setMaximumSize(150, 200)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#employeeCard {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #DAEBDE;
            }
            QFrame#employeeCard:hover {
                border: 2px solid #43B64D;
                background-color: #f0f9f0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Profile Picture
        pic = QLabel()
        pixmap = QPixmap(image) if image else QPixmap()
        if pixmap.isNull():
            try:
                pixmap = QPixmap("stylesAndPic/profile-user.png")
            except Exception:
                pixmap = QPixmap()
        pic.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation))
        pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pic)

        # Name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; color:#50D85B;")
        layout.addWidget(name_label)

        # Job
        job_label = QLabel(job)
        job_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        job_label.setWordWrap(True)
        job_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(job_label)

    def mousePressEvent(self, event):
        """Open employee detail window when card is clicked"""
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                dlg = EmployeeDetailWindow(
                    self.employee_id,
                    self.company,
                    self.role,
                    parent=self.parent_window
                )
                result = dlg.exec()
                if result == QDialog.DialogCode.Accepted and self.parent_window:
                    self.parent_window.refresh_employees()
            except Exception as e:
                print(f"❌ Error opening detail window: {e}")
        super().mousePressEvent(event)


# Employee Window
class EmployeeWindow(QWidget):
    def __init__(self, role, companyName):
        super().__init__()
        self.setWindowTitle('LooTech')
        try:
            self.setWindowIcon(QIcon('stylesAndPic/lootechIcon.png'))
        except Exception:
            pass
        self.resize(900, 600)
        self.__role = role
        self.__companyName = companyName

        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title
        label = QLabel("<h1>Employees</h1>")
        layout.addWidget(label, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        label.setProperty('class', 'label')

        # Scroll area for employee cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1, 0, 1, 5)

        # Container with grid layout for employee cards
        self.container = QWidget()
        self.container.setProperty('class', 'container')
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.scroll.setWidget(self.container)

        # Fetch employee data
        self.refresh_employees()

        # --- Floating Add Button (only for staff) ---
        if self.__role == 'staff':
            self.add_button = QPushButton("+", self)
            self.add_button.setFixedSize(60, 60)
            self.add_button.setToolTip("Add Employee")
            self.add_button.setProperty("class", "floating_button")
            self.add_button.clicked.connect(self.open_add_employee)
            self.add_button.raise_()
            self.update_button_position()
            self.add_button.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_button_position()

    def update_button_position(self):
        if hasattr(self, "add_button"):
            x = max(10, self.width() - 90)
            y = max(10, self.height() - 90)
            self.add_button.move(x, y)
            self.add_button.raise_()

    def refresh_employees(self):
        """Refresh employee list"""
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        employees = self.fetch_employees_from_db()
        self.populate_cards(employees)

    def fetch_employees_from_db(self):
        """Delegate fetching to Connectdb"""
        try:
            employees = mainsyslogics.Connectdb.fetch_employees(self.__companyName)
            print(f"✅ Loaded {len(employees)} employees from database.")
            return employees
        except Exception as e:
            print(f"❌ Error fetching employees: {e}")
            return []

    def populate_cards(self, employees):
        cols = 5
        row, col = 0, 0
        for emp in employees:
            card = EmployeeCard(
                emp["id"],
                emp["name"],
                emp["job"],
                emp.get("image", "stylesAndPic/profile-user.png"),
                self.__companyName,
                self.__role,
                parent=self
            )
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    # ✅ FIXED: Open AddEmployeeForm as top-level window
    def open_add_employee(self):
        try:
            self.next_window = employeewindow.AddEmployeeForm(self.__companyName)
            self.next_window.employee_added.connect(self.refresh_employees)
            self.next_window.show()
            self.next_window.raise_()
            self.next_window.activateWindow()
        except Exception as e:
            print(f"❌ Error opening add-employee form: {e}")
