from healthcare_booking import HealthcareBooking
import datetime

# Initialize the booking system
db_path = 'healthcare_bookings.db'
booking_system = HealthcareBooking(db_path)

# Example user details
user_id = 1
full_name = "John Doe"
date = "24-11-2024"
time = "12:30"
service_type = "general practitioner"

# Test booking without specifying a professional (automatically assigned)
success, message, appointment_id = booking_system.book_appointment(user_id, date, time, service_type, full_name)
print(f"Success: {success}, Message: '{message}', Appointment ID: {appointment_id}")
