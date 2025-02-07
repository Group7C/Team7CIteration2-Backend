import psycopg2


# connecting to the database, make sure you are connecting to the right database and user otherwise this will not work
connection = psycopg2.connect(
        host="localhost",
        database="team7db",
        user="admin",
        password="1234")

# Creating a session with the connection
current = connection.cursor()


# the %s will handle the parameter values and will ensure that there are no sql injection attacks
current.execute('INSERT INTO ONLINE_USER (username, email, user_password, theme, profile_picture, currency_total, customize_settings)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('test_user2',
             'test2@gmail.com',
             'strong_password',
             'Light',
             None,
             0,
             ''
             )
            )

# pushing the changes to the database
connection.commit()

# closing the current session and the connection
current.close()
connection.close()