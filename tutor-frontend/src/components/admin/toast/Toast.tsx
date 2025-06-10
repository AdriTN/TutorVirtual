import React, { useEffect, useState } from "react";
import { CheckCircle, WarningCircle, Info } from "@phosphor-icons/react";
import styles from "./Toast.module.css";

type Variant = "success" | "error" | "info";

interface Props { message: string; variant?: Variant }

export const Toast: React.FC<Props> = ({ message, variant = "info" }) => {
  const [show, setShow] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => setShow(false), 3000);
    return () => clearTimeout(t);
  }, []);

  if (!show) return null;

  const Icon = variant === "success"
    ? CheckCircle
    : variant === "error"
    ? WarningCircle
    : Info;

  return (
    <div className={`${styles.toast} ${styles[variant]}`} role="status" aria-live="polite">
      <Icon size={20} weight="duotone" />
      <span>{message}</span>
    </div>
  );
};
