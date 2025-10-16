import os
import shutil
import pymysql
import secrets
import string


class Connectdb:
    host = "localhost"
    user = "root"
    password = ""
    database = "lootech"

    # ------------------------------
    # Initialize Automatically
    # ------------------------------
    @staticmethod
    def _initialize():
        """Ensure database and tables exist automatically."""
        Connectdb.ensure_database_exists()
        Connectdb.create_users_table()
        Connectdb.create_employees_table()
        Connectdb.create_deductions_table()
        Connectdb.create_attendance_table()
        Connectdb.create_announcements_table()

    # ------------------------------
    # Connect to Main Database
    # ------------------------------
    @staticmethod
    def connect():
        """Connect to the lootech database."""
        return pymysql.connect(
            host=Connectdb.host,
            user=Connectdb.user,
            password=Connectdb.password,
            database=Connectdb.database
        )

    # ------------------------------
    # Ensure Database Exists
    # ------------------------------
    @staticmethod
    def ensure_database_exists():
        """Create the database if it doesn't exist."""
        try:
            connection = pymysql.connect(
                host=Connectdb.host,
                user=Connectdb.user,
                password=Connectdb.password
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Connectdb.database}")
            connection.close()
            print(f"✅ Database '{Connectdb.database}' is ready.")
        except pymysql.Error as e:
            print(f"❌ Failed to create database '{Connectdb.database}': {e}")

    # ------------------------------
    # Create Users Table
    # ------------------------------
    @staticmethod
    def create_users_table():
        """Create the users table if it doesn't exist."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company VARCHAR(100) NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    role ENUM('admin', 'staff') NOT NULL,
                    passkey VARCHAR(50) NOT NULL
                )
            """)
            connection.commit()
            connection.close()
            print("✅ Table 'users' is ready.")
        except pymysql.Error as e:
            print(f"❌ Error creating users table: {e}")

    # ------------------------------
    # Create Employees Table
    # ------------------------------
    @staticmethod
    def create_employees_table():
        """Create the employees table if it doesn't exist."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE,
                    address VARCHAR(255),
                    company VARCHAR(100),
                    contact VARCHAR(50),
                    job_title VARCHAR(100),
                    salary DECIMAL(10,2) DEFAULT 0.00,
                    employment_status ENUM('active', 'resigned', 'inactive') DEFAULT 'active',
                    photo_path VARCHAR(255)
                )
            """)
            connection.commit()
            connection.close()
            print("✅ Table 'employees' is ready.")
        except pymysql.Error as e:
            print(f"❌ Error creating employees table: {e}")
    @staticmethod
    def create_deductions_table():
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS deductions
                           (deduction_id INT AUTO_INCREMENT PRIMARY KEY,
                            employee_id INT NOT NULL, 
                            deduction_type VARCHAR(255) NOT NULL, 
                            total_amount DECIMAL(10,2) NOT NULL,
                            installment_count INT NOT NULL DEFAULT 1,
                            amount_paid DECIMAL(10, 2) DEFAULT 0,
                            status ENUM('pending', 'partial', 'paid') DEFAULT 'pending',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            FOREIGN KEY(employee_id) REFERENCES employees(employee_id))""")
            connection.commit()
            connection.close()
            print("✅ Table 'deductions' ready")
        except pymysql.MySQLError as e:
            print(f"❌ Error creating 'deductions' table: {e}")

    @staticmethod
    def create_attendance_table():
        """Create the attendance table if it doesn't exist."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    sunday DECIMAL(4, 2) DEFAULT 0.0,
    monday DECIMAL(4, 2) DEFAULT 0.0,
    tuesday DECIMAL(4, 2) DEFAULT 0.0,
    wednesday DECIMAL(4, 2) DEFAULT 0.0,
    thursday DECIMAL(4, 2) DEFAULT 0.0,
    friday DECIMAL(4, 2) DEFAULT 0.0,
    saturday DECIMAL(4, 2) DEFAULT 0.0,
    total_hours DECIMAL(5, 2) DEFAULT 0.0,
    payroll_status ENUM('draft', 'pending', 'approved') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (employee_id, start_date, end_date)
)    """)
            connection.commit()
            connection.close()
            print("✅ Table 'attendance' is ready.")
        except Exception as e:
            print(f"❌ Error creating attendance table: {e}")

    @staticmethod
    def create_announcements_table():
        """Automatically create announcements table if it doesn't exist"""
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    company VARCHAR(255) NOT NULL,  -- company name
    type VARCHAR(50) DEFAULT 'info',
    category VARCHAR(50) DEFAULT 'general',  -- 'attendance' or 'general'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unread'
)
            """)
            connection.commit()
            connection.close()
            print("✅ Announcements table checked/created successfully!")
        except Exception as e:
            print(f"❌ Error creating announcements table: {e}")

    # ------------------------------
    # Insert User (Signup)
    # ------------------------------
    @staticmethod
    def insert_user(username, password, company, role, passkey=None):
        """Insert a new user (admin or staff)."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()

            # Check duplicate username
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                connection.close()
                return "duplicate", "Username already exists."

            if role.lower() == "admin":
                # Generate passkey for admin
                alphabet = string.ascii_letters + string.digits
                passkey = ''.join(secrets.choice(alphabet) for _ in range(10))
            elif role.lower() == "staff":
                # Verify admin passkey
                cursor.execute("SELECT company FROM users WHERE passkey=%s AND role='admin'", (passkey,))
                admin_company = cursor.fetchone()
                if not admin_company:
                    connection.close()
                    return "invalid_passkey", "Invalid passkey."
                company = admin_company[0]

            # Insert user
            cursor.execute("""
                INSERT INTO users (company, username, password, role, passkey)
                VALUES (%s, %s, %s, %s, %s)
            """, (company, username, password, role.lower(), passkey))
            connection.commit()
            connection.close()

            if role.lower() == "admin":
                return "success", passkey
            return "success", None

        except pymysql.Error as e:
            return "error", str(e)

    # ------------------------------
    # Login
    # ------------------------------
    @staticmethod
    def login_user(username, password):
        """Validate credentials and return role, passkey, company if valid."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT role, passkey, company FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            result = cursor.fetchone()
            connection.close()
            if result:
                return result
            return "invalid"
        except pymysql.Error as e:
            print("Database error:", e)
            return None

    # ------------------------------
    # Add Employee
    # ------------------------------
    @staticmethod
    def add_employee(first_name, last_name, email, address, company, contact, job_title, salary,
                     employment_status="active", photo_path=None):
        """Add a new employee record."""
        try:
            photo_dir = "employeePic"
            os.makedirs(photo_dir, exist_ok=True)
            saved_photo_path = None
            if photo_path and os.path.exists(photo_path):
                ext = os.path.splitext(photo_path)[1]
                saved_photo_path = os.path.join(photo_dir, f"{first_name}_{last_name}{ext}")
                if not os.path.exists(saved_photo_path):
                    shutil.copy(photo_path, saved_photo_path)

            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO employees
                (first_name, last_name, email, address, company, contact, job_title, salary,
                 employment_status, photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, address, company, contact, job_title, salary,
                  employment_status, saved_photo_path))
            connection.commit()
            connection.close()
            print(f"✅ Employee '{first_name} {last_name}' added successfully.")
            return "success"

        except pymysql.IntegrityError:
            print("❌ Error: Employee email already exists.")
            return "duplicate"
        except Exception as e:
            print(f"❌ Error inserting employee: {e}")
            return "error"

    # =====================================================
    # Get Employees by Company (simpler fetch)
    # =====================================================
    @staticmethod
    def get_employees_by_company(company_name):
        """Fetch employees belonging to a specific company."""
        try:
            connection = Connectdb.connect()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                               SELECT employee_id,
                                      first_name,
                                      last_name,
                                      email,
                                      job_title,
                                      salary,
                                      employment_status,
                                      photo_path
                               FROM employees
                               WHERE company = %s
                               ORDER BY last_name, first_name
                               """, (company_name,))
                rows = cursor.fetchall()
            connection.close()
            return rows
        except Exception as e:
            print(f"❌ Error fetching employees: {e}")
            return []

    # =====================================================
    # Fetch employees (for EmployeeCard display)
    # =====================================================
    @staticmethod
    def fetch_employees(company_name):
        """Fetch employees formatted for UI cards."""
        try:
            connection = Connectdb.connect()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                               SELECT employee_id, first_name, last_name, job_title, photo_path, employment_status
                               FROM employees
                               WHERE company = %s
                               """, (company_name,))
                rows = cursor.fetchall()

            employees = []
            for row in rows:
                name = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
                job = row.get('job_title') or "N/A"
                image = row.get('photo_path') or "stylesAndPic/profile-user.png"
                status = row.get('employment_status', 'active').capitalize()
                employees.append({
                    "id": row.get("employee_id"),
                    "name": name,
                    "job": job,
                    "image": image,
                    "status": status
                })
            connection.close()
            return employees
        except pymysql.Error as e:
            print(f"❌ DB Fetch Error: {e}")
            return []

    # =====================================================
    # Update employee (with employment_status)
    # =====================================================
    @staticmethod
    def update_employee(employee_id, first_name, last_name, email, contact,
                        address, job_title, salary, employment_status, photo_path):
        try:
            connection = Connectdb.connect()
            with connection.cursor() as cursor:
                query = """
                        UPDATE employees
                        SET first_name=%s,
                            last_name=%s,
                            email=%s,
                            contact=%s,
                            address=%s,
                            job_title=%s,
                            salary=%s,
                            employment_status=%s,
                            photo_path=%s
                        WHERE employee_id = %s \
                        """
                cursor.execute(query, (
                    first_name, last_name, email, contact, address,
                    job_title, salary, employment_status, photo_path, employee_id
                ))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"❌ Error updating employee: {e}")
            return False

    # =====================================================
    # Get employee by ID
    # =====================================================
    @staticmethod
    def get_employee_by_id(employee_id, company):
        try:
            connection = Connectdb.connect()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM employees WHERE employee_id = %s AND company = %s",
                    (employee_id, company)
                )
                row = cursor.fetchone()
            connection.close()
            return row
        except Exception as e:
            print(f"❌ Error fetching employee by ID: {e}")
            return None

    # =====================================================
    # Add employee (with employment_status)
    # =====================================================
    @staticmethod
    def add_employee(first_name, last_name, email, contact,
                     address, job_title, salary, employment_status, company, photo_path):
        try:
            connection = Connectdb.connect()
            with connection.cursor() as cursor:
                query = """
                        INSERT INTO employees
                        (first_name, last_name, email, contact, address, job_title, salary, employment_status, company, \
                         photo_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                cursor.execute(query, (
                    first_name, last_name, email, contact, address,
                    job_title, salary, employment_status, company, photo_path
                ))
            connection.commit()
            connection.close()
            return "success"
        except Exception as e:
            print(f"❌ Error adding employee: {e}")
            return str(e)

    # ---------- ADD DEDUCTION ----------
    @staticmethod
    def add_deduction(employee_id, deduction_type, total_amount, times_to_pay):
        conn = Connectdb.get_connection()
        if not conn:
            return "fail"
        try:
            with conn.cursor() as cursor:
                sql = """
                      INSERT INTO deductions (employee_id, deduction_type, total_amount, installment_count)
                      VALUES (%s, %s, %s, %s) \
                      """
                cursor.execute(sql, (employee_id, deduction_type, total_amount, times_to_pay))
                conn.commit()
                return "success"
        except Exception as e:
            print(f"❌ add_deduction failed: {e}")
            return "fail"
        finally:
            conn.close()

    # ---------- UPDATE DEDUCTION PAYMENT ----------
    @staticmethod
    def update_deduction_payment(deduction_id, amount_paid):
        conn = Connectdb.get_connection()
        if not conn:
            return "fail"
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT total_amount FROM deductions WHERE deduction_id=%s", (deduction_id,))
                row = cursor.fetchone()
                if not row:
                    return "not_found"

                total_amount = float(row['total_amount'])
                status = "paid" if amount_paid >= total_amount else "partial"

                cursor.execute("""
                               UPDATE deductions
                               SET amount_paid=%s,
                                   status=%s,
                                   updated_at=NOW()
                               WHERE deduction_id = %s
                               """, (amount_paid, status, deduction_id))
                conn.commit()
                return "success"
        except Exception as e:
            print(f"❌ Error updating deduction payment: {e}")
            return "error"
        finally:
            conn.close()

    # ---------- GET DEDUCTIONS FOR AN EMPLOYEE ----------
    @staticmethod
    def get_deductions_for_employee(employee_id):
        """Fetch all deductions of a specific employee, including payments info"""
        try:
            connection = Connectdb.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)  # use DictCursor

            query = """
                    SELECT deduction_id, \
                           deduction_type, \
                           total_amount, \
                           installment_count        AS times_to_pay, \
                           amount_paid, \
                           status, \
                           COALESCE(amount_paid, 0) AS amount_paid, \
                           CASE \
                               WHEN installment_count IS NULL OR installment_count = 0 THEN 'every payroll' \
                               ELSE installment_count \
                               END                  AS times_to_pay
                    FROM deductions
                    WHERE employee_id = %s
                    ORDER BY created_at DESC \
                    """
            cursor.execute(query, (employee_id,))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()

            # Add calculated field: how many times paid
            for row in rows:
                if row['times_to_pay'] == 'every payroll':
                    row['payments_made'] = 'N/A'
                else:
                    row['payments_made'] = min(row.get('amount_paid', 0), row['times_to_pay'])

            return rows

        except Exception as e:
            print(f"❌ Error fetching deductions: {e}")
            return []

    @staticmethod
    def get_employees_with_deductions(companyName):
        conn = Connectdb.get_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                sql = """
                      SELECT e.employee_id,
                             CONCAT(e.first_name, ' ', e.last_name) AS name,
                             e.photo_path,
                             d.deduction_type,
                             d.total_amount
                      FROM employees e
                               INNER JOIN deductions d ON e.employee_id = d.employee_id
                      WHERE e.company = %s
                        AND d.status <> 'paid'
                      ORDER BY e.first_name, e.last_name, d.created_at DESC \
                      """
                cursor.execute(sql, (companyName,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ get_employees_with_deductions failed: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_employees_for_selection(companyName):
        conn = Connectdb.get_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                sql = "SELECT employee_id, first_name, last_name FROM employees WHERE company=%s"
                cursor.execute(sql, (companyName,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ get_employees_for_selection failed: {e}")
            return []
        finally:
            conn.close()

    # ------------------------------
    # Test Connection
    # ------------------------------
    @staticmethod
    def test_connection():
        """Test connection to the database."""
        try:
            connection = Connectdb.connect()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            connection.close()
            print(f"✅ Successfully connected to database: {db_name}")
        except pymysql.Error as e:
            print(f"❌ Database connection failed: {e}")

    @staticmethod
    def get_connection():
        try:
            conn = pymysql.connect(
                host=Connectdb.host,
                user=Connectdb.user,
                password=Connectdb.password,
                database=Connectdb.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        except Exception as e:
            print(f"❌ DB connection failed: {e}")
            return None


# ------------------ Add Announcement ------------------
    @staticmethod
    def add_announcement(title, message, company, category="general", type="info", status="unread"):
        """
        Add a new announcement.
        :param title: string, title of the announcement
        :param message: string, content of the message
        :param company: string, company name
        :param category: "attendance" or "general"
        :param type: type of message e.g., info, warning
        :param status: unread/read
        :return: True if added successfully, False otherwise
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO announcements (title, message, company, category, type, status)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               """, (title, message, company, category, type, status))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"❌ Error adding announcement: {e}")
            return False

    # ------------------ Get Announcements ------------------
    @staticmethod
    def get_announcements(company, category=None):
        """
        Fetch announcements for a specific company with optional category.

        :param company: the company to filter by
        :param category: optional, filter by category
        :return: list of dicts
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM announcements WHERE company=%s"
                params = [company]

                if category:
                    query += " AND category=%s"
                    params.append(category)

                query += " ORDER BY created_at DESC"
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
            connection.close()
            return rows
        except Exception as e:
            print(f"Error fetching announcements: {e}")
            return []

    # ------------------ Get General Announcements ------------------
    def get_general_announcements(self, company):
        """
        Return all general announcements for a given company.
        :param company: string, company name
        :return: list of dicts
        """
        return self.get_announcements(category="general", company=company)



    # ---------------- Attendance ----------------
    @staticmethod
    def get_attendance_weeks(companyName):
        """
        Get all attendance weeks for a company with summary info.
        Returns list of dicts with week_start, week_end, total_hours, status
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT DISTINCT a.start_date                          as week_start,
                                               a.end_date                            as week_end,
                                               SUM(a.monday + a.tuesday + a.wednesday + a.thursday +
                                                   a.friday + a.saturday + a.sunday) as total_hours,
                                               a.payroll_status                      as status
                               FROM attendance a
                                        JOIN employees e ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                               GROUP BY a.start_date, a.end_date, a.payroll_status
                               ORDER BY a.start_date DESC
                               """, (companyName,))
                rows = cursor.fetchall()
            connection.close()
            return rows
        except Exception as e:
            print(f"❌ Error fetching attendance weeks: {e}")
            return []

    @staticmethod
    def get_attendance_for_week(companyName, week_start, week_end):
        """
        Get detailed attendance data for a specific week.
        Returns list of dicts with employee info and daily hours.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT e.employee_id,
                                      CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                                      e.first_name,
                                      e.last_name,
                                      a.monday,
                                      a.tuesday,
                                      a.wednesday,
                                      a.thursday,
                                      a.friday,
                                      a.saturday,
                                      a.sunday,
                                      (a.monday + a.tuesday + a.wednesday + a.thursday +
                                       a.friday + a.saturday + a.sunday)     as total_hours,
                                      a.payroll_status                       as status
                               FROM employees e
                                        LEFT JOIN attendance a ON e.employee_id = a.employee_id
                                   AND a.start_date = %s AND a.end_date = %s
                               WHERE e.company = %s
                               ORDER BY e.last_name, e.first_name
                               """, (week_start, week_end, companyName))
                rows = cursor.fetchall()
            connection.close()
            return rows
        except Exception as e:
            print(f"❌ Error fetching attendance for week: {e}")
            return []

    @staticmethod
    def check_attendance_week_exists(companyName, start_date, end_date):
        """
        Check if attendance records exist for a specific week.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM attendance a
                                   JOIN employees e
                               ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                                 AND a.start_date = %s
                                 AND a.end_date = %s
                               """, (companyName, start_date, end_date))
                result = cursor.fetchone()
            connection.close()
            return result['count'] > 0 if result else False
        except Exception as e:
            print(f"❌ Error checking attendance week: {e}")
            return False

    @staticmethod
    def create_attendance_for_week(companyName, start_date, end_date):
        """
        Create blank attendance records for all employees in a company for a specific week.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                # Get all active employees
                cursor.execute("""
                               SELECT employee_id
                               FROM employees
                               WHERE company = %s
                                 AND employment_status = 'active'
                               """, (companyName,))
                employees = cursor.fetchall()

                # Create attendance record for each employee
                for emp in employees:
                    cursor.execute("""
                                   INSERT INTO attendance
                                   (employee_id, start_date, end_date, monday, tuesday, wednesday,
                                    thursday, friday, saturday, sunday, total_hours, payroll_status)
                                   VALUES (%s, %s, %s, 0, 0, 0, 0, 0, 0, 0, 0, 'draft') ON DUPLICATE KEY
                                   UPDATE
                                       payroll_status =
                                   VALUES (payroll_status)
                                   """, (emp['employee_id'], start_date, end_date))

            connection.commit()
            connection.close()
            print(f"✅ Created attendance for {len(employees)} employees")
            return True
        except Exception as e:
            print(f"❌ Error creating attendance for week: {e}")
            return False

    @staticmethod
    def save_attendance_for_week(companyName, week_start, week_end, attendance_data, status='draft'):
        """
        Save/update attendance data for a specific week.

        attendance_data: dict with employee_id as key and hours dict as value
        Example: {
            1: {'monday': 8, 'tuesday': 8, ...},
            2: {'monday': 7.5, 'tuesday': 8, ...}
        }
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                for employee_id, hours in attendance_data.items():
                    total = sum([
                        float(hours.get('monday', 0)),
                        float(hours.get('tuesday', 0)),
                        float(hours.get('wednesday', 0)),
                        float(hours.get('thursday', 0)),
                        float(hours.get('friday', 0)),
                        float(hours.get('saturday', 0)),
                        float(hours.get('sunday', 0))
                    ])

                    cursor.execute("""
                                   INSERT INTO attendance
                                   (employee_id, start_date, end_date, monday, tuesday, wednesday,
                                    thursday, friday, saturday, sunday, total_hours, payroll_status)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                                   UPDATE
                                       monday =
                                   VALUES (monday), tuesday =
                                   VALUES (tuesday), wednesday =
                                   VALUES (wednesday), thursday =
                                   VALUES (thursday), friday =
                                   VALUES (friday), saturday =
                                   VALUES (saturday), sunday =
                                   VALUES (sunday), total_hours =
                                   VALUES (total_hours), payroll_status =
                                   VALUES (payroll_status)
                                   """, (
                                       employee_id, week_start, week_end,
                                       hours.get('monday', 0),
                                       hours.get('tuesday', 0),
                                       hours.get('wednesday', 0),
                                       hours.get('thursday', 0),
                                       hours.get('friday', 0),
                                       hours.get('saturday', 0),
                                       hours.get('sunday', 0),
                                       total,
                                       status
                                   ))

            connection.commit()
            connection.close()
            print(f"✅ Saved attendance for week {week_start}")
            return True
        except Exception as e:
            print(f"❌ Error saving attendance: {e}")
            return False

    @staticmethod
    def approve_attendance(companyName, week_start, week_end):
        """
        Approve attendance and generate payroll records.
        Changes status from 'pending' to 'approved' and processes deduction payments.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                # Update attendance status to approved
                cursor.execute("""
                               UPDATE attendance a
                                   JOIN employees e
                               ON a.employee_id = e.employee_id
                                   SET a.payroll_status = 'approved'
                               WHERE e.company = %s
                                 AND a.start_date = %s
                                 AND a.end_date = %s
                                 AND a.payroll_status = 'pending'
                               """, (companyName, week_start, week_end))

                # Check if any rows were updated
                if cursor.rowcount == 0:
                    connection.close()
                    return False

                connection.commit()
            connection.close()

            # Process deduction payments after approval
            Connectdb.process_deduction_payments(companyName, week_start)

            print(f"✅ Attendance approved for week {week_start}")
            return True

        except Exception as e:
            print(f"❌ Error approving attendance: {e}")
            return False

    @staticmethod
    def reject_attendance(companyName, week_start, week_end):
        """
        Reject attendance and send it back to draft status.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               UPDATE attendance a
                                   JOIN employees e
                               ON a.employee_id = e.employee_id
                                   SET a.payroll_status = 'draft'
                               WHERE e.company = %s
                                 AND a.start_date = %s
                                 AND a.end_date = %s
                                 AND a.payroll_status = 'pending'
                               """, (companyName, week_start, week_end))

                connection.commit()
            connection.close()

            print(f"✅ Attendance rejected for week {week_start}")
            return True

        except Exception as e:
            print(f"❌ Error rejecting attendance: {e}")
            return False

    @staticmethod
    def process_deduction_payments(companyName, week_start):
        """
        Process deduction payments for approved payroll.
        This is called automatically when attendance is approved.
        Updates the amount_paid and status of deductions.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                # Get all employees with deductions for this week's payroll
                cursor.execute("""
                               SELECT DISTINCT d.deduction_id,
                                               d.employee_id,
                                               d.total_amount,
                                               d.installment_count,
                                               COALESCE(d.amount_paid, 0) as amount_paid,
                                               d.status
                               FROM deductions d
                                        JOIN employees e ON d.employee_id = e.employee_id
                                        JOIN attendance a ON e.employee_id = a.employee_id
                               WHERE e.company = %s
                                 AND a.start_date = %s
                                 AND a.payroll_status = 'approved'
                                 AND d.status != 'paid'
                               """, (companyName, week_start))

                deductions = cursor.fetchall()

                for ded in deductions:
                    deduction_id = ded['deduction_id']
                    total_amount = float(ded['total_amount'])
                    installment_count = int(ded['installment_count']) if ded['installment_count'] else 0
                    amount_paid = float(ded['amount_paid'])

                    # Calculate payment amount
                    if installment_count == 0:  # Every payroll - deduct full amount each time
                        payment = total_amount
                        new_amount_paid = amount_paid + payment
                        # For "every payroll", we just increment but never mark as "paid"
                        # unless you want a different logic
                        new_status = 'partial'
                    else:
                        # Installment-based: divide total by number of installments
                        payment = total_amount / installment_count
                        new_amount_paid = amount_paid + payment

                        # Determine new status
                        if new_amount_paid >= total_amount:
                            new_status = 'paid'
                            new_amount_paid = total_amount  # Cap at total amount
                        else:
                            new_status = 'partial'

                    # Update deduction
                    cursor.execute("""
                                   UPDATE deductions
                                   SET amount_paid = %s,
                                       status      = %s,
                                       updated_at  = NOW()
                                   WHERE deduction_id = %s
                                   """, (new_amount_paid, new_status, deduction_id))

                connection.commit()
            connection.close()

            print(f"✅ Processed {len(deductions)} deduction payments for week {week_start}")
            return True

        except Exception as e:
            print(f"❌ Error processing deduction payments: {e}")
            return False

    @staticmethod
    def get_payroll_summary(companyName):
        """
        Get payroll summary for all approved attendance weeks.
        Now properly calculates "every payroll" deductions.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                # Get all approved attendance weeks
                cursor.execute("""
                               SELECT DISTINCT a.start_date as week_start,
                                               a.end_date   as week_end
                               FROM attendance a
                                        JOIN employees e ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                                 AND a.payroll_status = 'approved'
                               ORDER BY a.start_date DESC
                               """, (companyName,))
                weeks = cursor.fetchall()

            results = []
            for week in weeks:
                week_start = week['week_start']
                week_end = week['week_end']

                # Calculate totals for this week
                with connection.cursor() as cursor:
                    cursor.execute("""
                                   SELECT e.employee_id,
                                          a.total_hours,
                                          e.salary
                                   FROM attendance a
                                            JOIN employees e ON a.employee_id = e.employee_id
                                   WHERE e.company = %s
                                     AND a.start_date = %s
                                     AND a.end_date = %s
                                     AND a.payroll_status = 'approved'
                                   """, (companyName, week_start, week_end))
                    employees = cursor.fetchall()

                total_gross = 0.0
                total_deductions = 0.0

                for emp in employees:
                    # Calculate gross pay
                    gross = float(emp['total_hours']) * float(emp['salary'])
                    total_gross += gross

                    # Calculate deductions for this employee
                    with connection.cursor() as cursor:
                        cursor.execute("""
                                       SELECT total_amount,
                                              installment_count,
                                              COALESCE(amount_paid, 0) as amount_paid,
                                              status
                                       FROM deductions
                                       WHERE employee_id = %s
                                         AND status != 'paid'
                                       """, (emp['employee_id'],))
                        deductions = cursor.fetchall()

                    for ded in deductions:
                        total_amount = float(ded['total_amount'])
                        installment_count = int(ded['installment_count']) if ded['installment_count'] else 0
                        amount_paid = float(ded.get('amount_paid', 0))

                        if installment_count == 0:
                            # "Every payroll" - deduct full amount each time
                            deduction_amount = total_amount
                        else:
                            # Installment - calculate per payroll
                            remaining = total_amount - amount_paid
                            deduction_amount = min(total_amount / installment_count, remaining)

                        total_deductions += deduction_amount

                total_net = total_gross - total_deductions

                # Format dates
                if hasattr(week_start, 'strftime'):
                    week_start = week_start.strftime('%Y-%m-%d')
                if hasattr(week_end, 'strftime'):
                    week_end = week_end.strftime('%Y-%m-%d')

                results.append({
                    'week_start': week_start,
                    'week_end': week_end,
                    'total_gross_pay': total_gross,
                    'total_deductions': total_deductions,
                    'total_net_pay': total_net
                })

            connection.close()
            return results

        except Exception as e:
            print(f"❌ Error fetching payroll summary: {e}")
            return []

    @staticmethod
    def get_payroll_details(week_start, companyName):
        """
        Get detailed payroll information for a specific week.
        Now properly calculates "every payroll" deductions.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT e.employee_id,
                                      CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                                      a.total_hours,
                                      e.salary                               as daily_rate
                               FROM attendance a
                                        JOIN employees e ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                                 AND a.start_date = %s
                                 AND a.payroll_status = 'approved'
                               ORDER BY e.last_name, e.first_name
                               """, (companyName, week_start))
                employees = cursor.fetchall()

            results = []
            for emp in employees:
                employee_id = emp['employee_id']
                total_hours = float(emp['total_hours'])
                daily_rate = float(emp['daily_rate'])
                gross_pay = total_hours * daily_rate

                # Calculate deductions for this employee
                with connection.cursor() as cursor:
                    cursor.execute("""
                                   SELECT total_amount,
                                          installment_count,
                                          COALESCE(amount_paid, 0) as amount_paid,
                                          status
                                   FROM deductions
                                   WHERE employee_id = %s
                                     AND status != 'paid'
                                   """, (employee_id,))
                    deductions = cursor.fetchall()

                total_deduction = 0.0
                for ded in deductions:
                    total_amount = float(ded['total_amount'])
                    installment_count = int(ded['installment_count']) if ded['installment_count'] else 0
                    amount_paid = float(ded.get('amount_paid', 0))

                    if installment_count == 0:
                        # "Every payroll" - deduct full amount each time
                        deduction_amount = total_amount
                    else:
                        # Installment - calculate per payroll
                        remaining = total_amount - amount_paid
                        deduction_amount = min(total_amount / installment_count, remaining)

                    total_deduction += deduction_amount

                net_pay = gross_pay - total_deduction

                results.append({
                    'employee_name': emp['employee_name'],
                    'employee_id': employee_id,
                    'total_hours': total_hours,
                    'daily_rate': daily_rate,
                    'gross_pay': gross_pay,
                    'deductions': total_deduction,
                    'net_pay': net_pay
                })

            connection.close()
            return results

        except Exception as e:
            print(f"❌ Error fetching payroll details: {e}")
            return []

    @staticmethod
    def delete_deduction(deduction_id):
        """
        Delete a deduction from the database.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               DELETE
                               FROM deductions
                               WHERE deduction_id = %s
                               """, (deduction_id,))
                connection.commit()
            connection.close()
            print(f"✅ Deduction {deduction_id} deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting deduction: {e}")
            return False

    @staticmethod
    def get_latest_attendance_for_dashboard(companyName):
        """
        Get the most recent week's total hours per day for dashboard graph.
        Returns dict like: {'Mon': 40, 'Tue': 38, 'Wed': 42, ...}
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT COALESCE(SUM(a.monday), 0)    as monday,
                                      COALESCE(SUM(a.tuesday), 0)   as tuesday,
                                      COALESCE(SUM(a.wednesday), 0) as wednesday,
                                      COALESCE(SUM(a.thursday), 0)  as thursday,
                                      COALESCE(SUM(a.friday), 0)    as friday,
                                      COALESCE(SUM(a.saturday), 0)  as saturday,
                                      COALESCE(SUM(a.sunday), 0)    as sunday
                               FROM attendance a
                                        JOIN employees e ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                                 AND a.start_date = (SELECT MAX(start_date)
                                                     FROM attendance a2
                                                              JOIN employees e2 ON a2.employee_id = e2.employee_id
                                                     WHERE e2.company = %s)
                               """, (companyName, companyName))
                result = cursor.fetchone()
            connection.close()

            if result:
                return {
                    'Mon': float(result.get('monday', 0)),
                    'Tue': float(result.get('tuesday', 0)),
                    'Wed': float(result.get('wednesday', 0)),
                    'Thu': float(result.get('thursday', 0)),
                    'Fri': float(result.get('friday', 0)),
                    'Sat': float(result.get('saturday', 0)),
                    'Sun': float(result.get('sunday', 0))
                }
            return {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0}
        except Exception as e:
            print(f"❌ Error fetching latest attendance: {e}")
            return {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0}

    @staticmethod
    def verify_passkey(passkey):
        """
        Verify if a passkey exists and return the associated company.
        Returns (True, company_name) if valid, (False, None) if invalid.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT company
                               FROM users
                               WHERE passkey = %s
                                 AND role = 'admin'
                               """, (passkey,))
                result = cursor.fetchone()
            connection.close()

            if result:
                return True, result['company']
            return False, None
        except Exception as e:
            print(f"❌ Error verifying passkey: {e}")
            return False, None

    @staticmethod
    def update_deduction(deduction_id, deduction_type, total_amount, installment_count):
        """
        Update an existing deduction.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               UPDATE deductions
                               SET deduction_type    = %s,
                                   total_amount      = %s,
                                   installment_count = %s,
                                   updated_at        = NOW()
                               WHERE deduction_id = %s
                               """, (deduction_type, total_amount, installment_count, deduction_id))
                connection.commit()
            connection.close()
            print(f"✅ Deduction {deduction_id} updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error updating deduction: {e}")
            return False

    @staticmethod
    def get_deduction_by_id(deduction_id):
        """
        Get a single deduction by ID.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT deduction_id,
                                      employee_id,
                                      deduction_type,
                                      total_amount,
                                      installment_count,
                                      COALESCE(amount_paid, 0) as amount_paid,
                                      status
                               FROM deductions
                               WHERE deduction_id = %s
                               """, (deduction_id,))
                result = cursor.fetchone()
            connection.close()
            return result
        except Exception as e:
            print(f"❌ Error fetching deduction: {e}")
            return None

    @staticmethod
    def get_employee_deductions_summary(employee_id):
        """
        Get the total remaining deductions for an employee.
        Returns the sum of all unpaid/partial deductions.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT COALESCE(SUM(total_amount - COALESCE(amount_paid, 0)), 0) as total_remaining
                               FROM deductions
                               WHERE employee_id = %s
                                 AND status != 'paid'
                               """, (employee_id,))
                result = cursor.fetchone()
            connection.close()
            return float(result['total_remaining']) if result else 0.0
        except Exception as e:
            print(f"âŒ Error fetching employee deductions summary: {e}")
            return 0.0

    @staticmethod
    def get_pending_drafts_count(companyName):
        """
        Get count of pending draft attendance records for dashboard.
        """
        try:
            connection = Connectdb.get_connection()
            with connection.cursor() as cursor:
                # ✅ FIX: Changed 'week_start' to 'start_date' (correct column name)
                cursor.execute("""
                               SELECT COUNT(DISTINCT start_date) as draft_count
                               FROM attendance a
                                        JOIN employees e ON a.employee_id = e.employee_id
                               WHERE e.company = %s
                                 AND a.payroll_status = 'draft'
                               """, (companyName,))
                result = cursor.fetchone()
            connection.close()
            return result['draft_count'] if result else 0
        except Exception as e:
            print(f"❌ Error fetching pending drafts count: {e}")
            return 0

# ✅ Automatically initialize on import
Connectdb._initialize()
Connectdb.test_connection()
