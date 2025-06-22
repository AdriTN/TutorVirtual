import { useState, useEffect } from "react";
import { CheckCircle, WarningCircle, Info } from "@phosphor-icons/react";
import styles from "./Toast.module.css";

export type ToastVariant = "success" | "error" | "info";

interface Props {
  message:  string;
  variant?: ToastVariant;
  duration?: number;          // ms
}

const Toast = ({ message, variant = "info", duration = 3000 }: Props) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setVisible(false), duration);
    return () => clearTimeout(t);
  }, [duration]);

  if (!visible) return null;

  const Icon = variant === "success"
    ? CheckCircle
    : variant === "error"
    ? WarningCircle
    : Info;

  return (
    <div
      className={`${styles.toast} ${styles[variant]}`}
      role="alert"
      aria-live="polite"
    >
      <Icon size={20} weight="duotone" aria-hidden />
      <span>{message}</span>
    </div>
  );
};

export default Toast;
