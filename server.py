from apps import create_app, init_socketio

app = create_app()
socketio = init_socketio(app)

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False, host="0.0.0.0", port=5000)
