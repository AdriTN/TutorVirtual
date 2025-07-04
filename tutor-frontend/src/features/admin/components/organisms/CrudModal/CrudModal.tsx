import { memo, useEffect, useRef } from "react";
import styles from "./CrudModal.module.css";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

function CrudModal({ open, title, onClose, children }: Props) {
  const boxRef = useRef<HTMLDivElement>(null);
  const focused = useRef(false);          // sólo una vez por apertura

  useEffect(() => {
    if (!open) { focused.current = false; return; }

    /* foco al primer elemento interactivo */
    if (!focused.current) {
      focused.current = true;
      boxRef.current?.querySelector<HTMLElement>(
        "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])",
      )?.focus();
    }

    /* ESC para cerrar & bloquear scroll fondo */
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    const { overflow } = document.body.style;

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);

    return () => {
      document.body.style.overflow = overflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className={styles.overlay}
      role="dialog"
      aria-modal="true"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className={styles.box} ref={boxRef}>
        <header className={styles.header}>
          <h3>{title}</h3>
          <button
            className={styles.close}
            aria-label="Cerrar"
            onClick={onClose}
          >
            ×
          </button>
        </header>

        {children}
      </div>
    </div>
  );
}

export default memo(CrudModal);
