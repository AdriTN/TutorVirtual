export interface AIRequest {
    model: string;
    response_format: { type: "json_object" };
    messages: { role: "system" | "user" | "assistant"; content: string }[];
  }
  
  export interface AIExerciseOut {
    id: number;
    tema: string;
    enunciado: string;
    dificultad: string;
    tipo: string;
    explicacion: string;
  }
  
  export interface AnswerOut {
    correcto: boolean;
  }
  