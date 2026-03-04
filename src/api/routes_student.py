from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PomodoroState(BaseModel):
    is_active: bool
    minutes_left: int

@router.get("/pomodoro/status")
async def get_pomodoro_status():
    """Retorna o status atual do Pomodoro (Student Feature)."""
    return {"status": "inactive"}

@router.post("/pomodoro/start")
async def start_pomodoro(state: PomodoroState):
    """Inicia um temporizador remoto de Pomodoro."""
    return {"message": "Pomodoro started!"}
