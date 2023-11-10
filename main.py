from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
socketio = SocketIO(app)

chats = {} 
#Página do formulário de login
@app.route("/", methods=["GET", "POST"])
def homePage():
    session.clear()
    if request.method == "POST":
        usuario = request.form.get("name")
        codigo_sala = request.form.get("code")
        criar_sala = request.form.get("create", False)
        room = codigo_sala
        if criar_sala != False:
            room = codigo_sala
            chats[room] = {"members":0, "messages":[]}
        elif codigo_sala not in chats:
            return render_template("home.html", aviso="Código da sala inválido.", code=codigo_sala, name=usuario)
        session["room"] = room
        session["name"] = usuario
        return redirect(url_for("room"))
    return render_template("home.html")
#Página do Chat
@app.route("/chat")
def room():
    name = session.get('name')
    room = session.get('room')
    messages = chats[room]['messages']
    return render_template("chat_room.html", room=room, name=name, messages=messages)

#Eventos socket
@socketio.on("connect")
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    join_room(room)
    send({"name": name, "message": "entrou no chat."}, to=room)
    chats[room]["members"] += 1
@socketio.on("message")
def message(infos):
    room = session.get("room")
    if room not in chats: return
    msg_na_tela = {
        "name": session.get("name"),
        "message": infos["infos"]
    }
    send(msg_na_tela, to=room)
    chats[room]["messages"].append(msg_na_tela)
@socketio.on("disconnect")
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)
    send({"name": name, "message": "saiu do chat."}, to=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)