import styles from "./SelectField.module.css";

export interface Option {
  id: number;
  label: string;
}

interface Props {
  id:       string;
  label:    string;
  value:    string | number;
  options:  Option[];
  onChange: (v: string) => void;
}

const SelectField = ({ id, label, value, options, onChange }: Props) => (
  <label className={styles.wrapper}>
    <span className={styles.caption}>{label}</span>

    <select
      id={id}
      value={value ?? ""}
      className={styles.select}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">— seleccionar —</option>

      {options.map((o) => (
        <option key={o.id} value={String(o.id)}>
          {o.label}
        </option>
      ))}
    </select>
  </label>
);

export default SelectField;
