import { api } from "../backend";
import { ChatConversation, UserMessageInput } from "@/types";

const CHAT_API_URL = "/api/chat";

/**
 * Sends a user's message to the chat backend.
 * @param messageInput - The message content, exercise ID, and optional conversation ID.
 * @returns The updated chat conversation, including the user's message and AI's response.
 */
export const sendMessage = async (messageInput: UserMessageInput): Promise<ChatConversation> => {
  const response = await api.post<ChatConversation>(`${CHAT_API_URL}/message`, messageInput);
  return response.data;
};

/**
 * Retrieves a specific chat conversation by its ID.
 * @param conversationId - The ID of the conversation to retrieve.
 * @returns The chat conversation with its history.
 */
export const getConversation = async (conversationId: number): Promise<ChatConversation> => {
  const response = await api.get<ChatConversation>(`${CHAT_API_URL}/conversation/${conversationId}`);
  return response.data;
};

/**
 * Retrieves all chat conversations for a given exercise for the current user.
 * @param exerciseId - The ID of the exercise.
 * @returns A list of chat conversations.
 */
export const getExerciseConversations = async (exerciseId: number): Promise<ChatConversation[]> => {
  const response = await api.get<ChatConversation[]>(`${CHAT_API_URL}/exercise/${exerciseId}`);
  return response.data;
};
