from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   make_response)
from config import conn, cursor
import hashlib
import datetime
# import locale

# locale.setlocale(locale.LC_TIME, 'uk_UA')



app = Flask(__name__)

@app.route('/')
def index():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username varchar(32), password varchar(32))")
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, username varchar(32), title varchar(50), text varchar(5000), date varchar(32))")

    conn.commit()
    if request.cookies:
        login = request.cookies.get('username')
        action = '/profile'
        
        cursor.execute("SELECT id, title, text, date FROM notes WHERE username = ? ORDER BY id DESC", (login,))
        notes = cursor.fetchall()

        return render_template('index.html', login=login, action=action, notes=notes)
    else:
        login = 'Вхід'
        action = '/login'
        return render_template('login.html')

@app.route('/new-note')
def title():
    return render_template('new-note.html')

@app.route('/note')
def note():
    id = request.args.get('id')
    login = request.cookies.get('username')

    cursor.execute("SELECT id, title, text FROM notes WHERE id = ?", (id,))
    notes = cursor.fetchall()

    return render_template('note.html', note=notes)

@app.route('/note-submit', methods=['POST'])
def submit():
    title = request.form['title']
    text = request.form['text']
    username = request.cookies.get('username')
    now = datetime.datetime.now()
    date = now.strftime("%a, %d.%m<br>%H:%M")

    cursor.execute("INSERT INTO notes (username, title, text, date) VALUES (?, ?, ?, ?)", (username, title, text, date,))
    conn.commit()
 
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/log', methods=['POST'])
def log():
    username = request.form['username']
    password = request.form['password']
    md5 = hashlib.md5(password.encode()).hexdigest()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, md5,))
    data = cursor.fetchall()

    if len(data) > 0:
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('username', username, max_age=2592000)
        return resp
    else:
        return render_template('login.html', error='Неправильний логін чи пароль')

@app.route('/reg', methods=['POST'])
def reg():
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']

    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    data = cursor.fetchall()

    if len(data) > 0:
        return render_template('register.html', error='exists')

    if len(username) == 0 or len(password) == 0 or len(password2) == 0:
        return render_template('register.html', error='Введи усі дані')
    elif len(username) < 5 or len(username) > 20:
        return render_template('register.html', error='Ім\'я користувача від 5 до 20 символів')
    elif len(password) < 8 or len(password) > 20:
        return render_template('register.html', error='Пароль від 8 до 20 символів')
    elif password != password2:
        return render_template('register.html', error='Паролі не збігаються')
    else:
        md5 = hashlib.md5(password.encode()).hexdigest()

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, md5,))
        conn.commit()
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('username', username, max_age=2592000)
        return resp

@app.route('/profile')
def profile():
    login = request.cookies.get('username')

    cursor.execute("SELECT * FROM notes WHERE username = ?", (login,))
    notes = len(cursor.fetchall())

    if login == 'nazar.rudenok':
        achievement = 'батько цієї тусовки'
    elif notes < 5:
        achievement = 'та так, спробую'
    elif notes < 10:
        achievement = 'норм тєма'
    elif notes < 15:
        achievement = 'шоб не забути'
    elif notes < 20:
        achievement = 'вже звичка'
    else:
        achievement = 'як Отче наш'
    
    return render_template('profile.html', username=login, notes=notes, achievement=achievement)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('username')
    return response

@app.route('/update-note', methods=['POST'])
def update_note():
    title = request.form['title']
    text = request.form['text'].replace('<br>', '')
    id = request.args.get('id')
    
    cursor.execute("UPDATE notes SET title = ?, text = ? WHERE id = ?", (title, text, id,))
    conn.commit()

    return redirect(url_for('index'))

@app.route('/delete-note')
def delete_note():
    id = request.args.get('id')

    cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    # app.run(debug=True, host= '192.168.1.249')
    app.run(debug=False, host='0.0.0.0')