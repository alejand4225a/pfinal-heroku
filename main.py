from lib2to3.pgen2.pgen import NFAState
import string
import random
from tokenize import Double
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
import re
from hashlib import sha256
from email.message import EmailMessage
from smtplib import SMTP

from datetime import date, datetime
from config.database import db
cursor = db.cursor(dictionary=True)


app = Flask(__name__)
app.secret_key = "##91!IyAj#FqkZ2C"
mail=Mail(app)
s=URLSafeTimedSerializer('Thisisasecret')

@app.route("/")
def inicio():
    return render_template("registroNotas/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):

        email = request.form["email"]
        password = request.form["password"]
        password = sha256(password.encode("utf-8")).hexdigest()

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registro WHERE email = %s AND contraseña = %s AND confirmacion='1'",
            (
                email,
                password,
            ),
        )

        cuenta = cursor.fetchone()
        cursor.close()

        if cuenta:
            session["login"] = True
            session["id_usuario"] = cuenta["id_usuario"]
            session["email"] = cuenta["email"]
            return redirect(url_for("muro", email=email))
        else:

            flash("¡Nombre de usuario/contraseña incorrectos!")

    return render_template("registroNotas/iniciosesion.html")

@app.route("/login/muro/<email>", methods=["GET", "POST"])
def muroEstudiante(email):
    if (
        request.method == "POST"
        and "nombre" in request.form
        and "nota1" in request.form
        and "nota2" in request.form
        and "nota3" in request.form

    ):
        nombre = request.form['nombre']
        nota1 = request.form['nota1']
        nota2 = request.form['nota2']
        nota3 = request.form['nota3']

        if (
            not nombre
        ):
            flash("¡Por favor llene el formulario!")
        else:
           
            n1=""
            n11=""
            if not(nota1==''):
                n1=", "+str(float(nota1))
                n11=", nota1"

            n2=""
            n22=""
            if not(nota2==''):
                n2=", "+str(float(nota2))
                n22=", nota2"

            n3=""
            n33=""

            if not(nota3==''):
                n3=", "+str(float(nota3))
                n33=", nota3"

            nf=""
            nff=""
            if not(nota1=='') or not(nota2=='') or not(nota3==''):
                nf=str((float(nota1)+float(nota2)+float(nota3))/3)
                nf=", "+nf
                nff=", notaf"

          
            cursor = db.cursor()
            cursor.execute("SELECT id_usuario FROM registro WHERE email=%s", (email,)) 
            id_u=cursor.fetchone()

            sql="INSERT INTO estudiantes(nombre"+n11+n22+n33+nff+", id_registro) VALUES ('"+nombre+"'"+n1+n2+n3+nf+", "+str(id_u[0])+")"
            print(sql)
            cursor.execute(sql)            
            cursor.close()
            flash("Se agrego al estudiante "+nombre)

    return render_template("registroNotas/muro.html")

@app.route("/login/muro", methods=["GET", "POST"])
def notas():
    email=session['email']
    cursor = db.cursor()
    cursor.execute("SELECT id_usuario FROM registro WHERE email=%s", (email,)) 
    id_u=cursor.fetchone()
    cursor.execute("SELECT * FROM estudiantes WHERE id_registro="+str(id_u[0]))
    estudiantes = cursor.fetchall()
    cursor.close()
    return render_template("registroNotas/notas.html", estudiantes=estudiantes)

