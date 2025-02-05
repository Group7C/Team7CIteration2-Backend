from flask import Flask

app = Flask(__name__)


# the url in the .route will be used to trigger the function
@app.route("/")
def hello_world():
    return "<h1>working<h1>"



# THE COMMAND BELOW IS HOW TO RUN THE FILE
# flask --app main run
