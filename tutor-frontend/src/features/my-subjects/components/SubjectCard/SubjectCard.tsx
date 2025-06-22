import { Subject }     from "@types";
import { Trash2 }      from "lucide-react";
import styles          from "../../pages/MySubjects.module.css";

interface Props {
  subject   : Subject;
  onDelete  : (id: number) => void;
  onThemes  : (id: number) => void;
  onStudy   : (id: number) => void;
}

const SubjectCard: React.FC<Props> = ({
  subject, onDelete, onThemes, onStudy,
}) => (
  <li className={styles.card}>
    <button
      className={styles.deleteBtn}
      onClick={() => onDelete(subject.id)}
      aria-label="Eliminar asignatura"
    >
      <Trash2 size={16}/>
    </button>

    <h3 className={styles.title}>{subject.name}</h3>
    <p  className={styles.desc}>{subject.description ?? "Sin descripción"}</p>

    <div className={styles.themes}>
      {subject.themes.map(t => (
        <span key={t.id} className={styles.badge}>{t.title}</span>
      ))}
    </div>

    <div className={styles.level}>
      <button className={styles.viewBtn}  onClick={() => onThemes(subject.id)}>
        Ver temas
      </button>
      <button className={styles.studyBtn} onClick={() => onStudy(subject.id)}>
        Estudiar
      </button>
    </div>
  </li>
);

export default SubjectCard;
