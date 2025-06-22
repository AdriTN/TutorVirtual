import clsx   from "clsx";
import styles from "./StepIndicator.module.css";

export interface StepIndicatorProps {
  current: number;
  steps: string[];
}

const StepIndicator = ({ current, steps }: StepIndicatorProps) => (
  <ol className={styles.track}>
    {steps.map((label, i) => {
      const n      = i + 1;
      const done   = n < current;
      const active = n === current;

      return (
        <li
          key={label}
          className={clsx(
            styles.step,
            done   && styles.done,
            active && styles.active,
          )}
        >
          <span className={styles.circle} aria-hidden>
            {done ? "✔" : n}
          </span>

          <span
            className={styles.label}
            aria-current={active ? "step" : undefined}
          >
            {label}
          </span>
        </li>
      );
    })}
  </ol>
);

export default StepIndicator;
