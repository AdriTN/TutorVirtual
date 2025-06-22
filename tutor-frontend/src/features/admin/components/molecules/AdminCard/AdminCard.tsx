import styles from "./AdminCard.module.css";

export interface AdminCardProps {
  title:    string;
  children: React.ReactNode;
}

const AdminCard = ({ title, children }: AdminCardProps) => (
  <article className={styles.card}>
    <h4 className={styles.header}>{title}</h4>
    <div className={styles.body}>{children}</div>
  </article>
);

export default AdminCard;
