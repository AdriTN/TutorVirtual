import React from "react";
import styles from "../pages/Themes.module.css";
import { Theme } from "@types";

const ThemeCard: React.FC<{ theme: Theme }> = ({ theme }) => (
  <li className={styles.card}>
    <h3 className={styles.title}>{theme.title}</h3>
    <p className={styles.desc}>{theme.description ?? "Sin descripción"}</p>
  </li>
);

export default ThemeCard;
