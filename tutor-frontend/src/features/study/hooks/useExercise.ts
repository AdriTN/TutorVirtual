import { useState, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AIRequest, AIExerciseOut } from "@/types";
import { askAI, sendAnswer } from "@/services/api";

export function useExercise() {
  const qc = useQueryClient();
  const [exercise, setExercise] = useState<AIExerciseOut|null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string|null>(null);
  const [checked, setChecked]     = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean|null>(null);
  const startTs = useRef<number| null>(null);

  const generate = useCallback(async (body: AIRequest) => {
    setExercise(null);
    setChecked(false);
    setIsCorrect(null);
    setLoading(true);
    setError(null);
    try {
      const ex = await askAI(body);
      setExercise(ex);
      startTs.current = performance.now();
    } catch (e: any) {
      setError(e.message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  const check = useCallback(async (answer: string) => {
    if (!exercise) return;
    const t = startTs.current
      ? Math.round((performance.now() - startTs.current) / 1000)
      : undefined;
    try {
      const res = await sendAnswer(exercise.id, answer, t);
      setChecked(true);
      setIsCorrect(res.correcto);
      qc.invalidateQueries({ queryKey: ["stats","overview"] });
    } catch (e:any) {
      setError(e.message ?? "Error al enviar respuesta");
    }
  }, [exercise, qc]);

  return {
    exercise, loading, error, checked, isCorrect,
    generate, check,
  };
}
