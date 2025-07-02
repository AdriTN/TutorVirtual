from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from src.api.dependencies.auth import jwt_required # Importar jwt_required
from src.database.session import get_db
# No es necesario importar User directamente si jwt_required devuelve el payload con user_id
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
    token_payload: dict = Depends(jwt_required), # Usar jwt_required
):
    """
    Endpoint for a user to send a message in a chat.
    The message can be part of an existing conversation or start a new one
    if conversation_id is not provided (or doesn't match exercise_id and user_id).
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        # Esto no debería ocurrir si jwt_required funciona y el token tiene user_id.
        # Si jwt_required pasa pero user_id no está, es un problema de generación de token.
        logger.error("User ID not found in token payload after jwt_required")
        raise HTTPException(status_code=401, detail="User ID missing in token payload")

    try:
        logger.info("Processing user message")
        user_msg, ai_msg, conversation = await chat_service.process_user_message(
            db=db,
            user_message_input=user_message_input,
            user_id=current_user_id, # Usar el ID obtenido del token
            request=request 
        )
        db.refresh(conversation)
        return ChatConversationResponse.from_orm(conversation)

    except HTTPException as e:
        raise e 
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/conversation/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(jwt_required), # Usar jwt_required
):
    """
    Retrieves the history of a specific chat conversation.
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        raise HTTPException(status_code=403, detail="User ID not found in token")

    try:
        conversation = await chat_service.get_conversation_history(
            db=db, conversation_id=conversation_id, user_id=current_user_id
        )
        return ChatConversationResponse.from_orm(conversation)
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation.")


@router.get("/exercise/{exercise_id}", response_model=List[ChatConversationResponse])
async def get_exercise_conversations(
    exercise_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(jwt_required), # Usar jwt_required
):
    """
    Retrieves all chat conversations for a given exercise by the current user.
    Typically, this will be one conversation, but the backend supports multiple.
    The frontend might choose to display the latest or allow selection.
    """
    current_user_id = token_payload.get("user_id")
    if not current_user_id:
        raise HTTPException(status_code=403, detail="User ID not found in token")

    try:
        conversations = await chat_service.get_user_conversations_for_exercise(
            db=db, user_id=current_user_id, exercise_id=exercise_id
        )
        return [ChatConversationResponse.from_orm(conv) for conv in conversations]
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail="Failed to retrieve exercise conversations.")
