from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from . import models, schemas, security, database

# Crear la aplicación FastAPI
app = FastAPI(title="Motor ETL BIM - API Authentication")

# Configuración CORS: Esencial para que Vue (que corre en otro puerto) pueda comunicarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto por el puerto exacto de Vue (ej. http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login", response_model=schemas.Token)
def login(
    request: Request, # Capturamos el objeto Request para extraer IP y navegador
    form_data: schemas.UserLogin, 
    db: Session = Depends(database.get_db)
):
    # 1. Buscar el usuario en la BD por su username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 2. Validar credenciales
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Validar estado del usuario (Inactivación lógica)
    if not user.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario se encuentra inactivo."
        )

    # 4. Generar el Token JWT
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 5. Auditoría: Registrar la sesión en la base de datos
    ip_cliente = request.client.host if request.client else "Desconocida"
    user_agent = request.headers.get("user-agent", "Desconocido")

    nueva_sesion = models.Sesion(
        user_id=user.id,
        token_sesion=access_token,
        ip_terminal=ip_cliente,
        user_agent=user_agent
    )
    
    db.add(nueva_sesion)
    db.commit()

    # 6. Responder al frontend con el token generado
    return {"access_token": access_token, "token_type": "bearer"}