@app.route('/login/muro/eliminar_estuiante/<string:id>')
def eliminarEstudiante(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM estudiantes WHERE id_estudiante = %s", (id,))
    db.commit()
    return redirect(url_for('notas'))
    
@app.route('/login/muro/editar_notas/<string:id>')
def editarEstudiante(id):
    cursor = db.cursor()
    cursor.execute("SELECT id_estudiante,nombre, nota1, nota2, nota3 FROM estudiantes WHERE id_estudiante = %s", (id,))
    estudiante= cursor.fetchone()
    db.commit()
    return render_template("registroNotas/editarnotas.html", id=estudiante[0], nombre=estudiante[1], nota1=estudiante[2], nota2=estudiante[3], nota3=estudiante[4])

@app.route('/login/muro/editar_notas', methods=["GET", "POST"])
def editarfinal():
    if request.method == "POST":
        id_u= request.form.get('id')
        nombre = request.form.get('nombre')
        nota1 = request.form.get('nota1')
        nota2 = request.form.get('nota2')
        nota3 = request.form.get('nota3') 
        nombre_sql=''
        nota1_sql=''
        nota2_sql=''
        nota3_sql=''
        print("111")
        if not(nombre==''):
            nombre_sql= " nombre = '"+str(nombre)+"'"
        
        if not(nota1==''):
            nota1_sql= ", nota1 = '"+str(nota1)+"'"
        
        if not(nota2==''):
            nota2_sql= ", nota2 = '"+str(nota2)+"'"

        if not(nota3==''):
            nota3_sql= ", nota3 = '"+str(nota3)+"'"

        nf=str((float(nota1)+float(nota2)+float(nota3))/3)
        print("hola"+ id_u)
        sql="UPDATE estudiantes SET " + nombre_sql + nota1_sql + nota2_sql + nota3_sql +", notaf = '"+nf+"' WHERE id_estudiante = "+id_u
        print("1")
        print(sql)
        cursor = db.cursor()    
        cursor.execute(sql)
        cursor.close()
        flash('Se ha editado el producto correctamente')  
    return redirect(url_for('notas'))

@app.route("/login/muro/<email>", methods=["GET", "POST"])
def muro(email):
    if (
        request.method == "POST"
        and "imagen" in request.files
        and "descripcion" in request.form
    ):
        imagen = request.files['imagen']
        descripcion = request.form['descripcion']

        if (
            not imagen and
            not descripcion
        ):
            flash("¡Por favor llene el formulario!")
        else:
            today = date.today()
            now = datetime.now()
            fecha= str(today)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
            nombreImagen = imagen.filename
            imagen.save('./static/imagenes/' + nombreImagen)
            imagen_n=str(fecha)+nombreImagen
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id_usuario FROM registro WHERE email=%s", (email,)) 
            id_u=cursor.fetchone()
            cursor.execute("INSERT INTO imagenes(descripcion, imagen, id_registro) VALUES (%s, %s, %s)", (
                descripcion, imagen_n, id_u["id_usuario"],
            ))            
            cursor.close()
            flash("Se guardo el archivo correctamente")

    return render_template("registroNotas/muro.html")

@app.route("/registrousuario", methods=["GET", "POST"])
def registrousuario():
    if (
        request.method == "POST"
        and "nombre" in request.form
        and "email" in request.form
        and "password" in request.form
    ):

        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registro WHERE email = %s", (email,))
        cuenta = cursor.fetchone()
        
        token=s.dumps(email, salt='email-confirm')
        link= url_for('confirmarEmail', token=token, _external=True)

        caracterspecial = ["$", "@", "#", "%"]

        is_valid = True

        if cuenta:
            flash("Ya hay un usuario registrado con este correo!")
            is_valid = False

        if nombre == "":
            flash("El nombre es requerido")
            is_valid = False

        if not (len(password) >= 8 and len(password) <= 20):
            flash("La contraseña debe tener min 8 y max 20 caracteres")
            is_valid = False

        if not any(char.isdigit() for char in password):
            flash("La contraseña debe tener al menos un número")
            is_valid = False

        if not any(char.isupper() for char in password):
            flash("La contraseña debe tener al menos una letra mayúscula")
            is_valid = False

        if not any(char.islower() for char in password):
            flash("La contraseña debe tener al menos una letra minúscula")
            is_valid = False

        if not any(char in caracterspecial for char in password):
            flash("La contraseña debe tener al menos uno de los símbolos $,@,%,#,*")
            is_valid = False

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("¡Dirección de correo electrónico no válida!")
            is_valid = False

        if (not nombre or not email or not password):
            flash("¡Por favor llene el formulario!")
            is_valid = False
       

        if is_valid == False:
            return render_template(
                "registroNotas/registrousuario.html",
                nombre=nombre,
                email=email,
                password=password,
            )
        else:
            password = sha256(password.encode("utf-8")).hexdigest()
            cursor.execute(
                "INSERT INTO registro(nombre, email, contraseña) VALUES (%s, %s, %s)",
                (
                    nombre,
                    email,
                    password,
                ),
            )
            cursor.close()

            msg = EmailMessage()
            msg.set_content("Confirmar tu correo aqui: {} ".format(link))
            msg["Subject"] = "REGISTRO DE USUARIO"
            msg["From"] = "diegofernandoortega2020@itp.edu.co"
            msg["To"] = email
            username = "diegofernandoortega2020@itp.edu.co"
            password = "Diegofernan92Do"  
            server = SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            flash("¡Te has registrado con éxito!")

    elif request.method == "POST":
        flash("¡Por favor llene el formulario!")

    return render_template("registroNotas/registrousuario.html")

@app.route("/login/confirmarEmail/<token>")
def confirmarEmail(token):
    try:
        email=s.loads(token, salt='email-confirm', max_age=120)
        cursor = db.cursor()
        cursor.execute("UPDATE registro SET confirmacion='1' WHERE email='"+email+"'")
        cursor.close()
    except SignatureExpired:
        cursor = db.cursor()
        cursor.execute("DELETE FROM registro WHERE email='"+email+"' AND confirmacion='0'")
        cursor.close()
        return "<h1>Tiempo limite excedido</h1>"
    return "<h1>Bienvenido tu cuenta se ha confirmado con exito!</h1>"


@app.route("/restablecerpassword", methods=["GET", "POST"])
def restablecerpassword():
    if (
        request.method == "POST"
        and "email" in request.form
    ):
        email = request.form.get("email")
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM registro WHERE email = %s AND confirmacion='1'",
            (
                email,
            ),
        )
        cuenta = cursor.fetchone()
        cursor.close()

        if not(cuenta):
            flash('¡Esta cuenta no existe!')
            return render_template('registroNotas/index.html')

        token_password=s.dumps(email, salt='restablecer-password')
        link_password= url_for('cambiarPassword_a', token_password=token_password, _external=True)  

        msg = EmailMessage()
        msg.set_content("Para restablecer tu contraseña ingresa al siguiente link (Tiempo limite 2 min) : {} ".format(link_password))
        msg["Subject"] = "Recuperar contraseña"
        msg["From"] = "diegofernandoortega2020@itp.edu.co"
        msg["To"] = email
        username = "diegofernandoortega2020@itp.edu.co"
        password = "Diegofernan92Do" 
        server = SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        flash("Revisar el correo")

    return render_template("registroNotas/restablecercontraseña.html")
        

