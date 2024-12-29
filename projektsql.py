from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123',
        database='hospital_db'
    )
    return connection

# Root route to give basic API information
@app.route('/')
def home():
    return "Welcome to the Hospital API. Use '/appointments/<patient_id>' or '/rooms/occupied' endpoints."

# API to get all appointments for a specific patient
@app.route('/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT a.Appointment_ID, a.Appointment_Date, a.Appointment_Time, 
           d.First_Name AS Doctor_First_Name, d.Last_Name AS Doctor_Last_Name, 
           n.First_Name AS Nurse_First_Name, n.Last_Name AS Nurse_Last_Name
    FROM Appointment a
    JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
    JOIN Nurse n ON a.Nurse_ID = n.Nurse_ID
    WHERE a.Patient_ID = %s;
    """
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    
    # Convert timedelta or datetime fields to strings
    for appointment in appointments:
        if isinstance(appointment['Appointment_Date'], datetime):
            appointment['Appointment_Date'] = appointment['Appointment_Date'].strftime('%Y-%m-%d')
        if isinstance(appointment['Appointment_Time'], timedelta):
            # Convert timedelta to string, assuming it's a time duration
            appointment['Appointment_Time'] = str(appointment['Appointment_Time'])
    
    conn.close()
    return jsonify(appointments)

# API to get occupied rooms and assigned patients
@app.route('/rooms/occupied', methods=['GET'])
def get_occupied_rooms():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT r.Room_Number, r.Room_Type, r.Availability_Status, 
           p.First_Name, p.Last_Name
    FROM Hospital_Room r
    JOIN Patient p ON r.Room_ID = p.Room_ID
    WHERE r.Availability_Status = 'Occupied';
    """
    cursor.execute(query)
    rooms = cursor.fetchall()
    conn.close()
    return jsonify(rooms)

if __name__ == '__main__':
    app.run(debug=True)
