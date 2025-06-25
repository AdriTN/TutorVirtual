import { Course }                  from "@types";
import { Trash2 }                  from "lucide-react";
import styles                      from "./CourseCard.module.css";

interface Props {
  course   : Course;
  onDelete : (id: number) => void;
  onView   : (id: number) => void;
}

const CourseCard: React.FC<Props> = ({ course, onDelete, onView }) => {
  const subjects = course.subjects.filter(s => s.enrolled);

  return (
    <li className={styles.card}>
      <button
        className={styles.deleteBtn}
        onClick={() => onDelete(course.id)}
        aria-label="Eliminar curso"
      >
        <Trash2 size={18}/>
      </button>

      <h3 className={styles.title}>{course.title}</h3>
      <p  className={styles.desc}>{course.description ?? "Sin descripción"}</p>

      <div className={styles.subjects}>
        {subjects.map(s => (
          <span key={s.id} className={styles.badge}>{s.name}</span>
        ))}
      </div>

      <button className={styles.viewBtn} onClick={() => onView(course.id)}>
        Ver asignaturas
      </button>
    </li>
  );
};

export default CourseCard;
