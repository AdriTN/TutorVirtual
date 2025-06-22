import styles from "../pages/Study.module.css";

interface Props {
  userAnswer: string;
  onAnswerChange: (s: string) => void;
  onCheck: () => void;
  onNext: () => void;
  loading: boolean;
  checked: boolean;
}

export default function Controls({
  userAnswer, onAnswerChange, onCheck, onNext, loading, checked
}: Props) {
  return (
    <div className={styles.controls}>
      <input
        className={styles.input}
        placeholder="Tu respuesta…"
        value={userAnswer}
        onChange={e => onAnswerChange(e.target.value)}
        disabled={checked}
      />
      { !checked
        ? <button
            className={styles.btn}
            onClick={onCheck}
            disabled={loading || !userAnswer.trim()}
          >
            Comprobar
          </button>
        : <button
            className={styles.btn}
            onClick={onNext}
            disabled={loading}
          >
            Siguiente →
          </button>
      }
    </div>
  );
}
