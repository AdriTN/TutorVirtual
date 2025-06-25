import styles from "./HeaderBar.module.css";
import { Course, Subject } from "@/types";

interface Props {
  course: Course;
  subject: Subject;
  difficulty: string;
  onDifficultyChange: (d: string) => void;
}

export default function HeaderBar({ course, subject, difficulty, onDifficultyChange }: Props) {
  return (
    <header className={styles.header}>
      <div className={styles.courseInfo}>
        {course.title} ― {subject.name}
      </div>
      <label className={styles.selectWrapper}>
        <span>Dificultad:</span>
        <select
          value={difficulty}
          onChange={e => onDifficultyChange(e.target.value)}
          className={styles.select}
        >
          <option value="fácil">Fácil</option>
          <option value="intermedia">Intermedia</option>
          <option value="difícil">Difícil</option>
        </select>
      </label>
    </header>
  );
}
