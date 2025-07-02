// Basado en los esquemas Pydantic del backend (ChatConversationResponse, ChatMessageResponse)

export interface ChatMessage {
    id: number;
    conversation_id: number;
    sender_type: "user" | "ai";
    message: string;
    created_at: string; // ISO date string
  }
  
  export interface ChatConversation {
    id: number;
    user_id: number;
    exercise_id: number;
    created_at: string; // ISO date string
    messages: ChatMessage[];
  }
  
  // Para enviar un nuevo mensaje
  export interface UserMessageInput {
    message: string;
    exercise_id: number;
    conversation_id?: number | null;
  }
  