@app.route("/restablecerpassword_a/<token_password>")
def cambiarPassword_a(token_password):
    try:
        email=s.loads(token_password, salt='restablecer-password', max_age=60)
    except SignatureExpired:
        return render_template("registroNotas/restablecercontraseña.html")
    return redirect(url_for('cambiarContra', email=email, _external=True))

@app.route("/restablecerPass/<email>", methods=["GET", "POST"])
def cambiarContra(email):
    if request.method == "GET":
        return render_template("registroNotas/restablecerpassword.html")
    else:   
        password = request.form.get("password")
        password_verificacion= request.form.get("password_verificacion")
        if password==password_verificacion:
                caracterspecial = ["$", "@", "#", "%"]
                is_valid = True
                print(password)
                print(len(password))
                if not (int(len(password)) >= 8 and int(len(password)) <= 20):
                    flash("La contraseña debe tener min 8 y max 20 caracteres")
                    is_valid = False

                if not any(char.isdigit() for char in password):
                    flash("La contraseña debe tener al menos un número")
                    is_valid = False

                if not any(char.isupper() for char in password):
                    flash("La contraseña debe tener al menos una letra mayúscula")
                    is_valid = False

                if not any(char.islower() for char in password):
                        flash("La contraseña debe tener al menos una letra minúscula")
                        is_valid = False

                if not any(char in caracterspecial for char in password):
                        flash("La contraseña debe tener al menos uno de los símbolos $,@,%,#")
                        is_valid = False    

                if is_valid == False:
                    return render_template(
                        "registroNotas/restablecerpassword.html",
                        password=password,
                        password_verificacion=password_verificacion,
                    )   

                passwordencriptada = sha256(password.encode("utf-8")).hexdigest()
                cursor = db.cursor(dictionary=True)
                cursor.execute("UPDATE registro SET contraseña=%s WHERE email=%s",
                (
                    passwordencriptada,
                    email,
                ))
                cursor.close()
                flash("Contraseña corregida")
                return render_template("registroNotas/iniciosesion.html")
        else:
            flash("Comprobar de que las contraseñas sean iguales!")
            return render_template(
                    "registroNotas/restablecerpassword.html",
                    password=password,
                    password_verificacion=password_verificacion,
            )

@app.route("/exit")
def exit():
    session.clear()
    return redirect(url_for('login'))



#========================================================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("acortador/index.html")

@app.route("/create", methods=["GET", "POST"])
def createShortener():
    
    length_of_string = 3
    
    short =(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string)))
    if request.method == 'POST':
        url=request.form['dirUrl']
        cursor = db.cursor()
        sql= "INSERT INTO acortador (short_url,large_url) VALUES (%s,%s)"
        val = (short,url)
        cursor.execute(sql,val)
        db.commit()
    
    return render_template("acortador/shorteners/create.html", url=url,short=short)

@app.get("/short/<shortened>")
def redirection(shortened):
    sql = "SELECT large_url FROM acortador WHERE short_url = %(short_url)s"
    cursor = db.cursor()
    cursor.execute(sql,{'short_url':shortened})
    result = cursor.fetchone()
    print(result[0])
    
    return redirect(result[0])

#app.run(debug=True)
