import clsx              from "clsx";
import styles            from "./Spinner.module.css";

export interface SpinnerProps {
  size?: number;
  className?: string;
  "aria-label"?: string;
}

const Spinner = ({
  size = 24,
  className,
  "aria-label": ariaLabel = "Cargando…",
}: SpinnerProps) => (
  <svg
    role="img"
    aria-label={ariaLabel}
    width={size}
    height={size}
    viewBox="0 0 24 24"
    className={clsx(styles.spinner, className)}
  >
    <circle
      cx="12" cy="12" r="10"
      className={styles.track}
    />
    <path
      d="M22 12a10 10 0 0 1-10 10"
      className={styles.arc}
    />
  </svg>
);

export default Spinner;
