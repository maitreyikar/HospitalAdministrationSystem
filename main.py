from flask import *
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'sjhuefbyuUGgyt3874'
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MacbookAirm1',
    'database': 'dbmsproject'
}

@app.route('/login/<user_type>')
def login(user_type):
    msg = ""
    if request.args.get("username"):
        username = request.args.get("username")
        password = request.args.get("password")
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        query = f'select * from {user_type} where {user_type[0]}_id = %s and password = %s'
        cursor.execute(query, (username, password))

        account = cursor.fetchone()
        cursor.close()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['type'] = user_type
            return redirect(f'/home/{user_type}/{account[1]}')
        else:
            msg = 'Incorrect username or password.'

    return render_template(f"log_{user_type[:3]}.html", msg=msg)

@app.route("/home/<user_type>/<user_name>")
def home(user_type, user_name):
    if "loggedin" in session:
        return render_template(f"home_{user_type[:3]}.html", type1=user_type,name=user_name)
    else:
        return redirect(f"/login/{user_type}")

@app.route("/home/<user_type>/<user_name>/activeAppointments")
def doc_appt(user_type, user_name):
    if "loggedin" in session:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        if user_type == "doctor":
            doctor_id = session['id']
            if doctor_id:
                query = "SELECT A_ID,date,scheduled_appointments.P_ID,name,age,start_time FROM patient,scheduled_appointments WHERE scheduled_appointments.P_ID=patient.p_id and scheduled_appointments.status = 'Scheduled' AND scheduled_appointments.D_ID = %s"
                cursor.execute(query, (doctor_id,))
                appointments = cursor.fetchall()
                conn.close()
                return render_template("doctor_appointments.html",user_type=user_type,user_name=user_name, appointments=appointments)
            else:
                return "Invalid doctor ID" 
        else:
            return "Invalid user type" 
    else:
        return redirect(f"/login/{user_type}")
@app.route("/home/<user_type>/<user_name>/activeAppointments/Prescription/<aid>")
def prescrip(user_type, user_name, aid):
    if "loggedin" in session:
        if user_type == "doctor":
            doctor_id = session['id']
            if doctor_id:
                return render_template("prescription.html", a_id=aid,user_type=user_type,user_name=user_name)
            else:
                return "Invalid doctor ID" 
        else:
            return "Invalid user type" 
    else:
        return redirect(f"/login/{user_type}")
    
@app.route("/home/<user_type>/<user_name>/activeAppointments/Prescription/<aid>/submit", methods=["POST"])
def submit(user_type, user_name, aid):
    if "loggedin" in session:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        if user_type == "doctor":
            doctor_id = session['id']
            if doctor_id:
                if request.method == "POST":
                    symptoms = request.form["symptoms"]
                    diagnosis = request.form["diagnosis"]
                    prescription = request.form["prescription"]
                    query1 = "UPDATE Scheduled_Appointments SET status = 'Completed' WHERE A_ID = %s"
                    cursor.execute(query1, (aid,))
                    query2 = "INSERT INTO Appointment_Summary (A_ID, Symptoms, Diagnosis, Prescription) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query2, (aid, symptoms, diagnosis, prescription))
                    conn.commit()
                    conn.close()
                    return redirect(f"/home/{user_type}/{user_name}")
            else:
                return "Invalid doctor ID"
        else:
            return "Invalid user type"
    else:
        return redirect(f"/login/{user_type}")

@app.route("/home/<user_type>/<user_name>/patientMedicalHistory")
def med_hist(user_type, user_name):
    if "loggedin" in session:
        if request.args.get("ptid"):
            ptid = request.args.get("ptid")
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor()
            query = "SELECT name, date, health_condition, treatment, type FROM patient, medical_history WHERE medical_history.P_ID = %s and patient.p_id = %s"
            cursor.execute(query, (ptid, ptid))
            history = cursor.fetchall()
            conn.close()
            if history:
                return render_template("med_history.html", user_type=user_type,user_name=user_name, history=history)
        return render_template("med_history.html", user_type=user_type,user_name=user_name, history=[])

    else:
        return redirect(f"/login/{user_type}")

@app.route("/home/<user_type>/<user_name>/requestedAppointments")
def req_appt(user_type, user_name):
    if "loggedin" in session:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        if user_type == "receptionist":
            recep_id = session['id']
            if recep_id:
                query = "SELECT * FROM requested_appointment"
                cursor.execute(query,)
                requested = cursor.fetchall()
                conn.close()
                return render_template("requested_appointment.html",user_type=user_type,user_name=user_name, requested=requested)
            else:
                return "Invalid Receptionist ID" 
        else:
            return "Invalid user type" 
    else:
        return redirect(f"/login/{user_type}")

@app.route("/home/<user_type>/<user_name>/requestedAppointments/fixappt/<d_id>/<p_id>")
def fix_appointment(user_type, user_name, d_id, p_id):
    if "loggedin" in session:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        if user_type == "receptionist":
            recep_id = session['id']
            if recep_id:
                query = "SELECT P_ID,date,start_time,end_time,status FROM scheduled_appointments WHERE D_ID=%s"
                cursor.execute(query,(d_id,))
                doc_schedule = cursor.fetchall()
                conn.close()
                return render_template("fixappt.html",doc_schedule=doc_schedule,user_type=user_type,user_name=user_name, d_id=d_id, p_id=p_id)
            else:
                return "Invalid Receptionist ID" 
        else:
            return "Invalid user type" 
    else:
        return redirect(f"/login/{user_type}")
    
@app.route("/home/<user_type>/<user_name>/requestedAppointments/fixappt/<d_id>/<p_id>/add_appointment", methods=["POST"])
def add_appt(user_type, user_name, d_id, p_id):
    if "loggedin" in session:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        if user_type == "receptionist":
            receptionist_id = session['id']
            if receptionist_id:
                if request.method == "POST":
                    aid = request.form["appointment_id"]
                    date = request.form["date"]
                    start_time = request.form["start_time"]
                    end_time = request.form["end_time"]
                    status = request.form["status"]
                    query1 = "Delete from requested_Appointment WHERE D_ID = %s AND P_ID=%s"
                    cursor.execute(query1, (d_id, p_id))
                    query2 = "INSERT INTO scheduled_appointments (A_ID, P_ID, D_ID, Date, Start_Time, End_Time, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query2, (aid, p_id, d_id, date, start_time, end_time, status))
                    conn.commit()
                    conn.close()
                    return redirect(f"/home/{user_type}/{user_name}")
            else:
                return "Invalid receptionist ID"
        else:
            return "Invalid user type"
    else:
        return redirect(f"/login/{user_type}")
@app.route("/logout/<user_type>")
def logout(user_type):
    if "loggedin" in session:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('type', None)
    return redirect(f'/login/patient')

if __name__ == "__main__":
    app.run( debug=True)
    print("Server up and running at port 5000")
