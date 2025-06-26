import clsx from "clsx";
import styles from "./MultiCheckList.module.css";

export interface Option { id: number; label: string }

interface Props {
  title?:     string;
  options:    Option[];
  value:      number[];
  onChange:   (ids: number[]) => void;
  className?: string;
  maxHeight?: number | string;
}

export default function MultiCheckList({
  title,
  options,
  value,
  onChange,
  className,
  maxHeight = 240,
}: Props) {
  const toggle = (id: number) =>
    value.includes(id)
      ? onChange(value.filter(v => v !== id))
      : onChange([...value, id]);

  return (
    <section className={clsx(styles.box, className)} style={{ maxHeight }}>
      {title && <h5 className={styles.header}>{title}</h5>}

      <ul className={styles.list}>
        {options.length
          ? options.map(o => (
              <li key={o.id}>
                <label className={styles.item}>
                  <input
                    type="checkbox"
                    checked={value.includes(o.id)}
                    onChange={() => toggle(o.id)}
                  />
                  <span className={styles.checkmark} />
                  <span className={styles.label}>{o.label}</span>
                </label>
              </li>
            ))
          : <li className={styles.empty}>— sin elementos —</li>}
      </ul>
    </section>
  );
}
