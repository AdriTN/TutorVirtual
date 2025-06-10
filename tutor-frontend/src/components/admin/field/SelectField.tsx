import React from "react";
import styles from "./SelectField.module.css";

interface Opt { id: number; label: string }

export const SelectField: React.FC<{
  id: string; label: string;
  value: string; onChange: (v: string) => void;
  options: Opt[];
}> = ({ id, label, value, onChange, options }) => (
  <div className={styles.wrapper}>
    <label htmlFor={id}>{label}:</label>
    <select
      id={id}
      className={styles.select}
      value={value}
      onChange={e => onChange(e.target.value)}
    >
      <option value="">— seleccionar —</option>
      {options.map(o => (
        <option key={o.id} value={o.id}>{o.label}</option>
      ))}
    </select>
  </div>
);
