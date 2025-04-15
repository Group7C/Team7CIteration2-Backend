from flask import Flask, request
import psycopg2
from credentials import ext_db_url
from flask_cors import CORS
from test_insert import current
from unpacking import unpacking_list

app = Flask(__name__)

# required to respond with CORS headers otherwise you will get 'failed to fetch' errors
# when making a request
CORS(app)

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

    email = request.args.get('email')

    print(email)

    conn = get_database_connection()
    current = open_database_connection(conn)
    current.execute('SELECT COUNT(username) FROM online_user WHERE email = %s;', (email,))

    # Since there can only be one user with the same username and email, it will either return 1 or 0
    userExists = current.fetchall()[0][0]

    # Once the database has been checked, you can close the database connection
    close_database_connection(current, conn)

    print(userExists, type(userExists))

    # the return type cannot be a bool, hence why it is converted to a String!
    if userExists >= 1:
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
                    '(%s, %s, %s, %s, %s, %s, %s);', (username, email, password, 'Light', None, 0, ''))

    # need to commit the changes to the database
    # consider adding exceptions in case there are any errors
    conn.commit()

    # once the changes to the database have been made, you can close the database connection
    close_database_connection(current, conn)

    return "executed"

    # the user does not need to retrieve anything from the db so the function does not need to return anything

@app.route("/check/project/exists", methods=['GET'])
def checkProjectExists():
    # THIS FUNCTION HAS NOT BEEN TESTED SO EXPECT SOME BUGS

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

@app.route("/get/user/id", methods=['GET'])
def getUserId():
    # function will return the userid given a username and an email
    # THIS FUNCTION HAS NOT BEEN TESTED SO EXPECT SOME BUGS

    email = request.args.get('email')
    #email = f"'{email}'"
    print(email)

    conn = get_database_connection()
    current = open_database_connection(conn)

    # need to test to see if this query works
    current.execute('SELECT user_id FROM online_user WHERE email = %s;', (email,))
    #current.execute('SELECT * FROM online_user;')

    # will return user id given a username
    user_id = current.fetchall()[0][0]
    print(user_id)

    close_database_connection(current, conn)

    return str(user_id)

@app.route("/get/user/projects", methods=['GET'])
def getUserProjects():
    # this function will get the projects that a user is a part of using their uid
    # THIS FUNCTION HAS NOT BEEN TESTED SO EXPECT SOME BUGS

    user_id = request.args.get('user_id')

    conn = get_database_connection()
    current = open_database_connection(conn)

    # need to test to see if this query works
    current.execute('SELECT p.proj_name '
                    'FROM online_user ou '
                    'INNER JOIN user_project up ON ou.user_id = up.user_id '
                    'INNER JOIN project p ON up.project_uid = p.project_uid '
                    'WHERE ou.user_id = %s;', (user_id,))

    # will return the projects associated with the uid
    user_id = current.fetchall()

    close_database_connection(current, conn)

    # need to unpack the list
    return unpacking_list(user_id)

@app.route("/get/user/theme", methods=['GET'])
def getUserTheme():
    # function will return the user theme
    # FUNCTION NEEDS TO BE TESTED

    user_id = request.args.get('user_id')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT theme FROM online_user WHERE user_id = %s;', user_id)

    # this will be the user's theme if they exist in the database
    theme = current.fetchall()[0][0]

    close_database_connection(current, conn)

    return theme

@app.route("/get/user/password", methods=['GET'])
def getUserPassword():
    # have to check to make sure the function works!
    user_id = request.args.get('user_id')

    print(user_id)

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT user_password FROM online_user WHERE user_id = %s;', (user_id,))

    password = current.fetchall()[0][0]

    close_database_connection(current, conn)

    return password

@app.route("/get/username", methods=['GET'])
def getUsername():
    # have to check to ensure function works!

    email = request.args.get('email')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT username FROM online_user WHERE email = %s;', (email,))

    username = current.fetchall()[0][0]

    close_database_connection(current, conn)

    return username

@app.route("/check/project/uuid/exists", methods=['GET'])
def checkProjectUuidExists():
    uuid = request.args.get('uuid')

    print(uuid, "is the uuid in here")

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT COUNT(uuid) FROM project WHERE uuid = %s;', (uuid,))

    # if the is 1 or more projects with the following uuid, then the uuid is already in use
    numUuid = current.fetchall()[0][0]

    close_database_connection(current, conn)

    # if value greater than 0, then it exists
    return str(numUuid)


@app.route("/upload/project", methods=['GET'])
def uploadProject():

    projectName = request.args.get('name')
    joinCode = request.args.get('join')
    dueDate = request.args.get('due')
    uuid = request.args.get('uuid')
    userId = request.args.get('user_id')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('INSERT INTO PROJECT (join_code, proj_name, deadline, notification_preference, google_drive_link, discord_link, uuid)'
                    'VALUES'
                    '(%s, %s, %s, %s, %s, %s, %s);', (joinCode, projectName, dueDate, 'Weekly', None, None, uuid))

    conn.commit()

    # now need to get project pk so can create insert into the intersection table

    current.execute('SELECT project_uid FROM project WHERE uuid = %s;', (uuid,))

    project_uid = current.fetchall()[0][0]

    print("this is the project uid: ", project_uid)

    current.execute('INSERT INTO user_project (user_id, project_uid) VALUES'
                    '(%s, %s);', (userId, project_uid))

    conn.commit()

    close_database_connection(current, conn)

    return "executed"


@app.route("/project/password/validation", methods=['GET'])
def projectPasswordValid():

    inputPassword = request.args.get('password')
    uuid = request.args.get('uuid')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT COUNT(proj_name) FROM project WHERE uuid = %s AND join_code = %s;', (uuid, inputPassword))

    # will have a value of 1 if there is a match
    correct = current.fetchall()[0][0]

    close_database_connection(current, conn)

    return str(correct)


@app.route("/get/project/attributes", methods=['GET'])
def getProjectAttributes():

    projectUuid = request.args.get('uuid')
    joinCode = request.args.get('password')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT (project_uid, notification_preference, proj_name, deadline, google_drive_link, discord_link)'
                    'FROM project WHERE uuid = %s AND join_code = %s;', (projectUuid, joinCode))

    # below converts the value to a list which can be returned
    values = current.fetchall()[0][0].strip("()").split(",")

    listValues = []

    for value in values:
        hasValue = value.strip()
        if hasValue:
            listValues.append(hasValue)
        else:
            listValues.append("Null")

    return listValues

@app.route("/get/project/id", methods=['GET'])
def getProjectId():
    # function will get the project id from the project's uuid

    uuid = request.args.get('uuid')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT project_uid FROM project WHERE uuid = %s;', (uuid,))

    values = current.fetchall()[0][0]

    return str(values)

@app.route("/user/in/project", methods=['GET'])
def userInProject():
    # function will check the intersection table to see if a user is in a project

    userId = request.args.get('user_id')
    projectId = request.args.get('project_id')

    conn = get_database_connection()
    current = open_database_connection(conn)

    current.execute('SELECT COUNT(*) FROM user_project WHERE user_id = %s AND project_uid = %s;', (userId, projectId))

    values = current.fetchall()[0][0]

    return str(values)


# THE COMMAND BELOW IS HOW TO RUN THE FILE
# flask --app main run
