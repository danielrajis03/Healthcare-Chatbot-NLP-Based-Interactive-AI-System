import sqlite3
import datetime

class HealthcareBooking:
    # Constructor to initialize the healthcare booking system with a database connection
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()

    # Setup database with appointments and users tables if they do not exist
    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                time TEXT,
                service_type TEXT,
                professional_name TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone_number TEXT
            )
        ''')
        self.conn.commit()

    # Method to add a user to the database
    def add_user(self, name, phone_number):
        self.cursor.execute("INSERT INTO users (name, phone_number) VALUES (?, ?)", (name, phone_number))
        self.conn.commit()

    # Method to check the availability of an appointment slot
    def check_availability(self, date, time, excluding_appointment_id=None):
        # Check if there's any existing appointment at the given date and time, excluding a specific appointment if provided
        query = "SELECT * FROM appointments WHERE date = ? AND time = ?"
        params = [date, time]
        if excluding_appointment_id:
            query += " AND id != ?"
            params.append(excluding_appointment_id)
        
        self.cursor.execute(query, params)
        appointment = self.cursor.fetchone()
        return appointment is None

    # Method to make an appointment
    def book_appointment(self, user_id, date, time, service_type, professional_name):
        if self.check_availability(date, time):
            try:
                self.cursor.execute(
                    "INSERT INTO appointments (user_id, date, time, service_type, professional_name) VALUES (?, ?, ?, ?, ?)",
                    (user_id, date, time, service_type, professional_name)
                )
                self.conn.commit()
                appointment_id = self.cursor.lastrowid
                return True, f"Your appointment with {professional_name} for {service_type} on {date} at {time} is confirmed. Appointment ID is {appointment_id}.", appointment_id
            except sqlite3.Error as e:
                print("Database error:", e)
                return False, "Sorry, we failed to make an appointment", None
        else:
            return False, "No available slots for the requested time", None

    # Method to get appointment details by ID
    def get_appointment_by_id(self, appointment_id):
        try:
            self.cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
            appointment = self.cursor.fetchone()
            if appointment:
                return appointment
            else:
                return None
        except sqlite3.Error as e:
            print("Database error:", e)
            return None

    # Method to check if an appointment exists
    def appointment_exists(self, appointment_id):
        try:
            self.cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print("Database error:", e)
            return False

    # Method to cancel an appointment
    def cancel_appointment(self, appointment_id):
        try:
            self.cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
            appointment = self.cursor.fetchone()
            if not appointment:
                return False, "Appointment not found"

            self.cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
            self.conn.commit()
            return True, "Your appointment has been successfully cancelled."
        except sqlite3.Error as e:
            print("Database error:", e)
            return False, "Your appointment has not been cancelled."

    # Method to list all appointments for a given user
    def list_appointments(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM appointments WHERE user_id = ?", (user_id,))
            appointments = self.cursor.fetchall()
            return True, appointments
        except sqlite3.Error as e:
            print("Database error:", e)
            return False, []

    # Destructor to close the database connection when the object is destroyed
    def __del__(self):
        self.conn.close()
