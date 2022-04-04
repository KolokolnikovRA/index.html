from flask import Flask, g, render_template, url_for, request, abort, flash, session, redirect
import sqlite3
import os

#Конфигурация
DATABASE = '/tmp/flsite.db' #Путь к базе данных с которыми мы работаем
DEBUG = True
SECRET_KEY = "23SabedO23"
USERNAME = 'admin'
PASSWORD = 'admin'

#Создаем создаем наше приложение
app = Flask(__name__)
app.config.from_object(__name__)
# Загружаем конфиг по умолчанию и переопределяем в конфигурации часть
# значений через переменную окружения
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'flsite.db'),#Переписываем адрес нашей базы даннах в на текущий каталог
    DEBUG = True,
    SECRET_KEY = "23SabedO23",
    USERNAME = 'admin',
    PASSWORD = 'admin'
    ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


#Начала работы с БД
def connect_db():
    #Подключаемся к базе данных
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """ Вспомогательная функция для создания таблиц БД название базы данной, которую мы создали и написали текст
    для создания 1 таблицы и 3 значения столбцов """
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()
        db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено   link_db по сути любое название"""
    if not hasattr(g,'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g,'link_db'):
        g.link_db.close()


# def create_db():
#     """ Вспомогательная функция для создания таблиц БД"""
#     db = connect_db()
#     with app.open_resource('sq_db.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#         db.commit()
#         db.close()







# menu = [{"name":"Установка","url":"instal-flask"},
#         {"name":"Первое приложение","url":"first-app"},
#         {"name":"Обратная связь","url":"contact"}]



@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select title, url from entries order by id desc')
    entries = cur.fetchall()

    return render_template("show_entries.html", entries=entries,  menu = [])

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/about')
def about():
    print(url_for('about'))
    return render_template("about.html", title = "О сайте",menu = menu)

@app.route('/contact', methods = ["POST","GET"])
def contact():
    # Здесь мы можем отбирать данные с формы как
    # request.form['username',email, message]
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template("contact.html", title = "Контакты",menu = menu)


@app.route('/login', methods=["POST","GET"])
def login():
    # if 'userLogged' in session:
    #     return redirect(url_for('profile', username=session['userLogged']))
    # elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
    #     session['userLogged'] = request.form['username']
    #     return redirect(url_for('profile', username = session['userLogged']))
    #
    # return render_template('login.html',title = 'Авторизация' , menu = menu)

    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login_a.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.errorhandler(404)
def pageNotFount(error):
    return render_template("page404.html", title = "Страница не найдена", menu = menu),404


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"Пользователь {username}"


#
# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('about'))
#     print(url_for('profile', username = 'selfedu'))


if __name__ == "__main__":
    #Запуск фрейворка, debug = True для того, что бы мы видели ошибки при создание сайта,
    #после завершения изменить на False
    app.run(debug=True)