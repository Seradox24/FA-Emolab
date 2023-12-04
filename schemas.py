#schemas.py
from typing import Any
from pydantic import BaseModel
from pydantic import validator
#from pydantic.utils import GetterDict
from pydantic.v1.utils import GetterDict
from peewee import ModelSelect

class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default:Any = None ):
        
        res = getattr(self._obj, key, default )
        if isinstance(res, ModelSelect):
            return list(res)
        
        return res


class ResponseModel(BaseModel):
    class Config:
        from_attributes: True    
    


class UserRequestModel(BaseModel):
    nombre_usuario: str
    contraseña: str
    correo_electronico : str
    
    @validator('nombre_usuario')
    def nombre_usuario_validator(cls,nombre_usuario):
        if len(nombre_usuario) < 3 or len(nombre_usuario) > 50:
            raise ValueError('la longitud debe encontrase entre 3 y 50')
        return nombre_usuario
    
class UserResponseModel(ResponseModel):
    id:int
    nombre_usuario: str
    
#    class Config:
#        from_attributes: True
#        orm_mode= True
#        getter_dict =PeeweeGetterDict
 
class FormularioRequestModel(BaseModel):
    user_id:int
    tipo:str
    proyecto:str
    respuesta:str
    pregunta:str    


class FormularioResponseModel(ResponseModel):
    id:int
    tipo:str
    proyecto:str
    respuesta:str
    pregunta:str
    
#codigo agregado 

class Presentacion(BaseModel):
    id: int
    nombre: str
    usuario: int

class Imagen(BaseModel):
    id: int
    url: str
    presentacion: int