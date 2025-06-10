import React, { useEffect, useRef } from "react";
import styles from "./CrudModal.module.css";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

const CrudModal: React.FC<Props> = ({ open, title, onClose, children }) => {
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    boxRef.current?.querySelector<HTMLElement>("input,textarea,select,button")?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className={styles.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={styles.box} ref={boxRef}>
        <header className={styles.header}>
          <h3>{title}</h3>
          <button onClick={onClose} aria-label="Cerrar">×</button>
        </header>
        {children}
      </div>
    </div>
  );
};

export default CrudModal;
