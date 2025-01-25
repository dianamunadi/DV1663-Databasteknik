# Den här koden är en Python Flask-applikation som 
# fungerar som ett API för att interagera med en sjukhusdatabas
from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime, timedelta

app = Flask(_name_)

# Database connection setup
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='0000',
        database='hospital_db'
    )
    return connection

# Root route to give basic API information
@app.route('/')
def home():
    return "Welcome to the Hospital API. Use '/appointments/<patient_id>', '/rooms/occupied',  '/medical_records/<int:patient_id>', '/patients/<int:patient_id>' or '/rooms/available', endpoints."

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

# API to get details of a specific patient
@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT Patient_ID, First_Name, Last_Name, Date_of_Birth, Address, Phone, Email, 
           Emergency_Contact, Insurance_Details, Room_ID, Nurse_ID, Staff_ID
    FROM Patient
    WHERE Patient_ID = %s;
    """
    cursor.execute(query, (patient_id,))
    patient = cursor.fetchone()
    
    # Convert datetime fields to strings if applicable
    if patient:
        if isinstance(patient.get('Date_of_Birth'), datetime):
            patient['Date_of_Birth'] = patient['Date_of_Birth'].strftime('%Y-%m-%d')
    
    conn.close()
    if patient:
        return jsonify(patient)
    else:
        return jsonify({"error": "Patient not found"}), 404
# API to get all medical records for a specific patient
@app.route('/medical_records/<int:patient_id>', methods=['GET'])
def get_medical_records(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT Record_ID, Date, Diagnosis, Treatment, Prescribed_Medication, Doctor_ID, Nurse_ID
    FROM Medical_Record
    WHERE Patient_ID = %s;
    """
    cursor.execute(query, (patient_id,))
    medical_records = cursor.fetchall()

    # Convert Date fields to strings if applicable
    for record in medical_records:
        if isinstance(record['Date'], datetime):
            record['Date'] = record['Date'].strftime('%Y-%m-%d')

    conn.close()
    return jsonify(medical_records)



@app.route('/rooms/available', methods=['GET'])
def get_available_rooms():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT Room_Number, Room_Type, Availability_Status
    FROM Hospital_Room
    WHERE Availability_Status = 'Available';
    """
    cursor.execute(query)
    rooms = cursor.fetchall()
    conn.close()
    return jsonify(rooms)



if _name_ == '_main_':
    app.run(debug=True)
