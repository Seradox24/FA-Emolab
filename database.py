#database.py
from peewee import *
import hashlib
from playhouse.db_url import connect
from datetime import datetime

DATABASE_URL = "postgresql://fl0user:D0apdLeP8Jxj@ep-green-term-61680709.us-east-2.aws.neon.fl0.io:5432/panamdb?sslmode=require&options=endpoint%3Dep-green-term-61680709"

pg_db = connect(DATABASE_URL)

class User(Model):
    id = AutoField()
    nombre_usuario = CharField(max_length=50, unique=True)
    correo_electronico = CharField(max_length=50, unique=True)
    contraseña = CharField(max_length=256)
    #token_jwt = CharField(max_length=200,default='sintoken')
    fecha_registro = DateTimeField(default=datetime.now)
    estado = BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_usuario
    
    class Meta:
        database = pg_db
        table_name = 'users'
     
    @classmethod    
    def create_password(cls,contraseña):
        h = hashlib.md5()
        h.update(contraseña.encode('utf-8'))
        return h.hexdigest()

class Formulario(Model):
    id = AutoField()
    user_id = ForeignKeyField(User, backref='formularios')
    tipo = CharField(max_length=50, default='autoevaluacion')
    proyecto = CharField(max_length=100)
    hora_creacion = DateTimeField(default=datetime.now)
    respuesta = CharField(max_length=500)
    pregunta = CharField(max_length=500)

    def __str__(self):
        return f'{self.nombre} - {self.respuesta} - {self.pregunta}'

    class Meta:
        database = pg_db
        table_name = 'formularios'



class Presentacion(Model):
    id = AutoField()
    nombre = CharField(max_length=100)
    usuario = ForeignKeyField(User, backref='presentaciones')

    def __str__(self):
        return f'{self.usuario.nombre_usuario} - {self.nombre}'

    class Meta:
        database = pg_db
        table_name = 'presentaciones'

class Imagen(Model):
    id = AutoField()
    url = CharField(max_length=255)
    presentacion = ForeignKeyField(Presentacion, backref='imagen')

    def __str__(self):
        return self.url

    class Meta:
        database = pg_db
        table_name = 'imagenes'


    # Puedes almacenar las URLs de las imágenes como una cadena de texto
    # Aquí puedes agregar los campos que necesites para tu presentación

# Crear las tablas en la base de datos






'''




class Presentacion(Model):
    id = AutoField()
    nombre = CharField(max_length=100)
    usuario = ForeignKeyField(User, backref='presentaciones')
    imagenes = TextField() 
    def __str__(self):
        return f'{self.usuario.nombre_usuario} - {self.nombre}'
    class Meta:
        database = pg_db
        table_name = 'presentaciones'

class Formulario(Model):
    id_formulario = AutoField()
    usuario = ForeignKeyField(User, backref='formularios')
    tipo = CharField(max_length=50, default='autoevaluacion')
    nombre = CharField(max_length=100)
    hora_creacion = DateTimeField(default=datetime.now)
    numero_pregunta = IntegerField()
    # Aquí puedes agregar los campos que necesites para tu formulario
    def __str__(self):
        return self.nombre
    class Meta:
        database = pg_db
        table_name = 'formularios'



db.create_tables([User, Formulario, Presentacion])
class User(Model):
    username = CharField(max_length=50,unique=True)
    password = CharField(max_length=50)
    created_at= DateTimeField(default=datetime.now)
    
    def __str__(self):
        return self.username
    
    class Meta:
        database = pg_db
        table_name = 'users'

'''