from pydantic import BaseModel

# Modelo para recibir los datos del formulario de Vue
class UserLogin(BaseModel):
    username: str
    password: str

# Modelo para responder al frontend tras un login exitoso
class Token(BaseModel):
    access_token: str
    token_type: str