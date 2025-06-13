import React from "react";
import styles from "./TabButton.module.css";

interface Props {
  active: boolean;
  onClick: () => void;
  id: string;
  controls: string;
  children: React.ReactNode;
}

export const TabButton: React.FC<Props> = ({
  active, onClick, id, controls, children,
}) => (
  <div role="tablist">
    <button
      id={id}
      role="tab"
      aria-controls={controls}
      aria-selected={active}
      className={`${styles.btn} ${active ? styles.active : ""}`}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  </div>
);
