import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def hello():
        execute_query("DROP TABLE IF EXISTS users")
        execute_query("CREATE TABLE users (Username text,Password text,firstname text, lastname text, email text, count integer)")
        return render_template('login.html')

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    msg = ''
    if request.method == 'POST' and str(request.form['usn']) !="" and str(request.form['pwd']) !="" and str(request.form['fn']) !="" and str(request.form['ln']) !="" and str(request.form['em']) !="":
        username = str(request.form['usn'])
        password = str(request.form['pwd'])
        firstname = str(request.form['fn'])
        lastname = str(request.form['ln'])
        email = str(request.form['em'])
        ufile = request.files['textfile']
        if not ufile:
            fname = null
            count = null
        else :
            fname = ufile.filename
            count = getNumberOfWords(ufile)
        res = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if res:
            msg = 'User has already registered!'
        else:
            sq1 = execute_query("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, count ))
            commit()
            sq2 = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            if sq2:
                for row in sq2:
                    return responsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        msg = 'Some of the fields are missing!'
    return render_template('registration.html', message = msg)

@app.route('/login', methods =['POST', 'GET'])
def login():
    msg = ''
    if request.method == 'POST' and str(request.form['usn']) !="" and str(request.form['pwd']) != "":
        username = str(request.form['usn'])
        password = str(request.form['pwd'])
        sq = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        if sq:
            for row in sq:
                return responsePage(row[0], row[1], row[2], row[3])
        else:
            msg = 'Invalid Credentials !'
    elif request.method == 'POST':
        msg = 'Please enter Credentials'
    return render_template('login.html', message = msg)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

def responsePage(firstname, lastname, email, count):
    return """User details <br><br> Name :  """ + str(firstname) + """ <br> Surname : """ + str(lastname) + """ <br> Email : """ + str(email) + """ <br><br> No of Words: """ + str(count) + """ <br><br> <a href="/download" >Download</a> """

if __name__ == '__main__':
  app.run()