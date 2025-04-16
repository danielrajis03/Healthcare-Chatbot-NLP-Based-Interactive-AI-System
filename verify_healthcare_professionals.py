import sqlite3

# Connect to the database
conn = sqlite3.connect('healthcare_bookings.db')
cursor = conn.cursor()

# Query and print all the healthcare professionals
cursor.execute("SELECT * FROM healthcare_professionals")
professionals = cursor.fetchall()

print("Healthcare Professionals:")
for professional in professionals:
    print(professional)

# Close the connection
conn.close()
