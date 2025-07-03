from sqlalchemy.orm import Session
# Removed: from sqlalchemy.future import select - Not used directly here
# Removed: from sqlalchemy.ext.asyncio import AsyncSession - Will be handled when DB calls are made async
# (Keeping Session for now as per plan to defer full async DB)

from src.models.chat import ChatConversation, ChatMessage
from src.models.user import User
from src.models.exercise import Exercise
from src.api.schemas.chat import ChatMessageCreate, UserMessageInput # ChatMessageCreate not used here, but fine
from src.utils.ollama_client import generate_with_ollama
from fastapi import Request, HTTPException
import structlog

from src.core.config import get_settings # Ensure this is imported once at the top

settings = get_settings() # Initialize settings once at the top
logger = structlog.get_logger(__name__) # Initialize logger once at the top

async def get_or_create_conversation(db: Session, user_id: int, exercise_id: int) -> ChatConversation:
    """
    Retrieves an existing chat conversation or creates a new one
    if it doesn't exist.
    """
    conversation = db.query(ChatConversation).filter_by(user_id=user_id, exercise_id=exercise_id).first()
    if not conversation:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        exercise = db.query(Exercise).get(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        conversation = ChatConversation(user_id=user_id, exercise_id=exercise_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation

async def add_message_to_conversation(
    db: Session, 
    conversation_id: int,
    sender_type: str, 
    message_text: str
) -> ChatMessage:
    """
    Adds a message to a given conversation.
    """
    chat_message = ChatMessage(
        conversation_id=conversation_id,
        sender_type=sender_type,
        message=message_text
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message

async def process_user_message(
    db: Session, 
    user_message_input: UserMessageInput,
    user_id: int,
    request: Request
) -> tuple[ChatMessage, ChatMessage, ChatConversation]:
    """
    Processes a user's message:
    1. Gets or creates a conversation.
    2. Saves the user's message.
    3. Gets a response from the AI.
    4. Saves the AI's message.
    5. Returns both messages and the conversation.
    """
    # 1. Get or create conversation
    if user_message_input.conversation_id:
        conversation = db.query(ChatConversation).get(user_message_input.conversation_id)
        if not conversation or conversation.user_id != user_id or conversation.exercise_id != user_message_input.exercise_id:
            raise HTTPException(status_code=403, detail="Invalid conversation ID or access denied.")
    else:
        conversation = await get_or_create_conversation(db, user_id, user_message_input.exercise_id)

    # 2. Save user's message
    user_chat_message = await add_message_to_conversation(
        db,
        conversation_id=conversation.id,
        sender_type="user",
        message_text=user_message_input.message
    )

    # 3. Get AI response
    exercise = db.query(Exercise).get(conversation.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found for this conversation.")

    # Construct messages for Ollama using windowing
    all_messages_in_conversation = db.query(ChatMessage)\
        .filter(ChatMessage.conversation_id == conversation.id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

    messages_for_ollama = []
    # Apply windowing: take the last N messages. N = settings.ollama_history_messages_window
    # The user's current message is already included in all_messages_in_conversation.
    # So, if window is 6, we take the latest 6, which includes the current user message.
    start_index = max(0, len(all_messages_in_conversation) - settings.ollama_history_messages_window)
    windowed_messages = all_messages_in_conversation[start_index:]

    for msg in windowed_messages:
        role = msg.sender_type
        if role == "ai": 
            role = "assistant"
        if role not in ["user", "assistant"]: 
            logger.warn(f"Message with unknown role '{role}' skipped for Ollama.", message_id=msg.id)
            continue
        messages_for_ollama.append({"role": role, "content": msg.message})
    
    prompt_context = (
        f"Contexto del Ejercicio (ID: {exercise.id}):\n"
        f"Enunciado: {exercise.statement}\n"
        f"Tipo: {exercise.type}\n"
        f"Dificultad: {exercise.difficulty}\n\n"
        f"El usuario está trabajando en este ejercicio y ha enviado el siguiente mensaje. "
        f"Por favor, responde como un tutor amigable y útil. Ayuda al usuario a entender "
        f"el problema o guíalo hacia la solución sin dar la respuesta directamente, "
        f"a menos que el usuario la pida explícitamente o esté claramente atascado."
        f"Si la pregunta no está relacionada con el ejercicio, intenta redirigir amablemente la conversación al ejercicio."
    )

    ollama_payload = {
        "model": "profesor", # Or your preferred model
        "messages": [
            {"role": "system", "content": prompt_context}
        ] + messages_for_ollama, # Add windowed messages to the system prompt
        "temperature": 0.7,
    }

    logger.info("Payload a enviar a Ollama", ollama_payload_to_send=ollama_payload)

    try:
        ai_response_data = await generate_with_ollama(ollama_payload, request)
        if not ai_response_data.get("choices") or not ai_response_data["choices"][0].get("message"):
            raise HTTPException(status_code=500, detail="Invalid AI response format.")
        ai_message_text = ai_response_data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("Error getting AI response", error=str(e), exc_info=True) # Added more logging
        raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")

    # 4. Save AI's message
    ai_chat_message = await add_message_to_conversation(
        db,
        conversation_id=conversation.id,
        sender_type="ai",
        message_text=ai_message_text.strip()
    )

    db.refresh(conversation) 

    return user_chat_message, ai_chat_message, conversation


async def get_conversation_history(db: Session, conversation_id: int, user_id: int) -> ChatConversation:
    """
    Retrieves the full history of a specific conversation for a user.
    """
    conversation = db.query(ChatConversation).filter_by(id=conversation_id, user_id=user_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied.")
    return conversation

async def get_user_conversations_for_exercise(db: Session, user_id: int, exercise_id: int) -> list[ChatConversation]:
    """
    Retrieves all conversations a user has had for a specific exercise.
    Typically, there should be only one, but this allows for flexibility.
    """
    conversations = db.query(ChatConversation)\
        .filter_by(user_id=user_id, exercise_id=exercise_id)\
        .order_by(ChatConversation.created_at.desc())\
        .all()
    return conversations
