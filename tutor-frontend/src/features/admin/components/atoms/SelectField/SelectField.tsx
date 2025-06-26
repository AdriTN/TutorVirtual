import styles from "./SelectField.module.css";

export interface Option {
  id: number;
  label: string;
}

interface Props {
  id:        string;
  label:     string;
  value:     string | string[];
  options:   Option[];
  multiple?: boolean;
  onChange:  (v: string | string[]) => void;
}

export default function SelectField({
  id,
  label,
  value,
  options,
  multiple = false,
  onChange,
}: Props) {
  return (
    <label className={styles.wrapper}>
      <span className={styles.caption}>{label}</span>

      <select
        id={id}
        multiple={multiple}
        className={styles.select}
        /* string  ✦  string[] */
        value={value}
        onChange={(e) =>
          onChange(
            multiple
              ? Array.from(e.target.selectedOptions).map((o) => o.value)
              : e.target.value,
          )
        }
      >
        {/* ⚠️  el placeholder SOLO cuando NO es multiple */}
        {!multiple && <option value="">— seleccionar —</option>}

        {options.map((o) => (
          <option key={o.id} value={String(o.id)}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
