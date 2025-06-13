from sqlalchemy.orm import Session
from models import Ejercicio, RespuestaUsuario, Tema, UserThemeProgress
from dependencies.security import strip_and_lower

def create_exercise_from_ai(data: dict, tema: Tema, db: Session) -> Ejercicio:
    ej = Ejercicio(
        enunciado   = data["enunciado"],
        tipo        = data["tipo"],
        dificultad  = data["dificultad"],
        respuesta   = data["respuesta"],
        explicacion = data.get("explicacion",""),
        tema_id     = tema.id
    )
    db.add(ej)
    db.commit()
    db.refresh(ej)
    return ej

def register_user_answer(user_id:int, ej:Ejercicio,
                         answer:str, time_sec:int|None, db:Session) -> bool:
    correcto = strip_and_lower(answer) == strip_and_lower(ej.respuesta)

    db.add(RespuestaUsuario(
        user_id=user_id, ejercicio_id=ej.id,
        respuesta=answer, correcto=correcto, tiempo_seg=time_sec
    ))

    prog = db.query(UserThemeProgress).get((user_id, ej.tema_id))
    if not prog:
        prog = UserThemeProgress(user_id=user_id, tema_id=ej.tema_id,
                                 completed=1, correct=1 if correcto else 0)
        db.add(prog)
    else:
        prog.completed += 1
        prog.correct   += 1 if correcto else 0

    db.commit()
    return correcto
