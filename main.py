from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random #generate a random room code
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
socketio = SocketIO(app)

#quando o server é reiniciado as mensagens são perdidas, pois estão armazenadas na RAM
chats = {} #Dicionário com todas as salas existentes.

def gen_code(length):
    while True:
        code = ""
        for _ in range (length):
            code += random.choice(ascii_uppercase)
        if code not in chats: break
    return code

#Página do formulário de login
@app.route("/", methods=["GET", "POST"])
def homePage():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        #Retorna erro se tentar entrar em uma sala sem colocar o código dela.
        if join != False and not code:
            return render_template("home.html", error="O campo de código está vazio.", code=code, name=name)
        room = code

        #Gera um código de 5 letras ao criar uma sala
        if create !=False:
            room = gen_code(5)
            chats[room] = {"members":0, "messages":[]}

        #Retorna um erro ao tentar usar um código que não existe.
        elif code not in chats:
            return render_template("home.html", error="Código da sala inválido.", code=code, name=name)
        
        #Define a sala e o nome do usuário, e redireciona para a página HTML do chat criado.
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))
    return render_template("home.html")

#Página do chat
@app.route("/room")
def room():
    #Vai pegar o código da sala e o nome do usuário para utilizar na página do chat.
    name = session.get('name')
    room = session.get('room')

    messages = chats[room]['messages']
    return render_template("chat_room.html", room=room, name=name, messages=messages)


#Inicializa o socket de fato.
@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in chats: return
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    #envia a mensgaem para todas as pessoas da sala
    send(content, to=room)
    chats[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    join_room(room)
    send({"name": name, "message": "entrou no chat."}, to=room)
    chats[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    if room in chats:
        chats[room]["members"] -= 1
        if chats[room]["members"] <= 0:
            del chats[room]

    send({"name": name, "message": "saiu do chat."}, to=room)
    print(f"{name} has left room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)