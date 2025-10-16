import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout,
    QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame, QScrollArea,
    QDialog, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from Employees import EmployeeWindow
import mainsyslogics


# ---------------- Add Announcement Dialog ----------------
class AddAnnouncementDialog(QDialog):
    def __init__(self, company_name, parent=None):
        super().__init__(parent)
        self.company_name = company_name
        self.setWindowTitle("Add Announcement")
        self.resize(500, 350)

        self.setStyleSheet("""
            QDialog {
                background-color: #2A7230;
            }
            QLabel {
                color: #F0F8FF;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                color: #2A7230;
                border: 2px solid #1e5024;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #50D85B;
            }
            QPushButton {
                background-color: #50D85B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45c050;
            }
            QPushButton#cancelBtn {
                background-color: #e74c3c;
            }
            QPushButton#cancelBtn:hover {
                background-color: #c0392b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("<h2>Create New Announcement</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter announcement title...")
        form_layout.addRow("Title:", self.title_input)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter announcement message...")
        self.message_input.setMinimumHeight(150)
        form_layout.addRow("Message:", self.message_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Post Announcement")
        save_btn.clicked.connect(self.save_announcement)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def save_announcement(self):
        """Save a new announcement to the database."""

        title = self.title_input.text().strip()
        message = self.message_input.toPlainText().strip()

        # Validate input
        if not title or not message:
            missing_field = "title" if not title else "message"
            QMessageBox.warning(self, "Missing Field", f"Please enter an announcement {missing_field}.")
            return

        try:
            db = mainsyslogics.Connectdb()
            success = db.add_announcement(
                title=title,
                message=message,
                company=self.company_name,  # company required by refactored add_announcement
                category="general",
                type="info",
                status="unread"
            )

            if success:
                QMessageBox.information(self, "Success", "Announcement posted successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Failed", "Could not save the announcement. Please try again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post announcement: {e}")


# ---------------- View Announcement Dialog ----------------
class ViewAnnouncementDialog(QDialog):
    def __init__(self, title, message, created_at, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Announcement Details")
        self.resize(500, 400)

        self.setStyleSheet("""
            QDialog {
                background-color: #2A7230;
            }
            QLabel {
                color: #F0F8FF;
                font-size: 13px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #50D85B;
            }
            QLabel#dateLabel {
                font-size: 11px;
                color: #b0e0b5;
            }
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.95);
                color: #2A7230;
                border: 2px solid #1e5024;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #50D85B;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45c050;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Date
        date_label = QLabel(f"Posted: {created_at}")
        date_label.setObjectName("dateLabel")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)

        # Message
        message_display = QTextEdit()
        message_display.setPlainText(message)
        message_display.setReadOnly(True)
        layout.addWidget(message_display)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


