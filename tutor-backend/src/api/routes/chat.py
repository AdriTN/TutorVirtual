from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from src.api.dependencies.auth import jwt_required
from src.database.session import get_db
from src.services import chat_service
from src.api.schemas.chat import UserMessageInput, ChatMessageResponse, ChatConversationResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ChatConversationResponse)
async def send_message(
    user_message_input: UserMessageInput,
    request: Request, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(jwt_required),
):
    """
    Endpoint para enviar un mensaje del usuario y recibir una respuesta del modelo AI.
    El mensaje del usuario se procesa y se guarda en la base de datos,
    y se devuelve la conversación actualizada.
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        logger.error("El ID de usuario no se encontró en el token")
        raise HTTPException(status_code=401, detail="El ID de usuario no se encontró en el token")

    try:
        logger.info("Procesando mensaje del usuario")
        user_msg, ai_msg, conversation = await chat_service.process_user_message(
            db=db,
            user_message_input=user_message_input,
            user_id=current_user_id,
            request=request 
        )
        db.refresh(conversation)
        return ChatConversationResponse.from_orm(conversation)

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hubo un errore inesperado: {str(e)}")


@router.get("/conversation/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(jwt_required),
):
    """
    Recupera el historial de mensajes de una conversación específica.
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        raise HTTPException(status_code=403, detail="El ID de usuario no se encontró en el token")

    try:
        conversation = await chat_service.get_conversation_history(
            db=db, conversation_id=conversation_id, user_id=current_user_id
        )
        return ChatConversationResponse.from_orm(conversation)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="No se pudo recuperar la conversación.")


@router.get("/exercise/{exercise_id}", response_model=List[ChatConversationResponse])
async def get_exercise_conversations(
    exercise_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(jwt_required),
):
    """
    Todas las conversaciones de chat asociadas a un ejercicio específico.
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        raise HTTPException(status_code=403, detail="No se encontró el ID de usuario en el token")

    try:
        conversations = await chat_service.get_user_conversations_for_exercise(
            db=db, user_id=current_user_id, exercise_id=exercise_id
        )
        return [ChatConversationResponse.from_orm(conv) for conv in conversations]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="No se pudieron recuperar las conversaciones del ejercicio.")
