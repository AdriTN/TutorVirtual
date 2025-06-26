import styles from "./EntityTable.module.css";

interface Col { key:string; label:string }
interface Props<T extends { id:number }> {
  items:   T[];
  cols:    Col[];
  onEdit:  (item:T)=>void;
  onDelete:(item:T)=>void;
}
export default function EntityTable<T extends { id:number }>({
  items, cols, onEdit, onDelete,
}: Props<T>) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          {cols.map(c => <th key={c.key}>{c.label}</th>)}
          <th style={{width:"90px"}}></th>
        </tr>
      </thead>
      <tbody>
        {items.map(row => (
          <tr key={row.id}>
            {cols.map(c => <td key={c.key}>{(row as any)[c.key]}</td>)}
            <td className={styles.actions}>
              <button onClick={()=>onEdit(row)}>✏️</button>
              <button onClick={()=>onDelete(row)}>🗑️</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