# ---------------- Announcement Card (Shows only title, click to view full) ----------------
class AnnouncementCard(QFrame):
    def __init__(self, title, message, created_at, parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.created_at = created_at

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                
                height: 20px;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(0)

        # Title only - truncate if too long (single line with ellipsis)
        # Truncate title if longer than 28 characters
        display_title = title if len(title) <= 28 else title[:25] + "..."

        title_label = QLabel(f"<b>{display_title}</b>")
        print(display_title)

        title_label.setWordWrap(False)
        title_label.setStyleSheet("font-size: 12px; color: aliceblue;")
        layout.addWidget(title_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = ViewAnnouncementDialog(self.title, self.message, self.created_at, self)
            dialog.exec()
        super().mousePressEvent(event)


class DashboardWindow(QWidget):
    def __init__(self, role, passkey, companyName):
        super().__init__()
        self.setWindowTitle('LooTech')
        try:
            self.setWindowIcon(QIcon('stylesAndPic/lootechIcon.png'))
        except:
            pass
        self.resize(900, 600)
        self.__role = role
        self.__passkey = passkey
        self.__companyName = companyName

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Body
        body = QWidget()
        body_layout = QGridLayout()
        body.setObjectName('body')
        body.setLayout(body_layout)
        body.setContentsMargins(10, 0, 10, 10)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(1)

        side = QVBoxLayout()
        side.setObjectName('side')
        side.setContentsMargins(0, 0, 20, 0)
        side.setSpacing(0)

        # Header
        label = QLabel("<h1>Dashboard</h1>")
        label.setProperty('class', 'label')
        body_layout.addWidget(label, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        # Get dashboard data
        db = mainsyslogics.Connectdb()

        # Calculate totals with error handling
        try:
            payroll_summaries = mainsyslogics.Connectdb.get_payroll_summary(self.__companyName)
            total_compensation = sum(p['total_net_pay'] for p in payroll_summaries) if payroll_summaries else 0
            latest_payroll = payroll_summaries[0]['total_net_pay'] if payroll_summaries else 0

            # Count drafts using static method
            pending_pay = mainsyslogics.Connectdb.get_pending_drafts_count(self.__companyName)
        except Exception as e:
            print(f"❌ Error fetching dashboard data: {e}")
            total_compensation = 0
            latest_payroll = 0
            pending_pay = 0

        # Dashboard Cards
        cards = {
            "Total Compensation": f'₱{total_compensation:,.2f}',
            "Latest Payroll": f'₱{latest_payroll:,.2f}',
            "Pending Drafts": str(pending_pay)
        }
        counter = 0

        for card, value in cards.items():
            frame = QWidget()
            frame.setMinimumSize(180, 150)
            frame.setMaximumSize(250, 250)
            frame.setContentsMargins(10, 10, 10, 10)
            frame_layout = QVBoxLayout()
            frame_layout.setSpacing(1)
            frame.setLayout(frame_layout)
            frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            frame.setObjectName('frame')

            card_label = QLabel(f"<p>{card}</p>")
            card_label.setProperty("class", "card_label")
            frame_layout.addWidget(card_label)

            card_value = QLabel(value)
            card_value.setProperty("class", "card_value_label")
            frame_layout.addWidget(card_value, alignment=Qt.AlignmentFlag.AlignRight)

            body_layout.addWidget(frame, 1, counter, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)
            counter += 1

        # Announcement Section
        announcement_frame = QWidget()
        announcement_frame.setMinimumSize(200, 350)
        announcement_frame.setMaximumSize(250, 700)
        announcement_frame.setContentsMargins(10, 10, 10, 10)
        announcement_frame.setObjectName('announcement_frame')
        announcement_frame.setStyleSheet("""
            QWidget#announcement_frame {
                background-color: #43B64D;
                border-radius: 15px;
            }
        """)

        announcement_layout = QVBoxLayout(announcement_frame)
        announcement_layout.setSpacing(10)
        announcement_layout.setContentsMargins(15, 15, 15, 15)
        announcement_frame.setLayout(announcement_layout)

        # Header with title and add button
        header_layout = QHBoxLayout()

        announcement_label = QLabel("<p style='font-size: 12px; font-weight: bold; color: #F0F8FF;'>Announcements</p>")
        header_layout.addWidget(announcement_label)

        # Add button for admin only
        if self.__role == 'admin':
            add_btn = QPushButton("+")
            add_btn.setFixedSize(30, 30)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #50D85B;
                    color: white;
                    border-radius: 15px;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    height: 20px;
                }
                QPushButton:hover {
                    background-color: #45c050;
                }
            """)
            add_btn.clicked.connect(self.open_add_announcement)
            header_layout.addWidget(add_btn)

        announcement_layout.addLayout(header_layout)

        # Scroll area for announcements
        announcement_scroll = QScrollArea()
        announcement_scroll.setWidgetResizable(True)
        announcement_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2A7230;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """)
        announcement_scroll.viewport().setStyleSheet("background-color: #43B64D;")

        # Container for announcement cards
        self.announcement_container = QWidget()
        self.announcement_container.setStyleSheet("background-color: #43B64D;")
        self.announcement_container_layout = QVBoxLayout(self.announcement_container)
        self.announcement_container_layout.setContentsMargins(5, 5, 5, 5)
        self.announcement_container_layout.setSpacing(8)
        self.announcement_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Load announcements
        self.load_announcements()

        announcement_scroll.setWidget(self.announcement_container)
        announcement_layout.addWidget(announcement_scroll)

        side.addWidget(announcement_frame, alignment=Qt.AlignmentFlag.AlignTop)

        # Attendance Graph with REAL DATA
        try:
            latest_attendance_data = mainsyslogics.Connectdb.get_latest_attendance_for_dashboard(self.__companyName)
            print(f"✅ Dashboard attendance data: {latest_attendance_data}")
        except Exception as e:
            print(f"❌ Error fetching attendance data: {e}")
            latest_attendance_data = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}

        attendance_card = create_attendance_card(
            title="Latest Week Attendance Summary",
            data=latest_attendance_data,
            color="#3498db"
        )
        body_layout.addWidget(attendance_card, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)


        layout.addWidget(body, 1, 0, 4, 1)
        body_layout.addLayout(side, 1, 4, 3, 1)

        if self.__role == 'admin':
            passkey_label = QLabel(f"<h4>Passkey: {self.__passkey}</h4>")
            passkey_label.setProperty("class", "passkey")
            body_layout.addWidget(passkey_label, 4, 0, 1, 2)

    def load_announcements(self):
        """Load announcements from database"""
        # Clear existing announcements
        while self.announcement_container_layout.count():
            child = self.announcement_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            # Use the new get_announcements method
            announcements = mainsyslogics.Connectdb.get_announcements(self.__companyName)

            if announcements:
                for ann in announcements:
                    title = ann.get('title', 'Announcement')
                    message = ann.get('message', '')
                    created_at = ann.get('created_at', '')

                    # Format date
                    if created_at:
                        try:
                            created_at = created_at.strftime("%b %d, %Y")
                        except:
                            created_at = str(created_at)

                    card = AnnouncementCard(title, message, created_at)
                    self.announcement_container_layout.addWidget(card)
            else:
                # Default message if no announcements
                no_ann_label = QLabel("<i>No announcements yet</i>")
                no_ann_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_ann_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); padding: 20px;")
                self.announcement_container_layout.addWidget(no_ann_label)

        except Exception as e:
            print(f"Error loading announcements: {e}")

    def open_add_announcement(self):
        """Open dialog to add new announcement"""
        dialog = AddAnnouncementDialog(self.__companyName, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_announcements()  # Refresh announcements

    def handle_menu(self, item):
        print(f"Menu clicked: {item}")
        if item == "Employee":
            self.open_employee_window()

    def open_employee_window(self):
        try:
            self.second_window = EmployeeWindow(self.__role, self.__companyName)
            self.close()
            self.second_window.show()
        except Exception as e:
            print(f"❌ Error opening employee window: {e}")


# ATTENDANCE CARD - BAR GRAPH
def create_attendance_card(**kwargs):
    """Create attendance summary card with bar graph"""
    title = kwargs.get("title", "Attendance Summary")
    data = kwargs.get("data", {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0})
    color = kwargs.get("color", "#3498db")

    # Create card frame
    frame = QFrame()
    frame.setMinimumSize(600, 200)
    frame.setMaximumSize(800, 200)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    frame.setProperty('class', 'graphframe')

    frame.setStyleSheet("""
        QFrame {
            background-color: #43B64D;
            color: white;
            border-radius: 15px;
        }
    """)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(10)

    try:
        # Create matplotlib figure
        figure, ax = plt.subplots(figsize=(6, 2))

        # Plot bar chart
        bars = ax.bar(data.keys(), data.values(), color='aliceblue', alpha=0.8, edgecolor='white', linewidth=1.5)

        # Customize chart
        ax.set_title(title, fontsize=12, color='white', fontweight='bold', pad=10)
        ax.set_xlabel("Day", color='white', fontsize=10)
        ax.set_ylabel("Hours", color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=9)
        ax.grid(axis='y', linestyle='--', color='white', alpha=0.3, linewidth=0.5)

        # Set background colors
        figure.patch.set_facecolor('#43B64D')
        ax.set_facecolor('#43B64D')

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.0f}',
                        ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')

        # Set y-axis limit
        max_hours = max(data.values()) if data.values() else 10
        ax.set_ylim(0, max_hours + 5)

        # Tight layout
        figure.tight_layout()

        # Add canvas to frame
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(canvas)

        plt.close(figure)
    except Exception as e:
        print(f"❌ Error creating graph: {e}")
        error_label = QLabel("Could not load attendance graph")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: white;")
        layout.addWidget(error_label)

    return frame