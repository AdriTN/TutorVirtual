import { Course } from "@types";
import { useNavigate } from "react-router-dom";
import styles from "./CourseCard.module.css";

interface Props{ course:Course }

export default function CourseCard({ course }:Props){
  const nav = useNavigate();
  const { id, title, description, subjects } = course;
  const fullyEnrolled =
    subjects.length && subjects.every(s => s.enrolled);

  return (
    <li className={styles.card}>
      <h3 className={styles.title}>{title}</h3>
      <p  className={styles.desc}>{description ?? "Sin descripción"}</p>

      {!!subjects.length && (
        <div className={styles.themesContainer}>
          {subjects.slice(0, 4).map(s =>
            <span key={s.id} className={styles.badge}>{s.name}</span>
          )}
          {subjects.length > 4 && <span className={styles.badge}>y más...</span>}
        </div>
      )}

      {fullyEnrolled
        ? <span className={styles.feedback}>Ya cursas todas</span>
        : <button className={styles.btn} onClick={() => nav(`/courses/${id}`)}>Seleccionar</button>}
    </li>
  );
}
