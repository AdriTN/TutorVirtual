import React from "react";
import styles from "./AdminCard.module.css";

export const AdminCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <article className={styles.card}>
    <header className={styles.header}><h4>{title}</h4></header>
    <div className={styles.body}>{children}</div>
  </article>
);
