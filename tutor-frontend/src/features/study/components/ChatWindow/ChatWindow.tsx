import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '@/types';
import styles from './ChatWindow.module.css';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (messageText: string) => Promise<void>;
  isLoading: boolean;
  chatError: string | null;
  currentUserId: number | null; // Para alinear mensajes del usuario actual
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  isLoading,
  chatError,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    try {
      await onSendMessage(inputText);
      setInputText(''); // Clear input only on successful send
    } catch (error) {
      // Error is handled by the hook, just log or display if needed here
      console.error("Send message failed from component:", error)
    }
  };

  return (
    <div className={styles.chatWindow}>
      <h3 className={styles.chatTitle}>Chat de Ayuda</h3>
      <div className={styles.messagesContainer}>
        {messages.length === 0 && !isLoading && !chatError && (
          <p className={styles.emptyChatMessage}>
            ¿Necesitas ayuda con el ejercicio? Escribe tu pregunta abajo.
          </p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${
              msg.sender_type === 'user' ? styles.userMessage : styles.aiMessage
            }`}
          >
            <p className={styles.messageText}>{msg.message}</p>
            <span className={styles.timestamp}>
              {new Date(msg.created_at).toLocaleTimeString()}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      {chatError && <p className={styles.errorMessage}>{chatError}</p>}
      <form onSubmit={handleSend} className={styles.inputForm}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Escribe tu mensaje..."
          className={styles.inputField}
          disabled={isLoading}
        />
        <button type="submit" className={styles.sendButton} disabled={isLoading}>
          {isLoading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
