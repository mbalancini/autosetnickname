from flask import Flask
from threading import Thread
import logging

app = Flask('')


@app.route('/')
def home():
    return "✅ El bot está vivo."


def run():
    # Oculta advertencias del servidor de desarrollo
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Inicia el servidor Flask
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
