from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.models.chat import ChatConversation, ChatMessage
from src.models.user import User
from src.models.exercise import Exercise
from src.api.schemas.chat import ChatMessageCreate, UserMessageInput
from src.utils.ollama_client import generate_with_ollama
from fastapi import Request, HTTPException # Added HTTPException
import structlog # Añadir import

logger = structlog.get_logger(__name__) # Añadir logger

async def get_or_create_conversation(db: Session, user_id: int, exercise_id: int) -> ChatConversation:
    """
    Retrieves an existing chat conversation or creates a new one
    if it doesn't exist.
    """
    # Corrected to use synchronous session for initial query if not converting fully to async yet
    # For a fully async app, db would be AsyncSession and all db calls would be awaited
    # Assuming db is Session for now as per existing project structure in other files
    
    conversation = db.query(ChatConversation).filter_by(user_id=user_id, exercise_id=exercise_id).first()
    if not conversation:
        # Ensure user and exercise exist before creating conversation
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
    db: Session, # Assuming Session for now, change to AsyncSession if db operations become async
    conversation_id: int,
    sender_type: str, # "user" or "ai"
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
    db: Session, # Assuming Session for now
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

    # 3. Get AI response (simplified example)
    # In a real scenario, you might want to include conversation history or exercise context
    # for a more relevant AI response.
    exercise = db.query(Exercise).get(conversation.exercise_id)
    if not exercise:
        # This should ideally not happen if conversation was created correctly
        raise HTTPException(status_code=404, detail="Exercise not found for this conversation.")

    # Construct a more detailed prompt for the AI
    # You might want to include previous messages for context
    previous_messages = db.query(ChatMessage)\
        .filter(ChatMessage.conversation_id == conversation.id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

    messages_for_ollama = [{"role": msg.sender_type, "content": msg.message} for msg in previous_messages]
    # Obtener TODOS los mensajes de la conversación, INCLUYENDO el que acabamos de añadir.
    all_messages_in_conversation = db.query(ChatMessage)\
        .filter(ChatMessage.conversation_id == conversation.id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

    messages_for_ollama = []
    for msg in all_messages_in_conversation:
        role = msg.sender_type
        if role == "ai": # Ollama espera "assistant" para los mensajes de la IA
            role = "assistant"
        if role not in ["user", "assistant", "system"]: 
            logger.warn(f"Mensaje con rol desconocido '{role}' omitido para Ollama.", message_id=msg.id)
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
        ] + messages_for_ollama,
        "temperature": 0.7,
         # "stream": False # Assuming non-streaming for now
    }

    logger.info("Payload a enviar a Ollama", ollama_payload_to_send=ollama_payload) # Log del payload

    try:
        ai_response_data = generate_with_ollama(ollama_payload, request)
        # Ensure 'choices' and 'message' are present and structured as expected
        if not ai_response_data.get("choices") or not ai_response_data["choices"][0].get("message"):
            raise HTTPException(status_code=500, detail="Invalid AI response format.")
        ai_message_text = ai_response_data["choices"][0]["message"]["content"]
    except Exception as e: # Catch generic exception from generate_with_ollama
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")


    # 4. Save AI's message
    ai_chat_message = await add_message_to_conversation(
        db,
        conversation_id=conversation.id,
        sender_type="ai",
        message_text=ai_message_text.strip()
    )

    db.refresh(conversation) # Refresh to get updated messages list if using relationships

    return user_chat_message, ai_chat_message, conversation


async def get_conversation_history(db: Session, conversation_id: int, user_id: int) -> ChatConversation:
    """
    Retrieves the full history of a specific conversation for a user.
    """
    conversation = db.query(ChatConversation).filter_by(id=conversation_id, user_id=user_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied.")
    # Messages are loaded via relationship, ensure they are sorted if needed by default order_by in model or here
    # If lazy loading, accessing conversation.messages will trigger the query.
    # For explicit loading with sorting:
    # conversation.messages = db.query(ChatMessage).filter_by(conversation_id=conversation_id).order_by(ChatMessage.created_at.asc()).all()
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
