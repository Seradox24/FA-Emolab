from pydantic import BaseModel

class UserBaseModel(BaseModel):
    nombre_usuario: str
    contraseña: str
    correo_electronico : str