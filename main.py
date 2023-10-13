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

# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'maitreyi@1304'
# app.config['MYSQL_DATABASE_DB'] = 'dbmsproject'

# mysql = MySQL()
# mysql.init_app(app)

@app.route('/login/<user_type>')
def login(user_type):
    msg = ""
    # print(request.args.get("username"),request.args.get("password"))
    print(user_type)

    if (request.args.get("username")):
        username = request.args.get("username")
        password = request.args.get("password")

        # cursor = mysql.get_db().cursor()
        # cursor.execute(f'select * from {user_type} where {user_type[0]}_id = "{username}" and password = "{password}";')
        # account = cursor.fetchone()
        # cursor.close()

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
            return redirect(f'/home/{user_type}/{account[1]}')
        else:
            msg = 'Incorrect username or password.'

    return render_template(f"log_{user_type[:3]}.html", msg = msg)


@app.route("/home/<user_type>/<user_name>")
def home_pat(user_type, user_name):
    if "loggedin" in session:
        return render_template(f"home_{user_type[:3]}.html", type = user_type, name = user_name)
    else:
        return redirect(f"/login/{user_type}")
    
@app.route("/home/<user_type>/<user_name>/requestAppointment")
def requestAppointment(user_type, user_name):
    if "loggedin" in session:

        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        cursor.execute(f'select distinct Department from Doctor;')
        departments = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template(f"request_appt.html", type = user_type, name = user_name, departments = departments)
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
    app.run(host="localhost", port=int("5000"), debug = True)
    print("Server up and running at port 5000")



#fix alignment of error message in home_doc
#add buttons to go to other login portals.