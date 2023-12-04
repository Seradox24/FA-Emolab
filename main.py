#main.py
from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from database import pg_db as connection
from database import User
from database import Formulario
from database import Presentacion
from database import Imagen

import os

from fastapi.security  import HTTPBasicCredentials
from schemas import UserRequestModel
from schemas import UserResponseModel
from schemas import FormularioRequestModel
from schemas import FormularioResponseModel
from datetime import datetime
from typing import List
from fastapi.responses import FileResponse
from os import getcwd, remove, makedirs
from shutil import rmtree





app = FastAPI()

@app.on_event('startup')
def startup():
    if connection.is_closed():
        connection.connect()
        print('connecting....')
    connection.create_tables([User, Formulario, Presentacion,Imagen])
    
    
@app.on_event('shutdown')
def shutdown():
    if not connection.is_closed():
        connection.close()
        print('close....')
        
    
    

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/users/',response_model=UserResponseModel)
async def create_user(user: UserRequestModel):
    
    if User.select().where(User.nombre_usuario == user.nombre_usuario).exists():
        return HTTPException(409,'el usuario ya existe')
    
    hash_password=User.create_password(user.contraseña)
    user = User.create(
        nombre_usuario=user.nombre_usuario,
        contraseña=hash_password,
        correo_electronico=user.correo_electronico
    )
    return user

@app.post('/login')
async def login(credentials:HTTPBasicCredentials):
    user= User.select().where(User.nombre_usuario == credentials.username).first()
    if user is None:
        raise HTTPException(404,'user not found')
        
    if user.contraseña != User.create_password(credentials.password):
        raise HTTPException(404,'password error')
    
    return user


    
@app.post('/formularios',response_model=FormularioResponseModel)
async def create_formulario(user_formulario:FormularioRequestModel):
    
    if User.select().where(User.id==user_formulario.user_id).first() is None:
        raise HTTPException(status_code=404, detail='user not found')
    
    user_formulario= Formulario.create(
        user_id = user_formulario.user_id,
        tipo = user_formulario.tipo,
        proyecto = user_formulario.proyecto,
        respuesta = user_formulario.respuesta,
        pregunta = user_formulario.pregunta  
        
    )
    
    return user_formulario

@app.get('/formularios',response_model=List[FormularioResponseModel])   
async def get_formularios():
    formularios=Formulario.select()
    return [formulario for formulario in formularios] 


#codigo de prueba 

#crea la carpeta y agrega a la tabla presentacion id nombre y uid
#punto de save
@app.post('/presentaciones')
async def crear_presentacion(nombre: str, usuario_id: int):
    try:
        presentacion = Presentacion.create(nombre=nombre, usuario=usuario_id)
        carpeta_presentacion = os.path.join("PresentacionesIMG", f"{usuario_id}_{presentacion.id}")
        makedirs(carpeta_presentacion)
        return JSONResponse(content={
            "created": True,
            "presentacion_id": presentacion.id
        }, status_code=200)
               
    except Exception as e:
        return JSONResponse(content={
            "created": False,
            "message": str(e)
        }, status_code=500)

@app.get('/presentaciones/{usuario_id}')
async def listar_presentaciones_usuario(usuario_id: int):
    try:
        presentaciones = Presentacion.select().where(Presentacion.usuario == usuario_id)
        presentaciones_dict = []
        for p in presentaciones:
            urls = []
            carpeta_imagenes = os.path.join("PresentacionesIMG", f"{usuario_id}_{p.id}")
            for filename in os.listdir(carpeta_imagenes):
                url = f'http://127.0.0.1:8000/presentaciones/{p.id}/imagenes/{filename}?user_id={usuario_id}'
                urls.append(url)
            presentacion_dict = {"id": p.id, "nombre": p.nombre, "urls": urls}
            presentaciones_dict.append(presentacion_dict)
        return JSONResponse(content=presentaciones_dict, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



@app.post('/presentaciones/{presentacion_id}/imagenes')
async def cargar_imagenes(presentacion_id: int, user_id: int, files: List[UploadFile] = File(...)):
    try:
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{timestamp}_{file.filename}'
            ruta_archivo = os.path.join("PresentacionesIMG", f"{user_id}_{presentacion_id}", filename)
            with open(ruta_archivo, "wb") as myfile:
                content = await file.read()
                myfile.write(content)
            print(f'La imagen se guardó en {ruta_archivo}')
            
            # Construye la URL correspondiente
            url = f'http://127.0.0.1:8000/presentaciones/{user_id}/imagenes/{filename}?user_id={presentacion_id}'
            
            # Crea una nueva instancia de Imagen y guarda la URL en la base de datos
            imagen = Imagen(url=url, presentacion=presentacion_id)
            imagen.save()
            
        return JSONResponse(content={"saved": True}, status_code=200)
               
    except FileNotFoundError:
        return JSONResponse(content={"saved": False}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"saved": False, "message": str(e)}, status_code=500)



