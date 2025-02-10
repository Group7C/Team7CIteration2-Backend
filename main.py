from flask import Flask, request
import psycopg2


app = Flask(__name__)


# this gets the information so you are able to connect to the database
def get_database_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="team7db",
        user="admin",
        password="1234"
    )

    return conn


# this uses connects to the database with the information provided
def open_database_connection(connection):
    return connection.cursor()


# this closes the currently running database connection
def close_database_connection(current_connection, database):
    # closes the current connection first
    current_connection.close()
    database.close()


# the url in the .route will be used to trigger the function
@app.route("/")
def index():
    return "<h1>working<h1>"

@app.route("/check/user/exists", methods=['GET'])
def checkUserExists():
    # inside the GET request, retrieve the username and email to check
    # if the user exists or not

    name = request.args.get('username')
    email = request.args.get('email')

    print(name, email)

    conn = get_database_connection()
    current = open_database_connection(conn)
    current.execute('SELECT COUNT(username) FROM online_user WHERE username = %s AND email = %s;', (name, email))

    # Since there can only be one user with the same username and email, it will either return 1 or 0
    userExists = current.fetchall()

    # print(userExists)

    # Once the database has been checked, you can close the database connection
    close_database_connection(current, conn)

    if userExists:
        # returns True if the user exists
        return True
    else:
        # returns False is the user does not exist
        return False

@app.route("/create/profile", methods=['GET'])
def createProfile():
    return "<h1>creating user profile...<h1>"

# use .execute() to handle sql query

# THE COMMAND BELOW IS HOW TO RUN THE FILE
# flask --app main run
