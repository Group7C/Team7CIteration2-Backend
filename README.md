# Installation (Run the following command)

pip install Flask

pip install -r requirements.txt


# Running the psql server locally (Windows Version)

net start postgresql-x64-17

this will start the psql service (run powershell in admin mode)

net stop postgresql-x64-17

this will stop the psql service (run powershell in admin mode)

sc query state= all | findstr "postgres"

use the command above in case this is not the same psql service name for you (name may be different on your machine)

before you can connect the PgAdmin to the database, have to ensure that the psql service is **running**

# Setup a admin user

Look into the main.py to see the user and password you need to use. This user needs to be created. Use the application
pgAdmin to create a server which you can use the admin user to connect it to. This means that when the table needs to be
read from or inserted to you can do so by connecting to the admin user. 

# After creating server 

Once you have created the server, make sure to create a database called team7db and look inside the database folder to 
find the **schema.sql** file which will be required to create the schema of the database. Ensure that psql server is 
running locally before you try creating the schema. You can use the query tool to upload the file then you can press F5 
to execute the query.

# After creating the schema (Inserts)

now that the server is created, you can create inserts for the ONLINE_USER table. Just to test i would go to the database 
folder inside the flutter project and there will be a file called 'insert_test.sql' execute that code inside the query 
tool and then make another query just to see if the table has been updated or not.