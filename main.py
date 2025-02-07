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
    connection.cursor()


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

    # testing to see if it works
    return f"hi {name} with the email address {email}"

@app.route("/create/profile", methods=['GET'])
def createProfile():
    return "<h1>creating user profile...<h1>"

# use .execute() to handle sql query

# THE COMMAND BELOW IS HOW TO RUN THE FILE
# flask --app main run
