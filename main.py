from flask import Flask, request
import psycopg2

from test_insert import current

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

    conn = get_database_connection()
    current = open_database_connection(conn)
    current.execute('SELECT COUNT(username) FROM online_user WHERE username = %s AND email = %s;', (name, email))

    # Since there can only be one user with the same username and email, it will either return 1 or 0
    userExists = current.fetchall()[0][0]

    # Once the database has been checked, you can close the database connection
    close_database_connection(current, conn)

    print(userExists, type(userExists))

    # the return type cannot be a bool, hence why it is converted to a String!
    if userExists == 1:
        # returns True if the user exists
        return str(True)
    else:
        # returns False is the user does not exist
        return str(False)

@app.route("/create/profile", methods=['GET'])
def createProfile():
    # need to get the user information to create an insert in the database, specifically the ONLINE_USER table
    username = request.args.get('username')
    email = request.args.get('email')

    # https is secure so the password should be fine to send over https as plaintext
    # may have to consider salting and hashing the password before it is inserted into the
    # database
    password = request.args.get('password')

    conn = get_database_connection()
    current = open_database_connection(conn)

    # need to test insert query to ensure it works.
    current.execute('INSERT INTO ONLINE_USER (username, email, user_password, theme, profile_picture, currency_total, customize_settings) '
                    'VALUES'
                    ' (%s, %s, %s, Light, NULL, 0, '');', (username, email, password))

    # need to commit the changes to the database
    # consider adding exceptions in case there are any errors
    conn.commit()

    # once the changes to the database have been made, you can close the database connection
    close_database_connection(current, conn)

    # the user does not need to retrieve anything from the db so the function does not need to return anything

@app.route("/check/project/exists", methods=['GET'])
def checkProjectExists():

    # Since all projects have a unique uid, you can do a query to see if a project matches with the corresponding uid
    # There will only be 1 or 0 projects with that uid
    uid = request.args.get('uid')

    conn = get_database_connection()
    current = open_database_connection(conn)

    # need to test to see if this query works
    current.execute('SELECT COUNT(project_uid) FROM PROJECT WHERE project_uid = %s', (uid))

    # will be an int with a value of 1 or 0
    projectExists = current.fetchall()[0][0]

    close_database_connection(current, conn)

    if projectExists == 1:
        # project exists
        return str(True)
    else:
        # project does not exist
        return str(False)

# THE COMMAND BELOW IS HOW TO RUN THE FILE
# flask --app main run
