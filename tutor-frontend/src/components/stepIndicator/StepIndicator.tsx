import React from "react";
import styles from "./StepIndicator.module.css";

interface StepIndicatorProps {
  /** Paso activo (1-N). Todo lo anterior se considera completado */
  current: number;
  /** Texto que se muestra bajo cada paso */
  steps: string[];
}

const StepIndicator: React.FC<StepIndicatorProps> = ({ current, steps }) => (
  <ol className={styles.track}>
    {steps.map((label, idx) => {
      const n = idx + 1;
      const done = n < current;
      const active = n === current;
      return (
        <li
          key={label}
          className={`${styles.step} ${done ? styles.done : ""} ${
            active ? styles.active : ""
          }`}
        >
          <span className={styles.circle}>
            {done ? "✔" : n}
          </span>
          <span className={styles.label}>{label}</span>
        </li>
      );
    })}
  </ol>
);

export default StepIndicator;
