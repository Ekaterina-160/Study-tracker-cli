import os
from flask import Flask
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

app = Flask(__name__)
# Секретный ключ нужен для шифрования сессий и защиты форм (понадобится в Часе 3 и 4)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return "<h1>Привет, Веб! Это мой журнал успеваемости.</h1>"


@app.route('/health')
def health_check():
    return "<h1>Приложение работает!</h1>"

if __name__ == '__main__':
    # debug=True автоматически перезагружает сервер при изменении кода
    app.run(debug=True)

