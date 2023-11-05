from flask import *
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'sjhuefbyuUGgyt3874'
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    #'password': 'MacbookAirm1',
    'password': 'maitreyi@1304',
    'database': 'dbmsproject'
}

@app.route("/")
@app.route("/login")
def first():
    return redirect("/login/patient")

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
            return redirect(f'/home/{user_type}/{account[1]}/valid')
        else:
            msg = 'Incorrect username or password.'

    return render_template(f"log_{user_type[:3]}.html", msg=msg)


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
                    return redirect(f"/home/{user_type}/{user_name}/valid")
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
                    query = "SELECT P_ID,date,start_time,end_time,status FROM scheduled_appointments WHERE D_ID=%s"
                    cursor.execute(query,(d_id,))
                    doc_schedule = cursor.fetchall()
                    date = request.form["date"]
                    start_time = request.form["start_time"]
                    end_time = request.form["end_time"]
                    zero = 0
                    exit_status = cursor.callproc('schedule_appointment', args = (p_id, d_id, date, start_time, end_time,zero))
                    if exit_status[5] == None:
                        conn.commit()
                        conn.close()
                        return redirect(f"/home/{user_type}/{user_name}/valid")
                    elif exit_status[5] == -1:
                        return render_template("fixappt.html", doc_schedule=doc_schedule, user_type=user_type, user_name=user_name, d_id=d_id, p_id=p_id, error="error")
            else:
                return "Invalid receptionist ID"
        else:
            return "Invalid user type"
    else:
        return redirect(f"/login/{user_type}")



@app.route("/home/<user_type>/<user_name>/<status>")
def home_pat(user_type, user_name, status):
    if "loggedin" in session:
        return render_template(f"home_{user_type[:3]}.html", type = user_type, name = user_name, status = status)
    else:
        return redirect(f"/login/{user_type}")
    
@app.route("/home/<user_type>/<user_name>/requestAppointment/status/<status>")
def requestAppointment(user_type, user_name, status):
    if "loggedin" in session and session['type'] == 'patient':

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select distinct Department from Doctor;')
        departments = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(f"request_appt.html", user_type = user_type, user_name = user_name, departments = departments, status = status)
    else:
        return redirect(f"/login/patient")
    
@app.route("/home/<user_type>/<user_name>/requestAppointment/<dept>")
def reqAppointmentDept(user_type, user_name, dept):
    if "loggedin" in session and session['type'] == 'patient':

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select D_ID, Name from Doctor where Department = "{dept}";')
        doctors = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(f"request_appt_dept.html", user_type = user_type, user_name = user_name, dept = dept, doctors = doctors)
    else:
        return redirect(f"/login/patient")
    

@app.route("/home/<user_type>/<user_name>/requestAppointment/<dept>/<doc_id>")
def reqAppointmentDoc(user_type, user_name, dept, doc_id):
    if "loggedin" in session and session['type'] == 'patient':

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        exit_status = cursor.callproc("request_appointment", args = (session['id'], doc_id, 0))
        print(exit_status)
        if exit_status[2] == -1:
            return redirect(f"/home/{user_type}/{user_name}/requestAppointment/status/appointmentexists")
        elif exit_status[2] == -2:
            return redirect(f"/home/{user_type}/{user_name}/requestAppointment/status/requestexists")
        
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(f"/home/patient/{user_name}/successful")
    else:
        return redirect(f"/login/patient")
    
@app.route("/home/<user_type>/<user_name>/appointmentHistory")
def apptHistory(user_type, user_name):
    if "loggedin" in session and session['type'] == 'patient':

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select d.Name, s.Date, s.Start_time, s.End_time from Doctor d natural join Scheduled_Appointments s where s.P_ID = "{session["id"]}" and s.Status = "Scheduled";')
        upcoming = cursor.fetchall()
        cursor.execute(f'select s.A_ID, d.Name, s.Date from Doctor d natural join Scheduled_Appointments s where s.P_ID = "{session["id"]}" and s.Status = "Completed";')
        past = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(f"appt_History.html", type = user_type, name = user_name, upcoming = upcoming, past = past)
    else:
        return redirect(f"/login/patient")
    
@app.route("/home/<user_type>/<user_name>/appointmentHistory/<a_id>")
def apptSummary(user_type, user_name, a_id):
    if "loggedin" in session and session['type'] == 'patient':

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select * from Appointment_Summary where A_ID = "{a_id}";')
        summary = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template(f"appt_Summary.html", user_type = user_type, user_name = user_name, summary = summary)
    else:
        return redirect(f"/login/patient")
    
@app.route("/home/<user_type>/<user_name>/scheduledAppointments")
def scheduled_appt(user_type, user_name):
    if "loggedin" in session and session['type'] == 'receptionist':
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select s.A_ID, p.Name, p.Phone, d.Name, s.Date, s.Start_Time, s.End_Time from patient p join scheduled_appointments s on p.P_ID = s.P_ID join doctor d on d.D_ID = s.D_ID where s.status = "scheduled" and s.date <  CAST(CURRENT_TIMESTAMP AS DATE) or (s.date =  CAST(CURRENT_TIMESTAMP AS DATE) and s.End_Time < CAST(CURRENT_TIMESTAMP AS TIME));')
        overdue = cursor.fetchall()
        cursor.execute(f'select s.A_ID, p.Name, p.Phone,  d.Name, s.Date, s.Start_Time, s.End_Time from patient p join scheduled_appointments s on p.P_ID = s.P_ID join doctor d on d.D_ID = s.D_ID where s.status = "scheduled" and s.date >  CAST(CURRENT_TIMESTAMP AS DATE) or (s.date =  CAST(CURRENT_TIMESTAMP AS DATE) and s.Start_Time >= CAST(CURRENT_TIMESTAMP AS TIME));')
        due = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(f"scheduled_appt.html", user_type = user_type, user_name = user_name, overdue = overdue, due = due)
    else:
        return redirect(f"/login/receptionist")

@app.route("/home/<user_type>/<user_name>/removeoverdue")
def remove_overdue(user_type, user_name):
    if "loggedin" in session and session['type'] == 'receptionist':
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute("update Scheduled_Appointments set Status = 'Overdue' where Status = 'Scheduled' and Date <  CAST(CURRENT_TIMESTAMP AS DATE) or (Date =  CAST(CURRENT_TIMESTAMP AS DATE) and End_Time < CAST(CURRENT_TIMESTAMP AS TIME));")
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(f"/home/{user_type}/{user_name}/valid")
    
    else:
        return redirect(f"/login/receptionist")
    
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




## URGENT: requested appointment should not have a corresponding value in scheduled_appointments with status scheduled.
# maybe use a trigger and a procedure, like with scheduling appt.

#fix alignment of error message in home_doc
#add buttons to go to other login portals.
#back button