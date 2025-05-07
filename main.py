from flask import Flask, request
import psycopg2
from credentials import ext_db_url
from flask_cors import CORS
from test_insert import current
from unpacking import unpacking_list

app = Flask(__name__)

# Enhanced CORS setup to handle preflight requests properly
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}})

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
    # UPDATED TO USE PROJECT_MEMBERS INSTEAD OF USER_PROJECT

    user_id = request.args.get('user_id')
    print(f"Getting projects for user_id: {user_id}")

    conn = get_database_connection()
    current = open_database_connection(conn)

    # Get complete project details
    current.execute('SELECT p.project_uid, p.join_code, p.proj_name, p.deadline, p.notification_preference, '
                    'p.google_drive_link, p.discord_link, p.uuid '
                    'FROM online_user ou '
                    'INNER JOIN project_members pm ON ou.user_id = pm.user_id '
                    'INNER JOIN project p ON pm.project_uid = p.project_uid '
                    'WHERE ou.user_id = %s;', (user_id,))

    # will return the projects associated with the uid
    projects = current.fetchall()
    print(f"Found {len(projects)} projects for user_id {user_id}")

    # Format the projects as a list of dictionaries
    project_list = []
    for p in projects:
        project_dict = {
            'project_uid': p[0],
            'join_code': p[1],
            'proj_name': p[2],
            'deadline': str(p[3]),
            'notification_preference': p[4],
            'google_drive_link': p[5] if p[5] else "",
            'discord_link': p[6] if p[6] else "",
            'uuid': p[7]
        }
        project_list.append(project_dict)

    close_database_connection(current, conn)

    # Convert to JSON string and return
    import json
    return json.dumps(project_list)

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

    # Update to also insert into PROJECT_MEMBERS table
    current.execute('INSERT INTO project_members (project_uid, user_id, is_owner, member_role, join_date) VALUES'
                    '(%s, %s, %s, %s, CURRENT_DATE);', (project_uid, userId, True, 'Editor'))

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
    # UPDATED TO USE PROJECT_MEMBERS INSTEAD OF USER_PROJECT

    userId = request.args.get('user_id')
    projectId = request.args.get('project_id')

    conn = get_database_connection()
    current = open_database_connection(conn)

    # Updated query to use PROJECT_MEMBERS table instead of USER_PROJECT
    current.execute('SELECT COUNT(*) FROM project_members WHERE user_id = %s AND project_uid = %s;', (userId, projectId))

    values = current.fetchall()[0][0]

    close_database_connection(current, conn)

    return str(values)

# additional functionlities

