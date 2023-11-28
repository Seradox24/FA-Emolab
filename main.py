from fastapi import FastAPI
from database import pg_db as connection
from database import User
from database import Formulario
from database import Presentacion
from schemas import UserBaseModel

app = FastAPI()

@app.on_event('startup')
def startup():
    if connection.is_closed():
        connection.connect()
        print('connecting....')
    connection.create_tables([User, Formulario, Presentacion])
    
    
@app.on_event('shutdown')
def shutdown():
    if not connection.is_closed():
        connection.close()
        print('close....')
        
    
    

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post('/users/')
async def create_user(user: UserBaseModel):
    user = User.create(
        nombre_usuario=user.nombre_usuario,
        contraseña=user.contraseña,
        correo_electronico=user.correo_electronico
    )
    return user.id_usuario
    
