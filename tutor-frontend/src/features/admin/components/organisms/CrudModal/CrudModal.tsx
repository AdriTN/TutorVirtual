// src/features/admin/components/CrudModal/CrudModal.tsx
import { memo, useEffect, useRef } from "react";
import styles from "./CrudModal.module.css";

interface CrudModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

function CrudModal({ open, title, onClose, children }: CrudModalProps) {
  const boxRef = useRef<HTMLDivElement>(null);

  /* Foco al primer campo SOLO cuando el modal se abre */
  useEffect(() => {
    if (!open) return;

    const firstFocusable = boxRef.current?.querySelector<HTMLElement>(
      "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])"
    );
    firstFocusable?.focus();

    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    const { overflow } = document.body.style;      // guarda estado previo

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);

    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
    };
  }, [open, onClose]);

  /* Si el modal está cerrado, no renderizamos nada */
  if (!open) return null;

  return (
    <div
      data-testid="modal"            /* ← opcional para tests / debug */
      className={styles.overlay}
      role="dialog"
      aria-modal="true"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className={styles.box} ref={boxRef}>
        <header className={styles.header}>
          <h3>{title}</h3>
          <button
            type="button"
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
