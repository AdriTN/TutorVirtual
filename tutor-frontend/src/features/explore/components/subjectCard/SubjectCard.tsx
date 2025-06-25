import { Subject } from "@types";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./SubjectCard.module.css";

interface Props{ subject:Subject }

export default function SubjectCard({ subject }:Props){
  const { id: courseId } = useParams();
  const nav = useNavigate();

  return (
    <li className={styles.card}>
      <h3 className={styles.title}>{subject.name}</h3>
      <p  className={styles.desc}>{subject.description ?? "Sin descripción"}</p>

      {subject.enrolled
        ? <span className={styles.feedback}>Matriculada</span>
        : (
          <button
            className={styles.btn}
            onClick={() => nav(`/courses/${courseId}/confirm?subject=${subject.id}`)}
          >
            Elegir
          </button>
        )}
    </li>
  );
}