@app.route("/get/project/details", methods=['GET'])
def getProjectDetails():
    # Function will get all details of a project by its ID
    project_id = request.args.get('project_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    # Get basic project details
    current.execute('SELECT project_uid, join_code, proj_name, deadline, notification_preference, google_drive_link, discord_link, uuid '
                   'FROM project WHERE project_uid = %s;', (project_id,))
    
    # Check if the project exists
    project_data = current.fetchall()
    if not project_data:
        close_database_connection(current, conn)
        # Return a JSON error response instead of plain text
        import json
        return json.dumps({"error": "Project not found"})
    
    project = project_data[0]
    
    # Format the project details
    project_details = {
        'project_uid': project[0],
        'join_code': project[1],
        'proj_name': project[2],
        'deadline': str(project[3]),  # Convert date to string
        'notification_preference': project[4],
        'google_drive_link': project[5],
        'discord_link': project[6],
        'uuid': project[7]
    }
    
    # Get project members
    current.execute('SELECT pm.members_id, pm.user_id, pm.is_owner, pm.member_role, pm.join_date, ou.username '
                   'FROM project_members pm '
                   'JOIN online_user ou ON pm.user_id = ou.user_id '
                   'WHERE pm.project_uid = %s;', (project_id,))
    
    members = current.fetchall()
    member_list = []
    
    for member in members:
        member_info = {
            'members_id': member[0],
            'user_id': member[1],
            'is_owner': member[2],
            'member_role': member[3],
            'join_date': str(member[4]),  # Convert date to string
            'username': member[5]
        }
        member_list.append(member_info)
    
    # Add members to project details
    project_details['members'] = member_list
    
    close_database_connection(current, conn)
    
    # Convert to JSON string and return
    import json
    return json.dumps(project_details)

@app.route("/update/project", methods=['GET', 'OPTIONS'])
def updateProject():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function to update project details
    project_id = request.args.get('project_id')
    proj_name = request.args.get('proj_name')
    deadline = request.args.get('deadline')
    notification_preference = request.args.get('notification_preference')
    google_drive_link = request.args.get('google_drive_link')
    discord_link = request.args.get('discord_link')
    join_code = request.args.get('join_code')
    
    # Add CORS headers to the regular response
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            response = app.response_class(
                response=json.dumps({"error": "Project not found"}),
                status=200,
                mimetype='application/json'
            )
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Update query parts - only update fields that were passed
        update_parts = []
        params = []
        
        if proj_name:
            update_parts.append("proj_name = %s")
            params.append(proj_name)
            
        if deadline:
            update_parts.append("deadline = %s")
            params.append(deadline)
            
        if notification_preference:
            update_parts.append("notification_preference = %s::notification_enum")
            params.append(notification_preference)
            
        if google_drive_link is not None:  # Allow empty string
            update_parts.append("google_drive_link = %s")
            params.append(google_drive_link)
            
        if discord_link is not None:  # Allow empty string
            update_parts.append("discord_link = %s")
            params.append(discord_link)
            
        if join_code:
            update_parts.append("join_code = %s")
            params.append(join_code)
        
        # If we have fields to update
        if update_parts:
            query = "UPDATE project SET " + ", ".join(update_parts) + " WHERE project_uid = %s"
            params.append(project_id)
            current.execute(query, params)
            conn.commit()
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/delete/project", methods=['GET', 'OPTIONS'])
def deleteProject():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function to delete a project
    project_id = request.args.get('project_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Project not found"})
        
        # Delete related records first due to foreign key constraints
        
        # 1. Delete task members for all tasks in this project
        current.execute('''
            DELETE FROM task_members
            WHERE task_id IN (
                SELECT task_id FROM task WHERE project_uid = %s
            );
        ''', (project_id,))
        
        # 2. Delete all tasks for this project
        current.execute('DELETE FROM task WHERE project_uid = %s;', (project_id,))
        
        # 3. Delete contribution reports
        current.execute('DELETE FROM contribution_report WHERE project_uid = %s;', (project_id,))
        
        # 4. Delete from members_meeting
        current.execute('''
            DELETE FROM members_meeting
            WHERE meeting_id IN (
                SELECT meeting_id FROM meeting WHERE project_uid = %s
            );
        ''', (project_id,))
        
        # 5. Delete meetings
        current.execute('DELETE FROM meeting WHERE project_uid = %s;', (project_id,))
        
        # 6. Delete project members
        current.execute('DELETE FROM project_members WHERE project_uid = %s;', (project_id,))
        
        # 7. Finally delete the project itself
        current.execute('DELETE FROM project WHERE project_uid = %s;', (project_id,))
        
        conn.commit()
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/get/project/tasks", methods=['GET', 'OPTIONS'])
def getProjectTasks():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will get all tasks for a specific project
    project_id = request.args.get('project_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    # Verify the project exists
    current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
    exists = current.fetchall()[0][0]
    
    if exists == 0:
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": "Project not found"})
    
    # Get all tasks for the project
    current.execute('''
        SELECT t.task_id, t.task_name, t.parent, t.weighting, t.tags, t.priority,
               t.start_date, t.end_date, t.description, t.members, t.notification_frequency, t.status
        FROM task t
        WHERE t.project_uid = %s
        ORDER BY t.priority DESC, t.end_date ASC;
    ''', (project_id,))
    
    tasks = current.fetchall()
    task_list = []
    
    for task in tasks:
        # Get the members assigned to this task from the intersection table
        current.execute('''
            SELECT pm.members_id, pm.user_id, ou.username
            FROM task_members tm
            JOIN project_members pm ON tm.members_id = pm.members_id
            JOIN online_user ou ON pm.user_id = ou.user_id
            WHERE tm.task_id = %s;
        ''', (task[0],))
        
        assigned_members = current.fetchall()
        members_list = []
        
        for member in assigned_members:
            member_info = {
                'members_id': member[0],
                'user_id': member[1],
                'username': member[2]
            }
            members_list.append(member_info)
        
        # Format each task
        task_info = {
            'task_id': task[0],
            'task_name': task[1],
            'parent': task[2],
            'weighting': task[3],
            'tags': task[4],
            'priority': task[5],
            'start_date': str(task[6]),
            'end_date': str(task[7]),
            'description': task[8],
            'members_string': task[9],  # Original members string from the task table
            'notification_frequency': task[10],
            'status': task[11],
            'assigned_members': members_list  # Detailed member info from the intersection table
        }
        task_list.append(task_info)
    
    close_database_connection(current, conn)
    
    # Convert to JSON string and return
    import json
    return json.dumps(task_list)

@app.route("/get/user/tasks", methods=['GET', 'OPTIONS'])
def getUserTasks():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will get all tasks assigned to a specific user
    user_id = request.args.get('user_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    # Verify the user exists
    current.execute('SELECT COUNT(*) FROM online_user WHERE user_id = %s;', (user_id,))
    exists = current.fetchall()[0][0]
    
    if exists == 0:
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": "User not found"})
    
    # Get all tasks assigned to this user
    current.execute('''
        SELECT t.task_id, t.task_name, t.parent, t.weighting, t.tags, t.priority,
               t.start_date, t.end_date, t.description, t.members, t.notification_frequency, t.status,
               t.project_uid, p.proj_name
        FROM task t
        JOIN project p ON t.project_uid = p.project_uid
        JOIN task_members tm ON t.task_id = tm.task_id
        JOIN project_members pm ON tm.members_id = pm.members_id
        WHERE pm.user_id = %s
        ORDER BY t.priority DESC, t.end_date ASC;
    ''', (user_id,))
    
    tasks = current.fetchall()
    task_list = []
    
    for task in tasks:
        # Format each task
        task_info = {
            'task_id': task[0],
            'task_name': task[1],
            'parent': task[2],
            'weighting': task[3],
            'tags': task[4],
            'priority': task[5],
            'start_date': str(task[6]),
            'end_date': str(task[7]),
            'description': task[8],
            'members': task[9],
            'notification_frequency': task[10],
            'status': task[11],
            'project_uid': task[12],
            'project_name': task[13]
        }
        task_list.append(task_info)
    
    close_database_connection(current, conn)
    
    # Convert to JSON string and return
    import json
    return json.dumps(task_list)

@app.route("/create/task", methods=['GET', 'OPTIONS'])
def createTask():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will create a new task for a project
    project_id = request.args.get('project_id')
    task_name = request.args.get('task_name')
    parent = request.args.get('parent')  # Can be null
    weighting = request.args.get('weighting')  # Can be null
    tags = request.args.get('tags')  # Can be null
    priority = request.args.get('priority')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    description = request.args.get('description')  # Can be null
    members = request.args.get('members')  # String representation of members
    notification_frequency = request.args.get('notification_frequency')
    status = request.args.get('status', 'to_do')  # Default to 'to_do' if not provided
    members_ids = request.args.get('members_ids')  # Comma-separated list of member IDs
    user_ids = request.args.get('user_ids')  # NEW: Comma-separated list of user IDs
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Project not found"})
        
        # Insert the task
        current.execute('''
            INSERT INTO task (project_uid, task_name, parent, weighting, tags, priority, 
                            start_date, end_date, description, members, notification_frequency, status)
            VALUES (%s, %s, %s, %s, %s::tags_enum, %s, %s, %s, %s, %s, %s::notification_enum, %s::task_status_enum)
            RETURNING task_id;
        ''', (project_id, task_name, parent, weighting, tags, priority, 
             start_date, end_date, description, members, notification_frequency, status))
        
        conn.commit()
        
        # Get the newly created task ID
        task_id = current.fetchone()[0]
        
        # If user_ids is provided, look up members_ids and assign them to the task
        if user_ids:
            user_id_list = user_ids.split(',')
            for user_id in user_id_list:
                # Look up the members_id for this user in this project
                current.execute('''
                    SELECT members_id FROM project_members 
                    WHERE project_uid = %s AND user_id = %s;
                ''', (project_id, user_id.strip()))
                
                result = current.fetchone()
                if result:
                    members_id = result[0]
                    current.execute('''
                        INSERT INTO task_members (task_id, members_id)
                        VALUES (%s, %s);
                    ''', (task_id, members_id))
            
            conn.commit()
        # If members_ids is provided (and user_ids isn't), assign members to the task
        elif members_ids:
            member_id_list = members_ids.split(',')
            for member_id in member_id_list:
                current.execute('''
                    INSERT INTO task_members (task_id, members_id)
                    VALUES (%s, %s);
                ''', (task_id, member_id.strip()))
            
            conn.commit()
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True, "task_id": task_id})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/update/task", methods=['GET', 'OPTIONS'])
def updateTask():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will update an existing task
    task_id = request.args.get('task_id')
    task_name = request.args.get('task_name')
    parent = request.args.get('parent')
    weighting = request.args.get('weighting')
    tags = request.args.get('tags')
    priority = request.args.get('priority')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    description = request.args.get('description')
    members = request.args.get('members')
    notification_frequency = request.args.get('notification_frequency')
    status = request.args.get('status')
    members_ids = request.args.get('members_ids')  # Comma-separated list of member IDs to add
    remove_members_ids = request.args.get('remove_members_ids')  # Comma-separated list to remove
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the task exists
        current.execute('SELECT COUNT(*) FROM task WHERE task_id = %s;', (task_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Task not found"})
        
        # Update query parts - only update fields that were passed
        update_parts = []
        params = []
        
        if task_name:
            update_parts.append("task_name = %s")
            params.append(task_name)
        
        if parent is not None:  # Allow empty string to clear parent
            update_parts.append("parent = %s")
            params.append(parent if parent else None)
            
        if weighting is not None:
            update_parts.append("weighting = %s")
            params.append(weighting)
            
        if tags:
            update_parts.append("tags = %s::tags_enum")
            params.append(tags)
            
        if priority:
            update_parts.append("priority = %s")
            params.append(priority)
            
        if start_date:
            update_parts.append("start_date = %s")
            params.append(start_date)
            
        if end_date:
            update_parts.append("end_date = %s")
            params.append(end_date)
            
        if description is not None:  # Allow empty string
            update_parts.append("description = %s")
            params.append(description)
            
        if members is not None:  # Allow empty string
            update_parts.append("members = %s")
            params.append(members)
            
        if notification_frequency:
            update_parts.append("notification_frequency = %s::notification_enum")
            params.append(notification_frequency)
            
        if status:
            update_parts.append("status = %s::task_status_enum")
            params.append(status)
        
        # If we have fields to update
        if update_parts:
            query = "UPDATE task SET " + ", ".join(update_parts) + " WHERE task_id = %s"
            params.append(task_id)
            current.execute(query, params)
            conn.commit()
        
        # Handle member assignments
        if members_ids:
            member_id_list = members_ids.split(',')
            for member_id in member_id_list:
                # Check if the assignment already exists to avoid duplicates
                current.execute('''
                    SELECT COUNT(*) FROM task_members 
                    WHERE task_id = %s AND members_id = %s;
                ''', (task_id, member_id.strip()))
                
                exists = current.fetchone()[0]
                if exists == 0:
                    current.execute('''
                        INSERT INTO task_members (task_id, members_id)
                        VALUES (%s, %s);
                    ''', (task_id, member_id.strip()))
            
            conn.commit()
        
        # Handle member removals
        if remove_members_ids:
            remove_id_list = remove_members_ids.split(',')
            for member_id in remove_id_list:
                current.execute('''
                    DELETE FROM task_members 
                    WHERE task_id = %s AND members_id = %s;
                ''', (task_id, member_id.strip()))
            
            conn.commit()
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/update/task/status", methods=['GET', 'OPTIONS'])
def updateTaskStatus():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Specialized function just for updating task status
    task_id = request.args.get('task_id')
    status = request.args.get('status')  # Must be one of: to_do, in_progress, complete
    
    # Validate the status input
    if status not in ['to_do', 'in_progress', 'complete']:
        import json
        return json.dumps({"error": "Invalid status. Must be one of: to_do, in_progress, complete"})
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the task exists
        current.execute('SELECT COUNT(*) FROM task WHERE task_id = %s;', (task_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Task not found"})
        
        # Update just the status
        current.execute('''
            UPDATE task SET status = %s::task_status_enum
            WHERE task_id = %s;
        ''', (status, task_id))
        
        conn.commit()
        
        # Get the updated task details
        current.execute('''
            SELECT task_id, task_name, status
            FROM task
            WHERE task_id = %s;
        ''', (task_id,))
        
        task = current.fetchone()
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps({
            "success": True,
            "task": {
                "task_id": task[0],
                "task_name": task[1],
                "status": task[2]
            }
        })
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/delete/task", methods=['GET', 'OPTIONS'])
def deleteTask():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will delete a task
    task_id = request.args.get('task_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the task exists
        current.execute('SELECT COUNT(*) FROM task WHERE task_id = %s;', (task_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Task not found"})
        
        # First delete from the task_members intersection table
        current.execute('DELETE FROM task_members WHERE task_id = %s;', (task_id,))
        
        # Then delete the task itself
        current.execute('DELETE FROM task WHERE task_id = %s;', (task_id,))
        
        conn.commit()
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/create/meeting", methods=['GET', 'OPTIONS'])
def createMeeting():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
        
    # Function will create a new meeting for a project
    project_id = request.args.get('project_id')
    meeting_type = request.args.get('meeting_type', 'Online')  # Default to Online
    subject = request.args.get('subject')
    start_date = request.args.get('start_date')  # Format: YYYY-MM-DD
    end_date = request.args.get('end_date', start_date)  # Default to same as start_date
    progress = request.args.get('progress', '')  # Can be empty for scheduled meetings
    takeaway = request.args.get('takeaway', '')  # Can be empty for scheduled meetings
    notes = request.args.get('notes', '')  # Optional
    attendees = request.args.get('attendees', '')  # Will be populated later with actual attendees
    
    # Check required fields
    if not subject or not start_date:
        import json
        response = app.response_class(
            response=json.dumps({"error": "Missing required fields"}),
            status=400,
            mimetype='application/json'
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Project not found"})
        
        # Insert the meeting
        current.execute('''
            INSERT INTO meeting (project_uid, meeting_type, start_date, end_date, attendees, subject, progress, takeaway, notes)
            VALUES (%s, %s::meeting_enum, %s, %s, %s, %s, %s, %s, %s)
            RETURNING meeting_id;
        ''', (project_id, meeting_type, start_date, end_date, attendees, subject, progress, takeaway, notes))
        
        conn.commit()
        
        # Get the newly created meeting ID
        meeting_id = current.fetchone()[0]
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True, "meeting_id": meeting_id})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/get/project/meetings", methods=['GET', 'OPTIONS'])
def getProjectMeetings():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
        
    # Function will get all meetings for a specific project
    project_id = request.args.get('project_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT COUNT(*) FROM project WHERE project_uid = %s;', (project_id,))
        exists = current.fetchall()[0][0]
        
        if exists == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Project not found"})
        
        # Get all meetings for the project - updated to match schema
        current.execute('''
            SELECT meeting_id, meeting_type, start_date, end_date, attendees, subject, progress, takeaway, notes
            FROM meeting
            WHERE project_uid = %s
            ORDER BY start_date DESC;
        ''', (project_id,))
        
        meetings = current.fetchall()
        meeting_list = []
        
        for meeting in meetings:
            # Get the attendance records for this meeting
            current.execute('''
                SELECT mm.members_id, pm.user_id, ou.username
                FROM members_meeting mm
                JOIN project_members pm ON mm.members_id = pm.members_id
                JOIN online_user ou ON pm.user_id = ou.user_id
                WHERE mm.meeting_id = %s;
            ''', (meeting[0],))
            
            attendees = current.fetchall()
            attendee_list = []
            
            # Count attended members - all attendees are considered attended for now
            attended_count = len(attendees)
            
            for attendee in attendees:
                attendee_info = {
                    'members_id': attendee[0],
                    'attended': True,  # Default to True since column doesn't exist
                    'user_id': attendee[1],
                    'username': attendee[2]
                }
                attendee_list.append(attendee_info)
            
            # Check if meeting has any attendee records as a way to determine if it's completed
            is_completed = len(attendees) > 0
            
            # Format each meeting to align with schema while providing compatibility with frontend
            meeting_info = {
                'meeting_id': meeting[0],
                'meeting_type': meeting[1],
                'meeting_title': meeting[5],  # Map 'subject' to 'meeting_title' for backwards compatibility
                'subject': meeting[5],  # Also include the actual field name
                'start_date': str(meeting[2]),  # Convert date to string
                'end_date': str(meeting[3]),
                'meeting_date': str(meeting[2]),  # Keep this for backwards compatibility
                'attendees_string': meeting[4],  # Original attendees string from the meeting table
                'progress': meeting[6],
                'takeaway': meeting[7],
                'notes': meeting[8],
                'is_completed': is_completed,  # Derived field based on attendance records
                'attendees': attendee_list,  # Detailed attendee info from the intersection table
                'total_attendees': len(attendee_list),
                'present_attendees': attended_count
            }
            meeting_list.append(meeting_info)
        
        close_database_connection(current, conn)
        
        import json
        return json.dumps(meeting_list)
        
    except Exception as e:
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/update/meeting/attendance", methods=['GET', 'OPTIONS'])
def updateMeetingAttendance():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
        
    # Function will update attendance for a meeting
    meeting_id = request.args.get('meeting_id')
    members_attendance = request.args.get('members_attendance')  # Format: "member_id:true,member_id:false,..."
    
    if not members_attendance:
        import json
        return json.dumps({"error": "No attendance data provided"})
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the meeting exists
        current.execute('SELECT COUNT(*), project_uid FROM meeting WHERE meeting_id = %s GROUP BY project_uid;', (meeting_id,))
        result = current.fetchone()
        
        if not result or result[0] == 0:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Meeting not found"})
        
        project_id = result[1]
        
        # Parse attendance data
        attendance_pairs = members_attendance.split(',')
        success_count = 0
        attendee_usernames = []
        
        for pair in attendance_pairs:
            if ':' not in pair:
                continue
                
            # We'll only process members who are marked as attended (which is all of them sent to this endpoint)
            member_id, attended_str = pair.split(':')
            member_id = member_id.strip()
            attended = attended_str.strip().lower() == 'true'
            
            # Only process if marked as attended
            if not attended:
                print(f"Skipping member {member_id} as they did not attend")
                continue
                
            # Verify this member belongs to the project
            current.execute('''
                SELECT COUNT(*), username FROM project_members pm
                JOIN online_user ou ON pm.user_id = ou.user_id
                WHERE pm.members_id = %s AND pm.project_uid = %s
                GROUP BY username;
            ''', (member_id, project_id))
            
            member_result = current.fetchone()
            if not member_result or member_result[0] == 0:
                print(f"Member {member_id} not found in project {project_id}")
                continue
                
            # Get username for later updating the attendees string
            username = member_result[1]
            attendee_usernames.append(username)
            
            # Check if an attendance record already exists
            current.execute('''
                SELECT COUNT(*) FROM members_meeting 
                WHERE meeting_id = %s AND members_id = %s;
            ''', (meeting_id, member_id))
            
            record_exists = current.fetchone()[0]
            
            if record_exists == 0:
                # Only create records for members who attended
                print(f"Creating attendance record for member {member_id} at meeting {meeting_id}")
                current.execute('''
                    INSERT INTO members_meeting (meeting_id, members_id)
                    VALUES (%s, %s);
                ''', (meeting_id, member_id))
            else:
                print(f"Member {member_id} already recorded as attended for meeting {meeting_id}")
            
            success_count += 1
        
        # Update the attendees field in the meeting table with the list of attendees
        if attendee_usernames:
            attendees_string = ", ".join(attendee_usernames)
            current.execute('''
                UPDATE meeting SET attendees = %s
                WHERE meeting_id = %s;
            ''', (attendees_string, meeting_id))
        
        conn.commit()
        close_database_connection(current, conn)
        
        import json
        return json.dumps({"success": True, "records_updated": success_count})
        
    except Exception as e:
        conn.rollback()
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})

@app.route("/get/group/tasks", methods=['GET', 'OPTIONS'])
def getGroupTasks():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will get all tasks that have multiple members and the user is part of
    user_id = request.args.get('user_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    # Verify the user exists
    current.execute('SELECT COUNT(*) FROM online_user WHERE user_id = %s;', (user_id,))
    exists = current.fetchall()[0][0]
    
    if exists == 0:
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": "User not found"})
    
    # Get all tasks that have multiple members and the user is part of
    current.execute('''
        -- First, get tasks with multiple members where the user is one of those members
        SELECT t.task_id, t.task_name, t.parent, t.weighting, t.tags, t.priority,
               t.start_date, t.end_date, t.description, t.members, t.notification_frequency, t.status,
               t.project_uid, p.proj_name
        FROM task t
        JOIN project p ON t.project_uid = p.project_uid
        -- Join with a subquery that counts members per task
        JOIN (
            SELECT task_id, COUNT(*) as member_count
            FROM task_members
            GROUP BY task_id
            HAVING COUNT(*) > 1
        ) tm ON t.task_id = tm.task_id
        -- Join with task_members to filter for the user's tasks
        JOIN task_members tmm ON t.task_id = tmm.task_id
        JOIN project_members pm ON tmm.members_id = pm.members_id
        WHERE pm.user_id = %s
        ORDER BY t.priority DESC, t.end_date ASC;
    ''', (user_id,))
    
    tasks = current.fetchall()
    task_list = []
    
    for task in tasks:
        # Get all members assigned to this task for detailed info
        current.execute('''
            SELECT pm.members_id, pm.user_id, ou.username
            FROM task_members tm
            JOIN project_members pm ON tm.members_id = pm.members_id
            JOIN online_user ou ON pm.user_id = ou.user_id
            WHERE tm.task_id = %s;
        ''', (task[0],))
        
        assigned_members = current.fetchall()
        members_list = []
        
        for member in assigned_members:
            member_info = {
                'members_id': member[0],
                'user_id': member[1],
                'username': member[2]
            }
            members_list.append(member_info)
        
        # Format each task
        task_info = {
            'task_id': task[0],
            'task_name': task[1],
            'parent': task[2],
            'weighting': task[3],
            'tags': task[4],
            'priority': task[5],
            'start_date': str(task[6]),
            'end_date': str(task[7]),
            'description': task[8],
            'members': task[9],
            'notification_frequency': task[10],
            'status': task[11],
            'project_uid': task[12],
            'project_name': task[13],
            'assigned_members': members_list
        }
        task_list.append(task_info)
    
    close_database_connection(current, conn)
    
    # Convert to JSON string and return
    import json
    return json.dumps(task_list)

@app.route("/get/contribution/report", methods=['GET', 'OPTIONS'])
def getContributionReport():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
        
    # Function will generate a contribution report for a project
    project_id = request.args.get('project_id')
    
    conn = get_database_connection()
    current = open_database_connection(conn)
    
    try:
        # Verify the project exists
        current.execute('SELECT proj_name FROM project WHERE project_uid = %s;', (project_id,))
        project_data = current.fetchall()
        
        if not project_data:
            close_database_connection(current, conn)
            import json
            return json.dumps({"error": "Project not found"})
            
        project_name = project_data[0][0]
        
        # Get all project members
        current.execute('''
            SELECT pm.members_id, pm.user_id, ou.username
            FROM project_members pm
            JOIN online_user ou ON pm.user_id = ou.user_id
            WHERE pm.project_uid = %s;
        ''', (project_id,))
        
        members = current.fetchall()
        contribution_report = []
        
        # Calculate contribution for each member
        for member in members:
            member_id = member[0]
            user_id = member[1]
            username = member[2]
            
            # 1. Calculate meeting contribution (10% weight)
            # Get total meetings for the project
            current.execute('''
                SELECT COUNT(*) FROM meeting
                WHERE project_uid = %s;
            ''', (project_id,))
            
            total_meetings = current.fetchall()[0][0]
            meeting_contribution = 0
            attended_meetings = 0
            
            if total_meetings > 0:
                # Get meetings attended by this member
                current.execute('''
                    SELECT COUNT(*) FROM members_meeting mm
                    JOIN meeting m ON mm.meeting_id = m.meeting_id
                    WHERE mm.members_id = %s AND m.project_uid = %s;
                ''', (member_id, project_id))
                
                attended_meetings = current.fetchall()[0][0]
                
                # Calculate meeting contribution (10% weight)
                meeting_contribution = (attended_meetings / total_meetings) * 10
            
            # 2. Calculate task contribution (90% weight)
            # Get completed tasks where this member is assigned
            current.execute('''
                SELECT t.task_id, t.task_name, t.weighting, 
                       (SELECT COUNT(*) FROM task_members WHERE task_id = t.task_id) as member_count
                FROM task t
                JOIN task_members tm ON t.task_id = tm.task_id
                WHERE tm.members_id = %s AND t.project_uid = %s AND t.status = 'complete';
            ''', (member_id, project_id))
            
            completed_tasks = current.fetchall()
            task_contribution = 0
            task_details = []
            
            for task in completed_tasks:
                task_id = task[0]
                task_name = task[1]
                task_weight = task[2] if task[2] is not None else 0  # Default to 0 if NULL
                member_count = task[3]
                
                # Calculate individual contribution for this task
                individual_contribution = 0
                if member_count > 0:
                    individual_contribution = (task_weight / member_count) * 0.9
                
                task_contribution += individual_contribution
                
                # Add task detail to the report
                task_details.append({
                    'task_id': task_id,
                    'task_name': task_name,
                    'task_weight': task_weight,
                    'member_count': member_count,
                    'individual_contribution': individual_contribution
                })
            
            # 3. Calculate total contribution
            total_contribution = meeting_contribution + task_contribution
            
            # 4. Add to report
            member_report = {
                'members_id': member_id,
                'user_id': user_id,
                'username': username,
                'meeting_contribution': meeting_contribution,
                'task_contribution': task_contribution,
                'total_contribution': total_contribution,
                # Additional details for meetings
                'total_meetings': total_meetings,
                'attended_meetings': attended_meetings,
                # Add details about completed tasks
                'completed_tasks': task_details
            }
            
            contribution_report.append(member_report)
        
        close_database_connection(current, conn)
        
        # Sort by total contribution (descending)
        contribution_report.sort(key=lambda x: x['total_contribution'], reverse=True)
        
        # Normalize contributions to ensure all members sum to 100%
        total_contribution_sum = sum(member['total_contribution'] for member in contribution_report)
        
        if total_contribution_sum > 0:
            for member in contribution_report:
                # Save the raw contribution for reference
                member['raw_contribution'] = member['total_contribution']
                # Normalize the contribution
                member['total_contribution'] = (member['total_contribution'] / total_contribution_sum) * 100
        
        # Get project progress
        completed_tasks_percentage = 0
        try:
            # Re-establish connection for project progress calculation
            conn = get_database_connection()
            current = open_database_connection(conn)
            
            # Count total tasks and completed tasks
            current.execute('''
                SELECT 
                    COUNT(*) AS total_tasks,
                    SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS completed_tasks
                FROM task
                WHERE project_uid = %s;
            ''', (project_id,))
            
            task_stats = current.fetchall()[0]
            total_tasks = task_stats[0] or 0
            completed_tasks = task_stats[1] or 0
            
            if total_tasks > 0:
                completed_tasks_percentage = (completed_tasks / total_tasks) * 100
                
            close_database_connection(current, conn)
        except Exception as e:
            print(f"Error calculating project progress: {e}")
            # If there's an error, just continue with default value
            pass
        
        import json
        return json.dumps({
            "success": True,
            "project_id": project_id,
            "project_name": project_name,
            "project_progress": completed_tasks_percentage,
            "report": contribution_report
        })
        
    except Exception as e:
        conn.rollback()  # Rollback any pending transaction
        close_database_connection(current, conn)
        import json
        return json.dumps({"error": str(e)})
