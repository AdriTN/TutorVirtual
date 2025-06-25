import styles from "./ExerciseCard.module.css";

interface Props {
  enunciado: string;
  explanation?: string;
  checked: boolean;
  isCorrect: boolean | null;
}

export default function ExerciseCard({ 
  enunciado, explanation, checked, isCorrect 
}: Props) {
  return (
    <section className={styles.card}>
      <p className={styles.question}>{enunciado}</p>
      {checked && (
        <div className={isCorrect ? styles.correct : styles.incorrect}>
          {isCorrect ? "¡Correcto!" : "Incorrecto"}
        </div>
      )}
      {checked && explanation && (
        <div className={styles.explanation}>
          <strong>Respuesta correcta:</strong> {explanation}
        </div>
      )}
    </section>
  );
}
