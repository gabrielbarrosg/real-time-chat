from flask import Flask, render_template, request, session, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random #generate a random room code
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "311216"
socketio = SocketIO(app)

#routes
@app.route("/", methods=["GET", "POST"])
def homePage():
    return render_template("home.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)