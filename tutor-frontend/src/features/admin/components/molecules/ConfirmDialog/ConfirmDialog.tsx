import styles from "./ConfirmDialog.module.css";
interface Props{
  open:boolean;
  message:string;
  onConfirm:()=>void;
  onCancel:()=>void;
}
export default function ConfirmDialog({ open, message, onConfirm, onCancel }:Props){
  if(!open) return null;
  return(
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.box}>
        <p>{message}</p>
        <div className={styles.actions}>
          <button onClick={onCancel}>Cancelar</button>
          <button className={styles.danger} onClick={onConfirm}>Eliminar</button>
        </div>
      </div>
    </div>
  );
}