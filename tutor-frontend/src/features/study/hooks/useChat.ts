import { useState, useCallback, useEffect } from 'react';
import { ChatConversation, ChatMessage, UserMessageInput } from '@/types';
import { sendMessage as apiSendMessage, getExerciseConversations as apiGetExerciseConversations } from '@/services/api';

interface UseChatProps {
  exerciseId: number | null;
  currentUserId: number | null; // Asumiendo que tienes forma de obtener el ID del usuario actual
}

interface UseChatReturn {
  conversation: ChatConversation | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (messageText: string) => Promise<void>;
  loadInitialConversation: () => Promise<void>;
}

export const useChat = ({ exerciseId, currentUserId }: UseChatProps): UseChatReturn => {
  const [conversation, setConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadInitialConversation = useCallback(async () => {
    if (!exerciseId || !currentUserId) {
      setMessages([]);
      setConversation(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const conversations = await apiGetExerciseConversations(exerciseId);
      if (conversations && conversations.length > 0) {
        const activeConversation = conversations[0];
        setConversation(activeConversation);
        setMessages(activeConversation.messages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()));
      } else {
        setConversation(null);
        setMessages([]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load conversation history.');
      setConversation(null);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  }, [exerciseId, currentUserId]);

  useEffect(() => {
    loadInitialConversation();
  }, [loadInitialConversation]);


  const sendMessage = async (messageText: string) => {
    if (!exerciseId || !currentUserId) {
      setError("Cannot send message: exercise ID or user ID is missing.");
      return;
    }
    if (!messageText.trim()) return;

    setIsLoading(true);
    setError(null);

    const userMessageInput: UserMessageInput = {
      message: messageText,
      exercise_id: exerciseId,
      conversation_id: conversation?.id,
    };

    const optimisticUserMessage: ChatMessage = {
      id: Date.now(),
      conversation_id: conversation?.id || 0,
      sender_type: "user",
      message: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages(prevMessages => [...prevMessages, optimisticUserMessage]);

    try {
      const updatedConversation = await apiSendMessage(userMessageInput);
      setConversation(updatedConversation);
      const sortedMessages = updatedConversation.messages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      setMessages(sortedMessages);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to send message.');
      setMessages(prevMessages => prevMessages.filter(msg => msg.id !== optimisticUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  return {
    conversation,
    messages,
    isLoading,
    error,
    sendMessage,
    loadInitialConversation,
  };
};
