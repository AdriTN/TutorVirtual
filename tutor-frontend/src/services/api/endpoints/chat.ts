import { api } from "../backend";
import { ChatConversation, UserMessageInput } from "@/types";

const CHAT_API_URL = "/api/chat";


export const sendMessage = async (messageInput: UserMessageInput): Promise<ChatConversation> => {
  const response = await api.post<ChatConversation>(`${CHAT_API_URL}/message`, messageInput);
  return response.data;
};

export const getConversation = async (conversationId: number): Promise<ChatConversation> => {
  const response = await api.get<ChatConversation>(`${CHAT_API_URL}/conversation/${conversationId}`);
  return response.data;
};

export const getExerciseConversations = async (exerciseId: number): Promise<ChatConversation[]> => {
  const response = await api.get<ChatConversation[]>(`${CHAT_API_URL}/exercise/${exerciseId}`);
  return response.data;
};