@app.get('/presentaciones_id/{presentacion_id}/imagenes')
async def listar_imagenes(presentacion_id: int):
    try:
        imagenes = Imagen.select().where(Imagen.presentacion == presentacion_id)
        imagenes_dict = [{"id": i.id, "url": i.url} for i in imagenes]
        return JSONResponse(content=imagenes_dict, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/presentaciones/{presentacion_id}/imagenes/{filename}")
async def ver_imagen(presentacion_id: int, user_id: int, filename: str):
    ruta_archivo = os.path.join("PresentacionesIMG", f"{presentacion_id}_{user_id}", filename)
    if os.path.exists(ruta_archivo):
        print(f"La imagen se encuentra en {ruta_archivo}")
        return FileResponse(ruta_archivo)
    else:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

@app.get('/presentaciones/{presentacion_id}/imagenes')
async def listar_imagenes(presentacion_id: int, user_id: int):
    try:
        urls = []
        carpeta_imagenes = os.path.join("PresentacionesIMG", f"{user_id}_{presentacion_id}")
        for filename in os.listdir(carpeta_imagenes):
            url = f'http://127.0.0.1:8000/presentaciones/{user_id}/imagenes/{filename}?user_id={presentacion_id}'
            urls.append(url)
        return JSONResponse(content={"urls": urls}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"urls": []}, status_code=404)


@app.delete("/presentaciones/{presentacion_id}/imagenes/{filename}")
async def eliminar_imagen(presentacion_id: int, filename: str):
    try:
        remove(f"PresentacionesIMG/{presentacion_id}/{filename}")
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "message": "File not found"
        }, status_code=404)


@app.delete("/presentaciones/{presentacion_id}")
async def eliminar_presentacion(presentacion_id: int):
    try:
        rmtree(f"PresentacionesIMG/{presentacion_id}")
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "message": "Folder not found"
        }, status_code=404)


'''

@app.post('/presentaciones/{presentacion_id}/imagenes')
async def cargar_imagenes(presentacion_id: int, user_id: int, files: List[UploadFile] = File(...)):
    try:
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{timestamp}_{file.filename}'
            ruta_archivo = os.path.join("PresentacionesIMG", f"{user_id}_{presentacion_id}", filename)
            with open(ruta_archivo, "wb") as myfile:
                content = await file.read()
                myfile.write(content)
            print(f'La imagen se guardó en {ruta_archivo}')
        return JSONResponse(content={"saved": True}, status_code=200)
               
    except FileNotFoundError:
        return JSONResponse(content={"saved": False}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"saved": False, "message": str(e)}, status_code=500)

    
    
@app.post('/multiple/files')
async def upload_multiple_files(files: List[UploadFile]= File(...)):
    try:
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{timestamp}_{file.filename}'
            with open(f'PresentacionesIMG/{filename}',"wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
            print(f'La imagen se guardó en PresentacionesIMG/{filename}')
        return JSONResponse(content={
            "saved":True
        },status_code=200)
               
    except FileNotFoundError:
        return JSONResponse(content={
            "saved":False
        },status_code=404)


@app.get("/imagenes/{filename}")
async def ver_imagen(filename: str):
    return FileResponse(f"PresentacionesIMG/{filename}")
------------------
@app.post('/multiple/files')
async def upload_multiple_files(files: List[UploadFile]= File(...)):
    try:
        for file in files:
            with open(file.filename,"wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
        return JSONResponse(content={
            "saved":True
        },status_code=200)
               
    except FileNotFoundError:
        return JSONResponse(content={
            "saved":False
        },status_code=404)

@app.post('/multiple/files')
async def upload_multiple_files(files: List[UploadFile]= File(...)):
    try:
        for file in files:
            with open(f'PresentacionesIMG/{file.filename}',"wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
        return JSONResponse(content={
            "saved":True
        },status_code=200)
               
    except FileNotFoundError:
        return JSONResponse(content={
            "saved":False
        },status_code=404)

'''        