import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory


app=Flask(__name__)

app.secret_key="AsDfcreIO173490"

mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='root'
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)


@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/img/<imagen>')
def imagenes(imagen):    
    return send_from_directory( os.path.join('templates/sitio/img'),imagen)

@app.route('/css/<archivocss>')
def css_link(archivocss):
    return send_from_directory( os.path.join('templates/sitio/css'),archivocss)
    


@app.route('/libros')
def libros():
    conexion=mysql.connect()      
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM libros;")
    libros=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/libros.html', libros=libros)


@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_loguin():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=[ 'POST'])
def admin_login_post():
    _usuario=request.form['textUsuario']
    _password=request.form['textPassword']
    
    if _usuario=="admin" and _password=="admin":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")
    
    if _usuario=="usuario" and _password=="1234":
        session["login"]=True
        session["usuario"]="Usuario"
        return redirect("/admin")
    
    return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')



@app.route('/admin/libros')
def admin_libros():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    conexion=mysql.connect()      
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM libros;")
    libros=cursor.fetchall()
    conexion.commit()
    return render_template('admin/libros.html', libros=libros)

@app.route('/admin/libros/guardar', methods=[ 'POST'])
def admin_libros_guardar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    _nombre=request.form['textNombre'] 
    _archivo=request.files['textImagen']
    _url=request.form['textURL']
    # se genera la hora actual para adjuntarlo al nombre de archivo imagen     
    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')
    # se verifica que el archivo esta vacio y se procede a dar nombre y guardarlo en la carpeta de img
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)
    
    
    sql="INSERT INTO libros ( nombre,imagen,url) VALUES ( %s, %s, %s);"
    datos=(_nombre,nuevoNombre,_url)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()        
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=[ 'POST'])
def admin_libros_borrar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id=request.form['textID']   
    # opcional previo al borrado del registro
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM libros WHERE id=%s", (_id)) 
    libro=cursor.fetchall()
    conexion.commit()    
        
    if os.path.exists("templates/sitio/img"+str(libro[0][0])):
        os.unlink("templates/sitio/img"+str(libro[0][0]))
          
    # comando de borrado de registro
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s", (_id))    
    conexion.commit()         
    return redirect('/admin/libros')
    


if __name__ == '__main__':
    app.run(debug=True)