from flask import *
#from flaskext.mysql import MySQL
import re
app = Flask(__name__)
app.secret_key = 'sjhuefbyuUGgyt3874'
import mysql.connector

mysql_config = {
   'host': 'localhost',
   'user': 'root',
   'password': 'maitreyi@1304',
   'database': 'dbmsproject' 
}

@app.route("/")
def first():
    return redirect("/login/patient")

@app.route('/login/<user_type>')
def login(user_type):
    msg = ""
    # print(request.args.get("username"),request.args.get("password"))
    print(user_type)

    if (request.args.get("username")):
        username = request.args.get("username")
        password = request.args.get("password")

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select * from {user_type} where {user_type[0]}_id = "{username}" and password = "{password}";')
        account = cursor.fetchone()
        cursor.close()
        connection.close()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['type'] = user_type
            return redirect(f'/home/{user_type}/{account[1]}/valid')
        else:
            msg = 'Incorrect username or password.'

    return render_template(f"log_{user_type[:3]}.html", msg = msg)


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
        cursor.execute(f'select * from Requested_Appointment where P_ID = "{session["id"]}" and D_ID = "{doc_id}";')
        exists = cursor.fetchall()
        if len(exists) > 0:
            return redirect(f"/home/{user_type}/{user_name}/requestAppointment/status/invalid")
        
        cursor.execute(f'insert into Requested_Appointment value("{session["id"]}", "{doc_id}");')
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
    app.run(host="localhost", port=int("5000"), debug = True)
    print("Server up and running at port 5000")



#fix alignment of error message in home_doc
#add buttons to go to other login portals.
#back button