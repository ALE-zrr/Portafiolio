from flask import Flask, render_template, request, redirect, session, url_for
from Coneccion import * 
from functools import wraps
import datetime
from random import sample
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'a8f$3Lk@9zQ1!xR7wT2#vB6mN0pQ4sE'  # Clave secreta para proteger sesiones

# 🔒 Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return "Ruta no encontrada"

# 🔐 Decorador para proteger rutas que requieren sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 🔁 Generador de string aleatorio (puede usarse para nombres de archivos, tokens, etc.)
def stringAleatorio():
    string_aleatorio = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    longitud = 20
    secuencia = string_aleatorio.upper()
    resultadoaleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultadoaleatorio)
    return string_aleatorio

# 🏠 Página principal
@app.route('/')
def mostrar_inicio():
    skill = "SELECT * FROM habilidades"
    habilidades = consulta(skill)
    return render_template('index.html', index=True, habilidades=habilidades)

# 📩 Formulario de contacto
@app.route("/Formulario", methods=["GET", "POST"])
def contacto():
    msg = ""
    if request.method == "POST":
        Nombre = request.form["name"]
        Correo = request.form["email"]
        Telefono = request.form["phone"]
        Mensaje = request.form["mensaje"]

        conexion = connection()
        cursor = conexion.cursor(dictionary=True)

        insertar = ("INSERT INTO contacto (Nombre, Correo, Telefono, Mensaje) VALUES (%s, %s, %s, %s)")
        valores = (Nombre, Correo, Telefono, Mensaje)
        cursor.execute(insertar, valores)
        conexion.commit()

        cursor.close()
        conexion.close()
        msg = "Mensaje enviado correctamente"

        return render_template("/Formulario.html", msg=msg, Formulario=True)
    
    return render_template("/Formulario.html", msg="Metodo incorrecto", Formulario=True)

# 👤 Página pública "Acerca de mí"
@app.route("/acercademi")
def acercademi():
    return render_template("Acerca-de-mi.html", Acerca_de_mi=True)

# 📁 Página pública de proyectos
@app.route("/Proyectos")
def proyectos():
    return render_template("Proyectos.html", Proyectos=True)

# 🔍 Función para ejecutar consultas SQL
def consulta(consulta, parametros=None):
    resultado = []
    try:
        conexion = connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(consulta, parametros or ())
        resultado = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error en consulta:", e)
    return resultado

# 🗨️ Comentarios (protegido)
@app.route('/comentarios', methods=['GET', 'POST'])
@login_required
def comentarios():
    query = "SELECT * FROM contacto"
    mensajes = consulta(query)
    return render_template('admin/comentarios.html', mensajes=mensajes, comentarios=True)

# 🔐 Login de usuario
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    resultado = None

    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conexion = connection()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
        cursor.execute(query, (usuario, password))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            session["usuario"] = resultado["usuario"]  # Guarda el usuario en sesión
            return redirect('/admin')
        else:
            mensaje = "Usuario o contraseña incorrecta"

    return render_template('login.html', mensaje=mensaje, login=True)

# 🚪 Logout
@app.route('/logout')
def logout():
    session.pop("usuario", None)
    return redirect('/login')

# 🛡️ Panel de administración (protegido)
@app.route("/admin")
@login_required
def admin():
    return render_template("admin/admin.html", admin=True)

# 🧠 Gestión de habilidades (protegido)
@app.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    msg = ""
    skill = "SELECT * FROM habilidades"
    habilidades = consulta(skill)

    if request.method == "POST":
        Nombre = request.form["habilidad"]
        Descripcion = request.form["descripcion"]
        Svg = request.form["svg"]

        conexion = connection()
        cursor = conexion.cursor(dictionary=True)

        insertar = ("INSERT INTO habilidades (Nombre, Descripcion, Svg) VALUES (%s, %s, %s)")
        valores = (Nombre, Descripcion, Svg)
        cursor.execute(insertar, valores)
        conexion.commit()

        cursor.close()
        conexion.close()
        msg = "Mensaje enviado correctamente"

        return redirect(url_for('skills'))
    
    return render_template("admin/habilidades.html", msg="Metodo incorrecto", skills=True , habilidades=habilidades)

# 🗑️ Eliminar habilidad (protegido)
@app.route("/eliminar_habilidad", methods=["POST"])
@login_required
def eliminar_habilidad():
    id = request.form["id"]

    try:
        conexion = connection()
        cursor = conexion.cursor()
        eliminar = "DELETE FROM habilidades WHERE id = %s"
        cursor.execute(eliminar, (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        print("Habilidad eliminada con ID:", id)
    except Exception as e:
        print("Error al eliminar:", e)

    return redirect("/skills")

# 🧩 Panel de proyectos (protegido)
@app.route("/adminproyectos")
@login_required
def adminproyectos():
    return render_template("admin/Adminproyectos.html", adminproyectos=True)

# 🚀 Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)