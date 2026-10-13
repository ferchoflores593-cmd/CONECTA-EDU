from flask import Flask, render_template, request, redirect
import sqlite3
import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS solicitudes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, recurso TEXT, contacto TEXT, estado TEXT, fecha TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS recursos (id INTEGER PRIMARY KEY, titulo TEXT, descripcion TEXT, lugar TEXT)')
    c.execute('SELECT COUNT(*) FROM recursos')
    if c.fetchone()[0] == 0:
        datos = [
            ('Internet Infocentro', 'Acceso a PCs e Internet', 'Casa Comunal'),
            ('Curso Computacion', 'Basico para adultos', 'ConQuito'),
            ('Prestamo Laptops', '15 dias para tareas', 'Biblioteca'),
            ('Tramites IESS', 'Ayuda en linea', 'Infocentro')
        ]
        c.executemany('INSERT INTO recursos (titulo, descripcion, lugar) VALUES (?,?,?)', datos)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recursos')
    r = c.fetchall()
    conn.close()
    return render_template('index.html', recursos=r)

@app.route('/solicitar', methods=['GET','POST'])
def solicitar():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO solicitudes VALUES (NULL,?,?,?,?,?)', (request.form['nombre'], request.form['recurso'], request.form['contacto'], 'Pendiente', datetime.datetime.now().strftime('%d/%m/%Y')))
        conn.commit()
        conn.close()
        return redirect('/seguimiento?contacto=' + request.form['contacto'])
    return render_template('solicitar.html', recurso_pre=request.args.get('recurso',''))

@app.route('/seguimiento')
def seguimiento():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    cont = request.args.get('contacto')
    if cont:
        c.execute('SELECT * FROM solicitudes WHERE contacto=? ORDER BY id DESC', (cont,))
    else:
        c.execute('SELECT * FROM solicitudes ORDER BY id DESC')
    s = c.fetchall()
    conn.close()
    return render_template('admin.html', solicitudes=s, filtro=cont)

@app.route('/admin/cambiar/<int:id>/<string:nuevo_estado>')
def cambiar_estado(id, nuevo_estado):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE solicitudes SET estado=? WHERE id=?', (nuevo_estado, id))
    conn.commit()
    conn.close()
    return redirect('/seguimiento')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)