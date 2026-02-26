import os
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import jwt
import bcrypt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configurações JWT e Hashing
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-sovereign-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Dias logado
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

router = APIRouter()

# Modelos Pydantic
class SetupRequest(BaseModel):
    owner_name: str
    sovereign_name: str
    password: str

class LoginRequest(BaseModel):
    password: str

# Funções Auxiliares
def verify_password(plain_password, hashed_password):
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_config_path() -> Path:
    return Path(os.environ.get("SOVEREIGN_CONF", "~/.config/sovereign.conf")).expanduser()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """ Validador JWT para injetar como Dependência nas Rotas Privadas """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


# Rotas
@router.post("/setup")
async def setup_system(req: SetupRequest):
    """ Chamada da UI de Oboarding - Roda 1 única vez para travar a base """
    conf_path = get_config_path()
    
    # Se o master password hash já existe, o setup está bloqueado.
    if conf_path.exists():
        with open(conf_path, "r") as f:
            content = f.read()
            if "VAULT_LOCK_KEY=" in content:
                raise HTTPException(status_code=400, detail="System já foi configurado. Use Login.")

    conf_path.parent.mkdir(parents=True, exist_ok=True)
    hash_pwd = get_password_hash(req.password)
    
    # Adicionar no conf (Append mode para não apagar nada pré-existente sem querer)
    with open(conf_path, "a") as f:
        f.write(f"\n# Auth Identity\n")
        f.write(f"OWNER_NAME={req.owner_name}\n")
        f.write(f"SOVEREIGN_NAME={req.sovereign_name}\n")
        f.write(f"VAULT_LOCK_KEY={hash_pwd}\n")
        
    # Já retorna um token logado
    access_token = create_access_token(data={"sub": req.owner_name}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"message": "Setup concluded", "access_token": access_token, "token_type": "bearer"}


@router.post("/login")
async def login_user(req: LoginRequest):
    conf_path = get_config_path()
    
    if not conf_path.exists():
        raise HTTPException(status_code=404, detail="System not configured yet.")
        
    master_hash = None
    owner = "Jeferson"
    
    with open(conf_path, "r") as f:
        for line in f:
            if line.startswith("VAULT_LOCK_KEY="):
                master_hash = line.strip().split("=", 1)[1]
            if line.startswith("OWNER_NAME="):
                owner = line.strip().split("=", 1)[1]
                
    if not master_hash:
        raise HTTPException(status_code=400, detail="Password hash not set in conf.")
        
    if not verify_password(req.password, master_hash):
        raise HTTPException(status_code=401, detail="Incorrect password.")
        
    access_token = create_access_token(data={"sub": owner}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/status")
async def auth_status():
    """ Rota pública para a Web-UI saber se manda o usuário para /setup ou /login """
    conf_path = get_config_path()
    is_setup = False
    
    if conf_path.exists():
        with open(conf_path, "r") as f:
            is_setup = "VAULT_LOCK_KEY=" in f.read()
            
    return {"is_setup": is_setup}
