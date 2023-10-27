from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random #generate a random room code
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
socketio = SocketIO(app)

rooms = {}

def gen_code(length):
    while True:
        code = ""
        for _ in range (length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

#routes
@app.route("/", methods=["GET", "POST"])
def homePage():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        if join != False and not code:
            return render_template("home.html", error="Room Code field is empty.", code=code, name=name)
        room = code
        if create !=False:
            room = gen_code(5)
            rooms[room] = {"members":0, "messages":[]}
        elif code not in rooms:
            return render_template("home.html", error="Invalid Room Code.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))
    return render_template("home.html")

@app.route("/room")
def room():
    name = session.get('name')
    room = session.get('room')
    messages = rooms[room]['messages']
    return render_template("chat_room.html", room=room, name=name, messages=messages)

if __name__ == "__main__":
    socketio.run(app, debug=True)