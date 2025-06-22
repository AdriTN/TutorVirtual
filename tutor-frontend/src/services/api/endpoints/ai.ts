import { api } from "../backend";
import { AIRequest, AIExerciseOut, AnswerOut } from "@/types";

/* Preguntar a la IA ------------------------------------------------------ */
export const askAI = (body: AIRequest) =>
  api.post<AIExerciseOut>("/api/ai/request", body).then(r => r.data);

/* Enviar respuesta del usuario ------------------------------------------ */
export const sendAnswer = (ejercicio_id: number, answer: string, tiempo_seg?: number) =>
  api.post<AnswerOut>("/api/answer", { ejercicio_id, answer, tiempo_seg }).then(r => r.data);
