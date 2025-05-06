import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, fetchCourse } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

const SubjectsPage: React.FC = () => {
  /* ---------------- hooks ---------------- */
  const { id } = useParams<{ id: string }>();   // courseId
  const nav = useNavigate();

  const [course, setCourse] = useState<Course | null>(null);

  /* ---------------- helpers ---------------- */
  const loadCourse = useCallback(() => {
    if (!id) return;
    fetchCourse(Number(id))
      .then(setCourse)
      .catch(console.error);
  }, [id]);

  useEffect(loadCourse, [loadCourse]);

  /* ---------------- UI ---------------- */
  if (!course) return null; // o un spinner

  const handleSelect = (subjectId: number) => {
    nav(`/courses/${course.id}/confirm?subject=${subjectId}`);
  };

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        <div className={styles.wrapper}>
          <StepIndicator current={2} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]} />

          <h2>{course.title}</h2>

          <ul className={styles.grid}>
            {course.subjects.map((s) => (
              <li key={s.id} className={styles.card}>
                <h3 className={styles.title}>{s.name}</h3>
                <p className={styles.desc}>{s.description ?? "Sin descripción"}</p>

                {s.enrolled ? (
                  <span className={styles.feedback}>Matriculada</span>
                ) : (
                  <button
                    className={`${styles.btn} ${styles.primary}`}
                    onClick={() => handleSelect(s.id)}
                  >
                    Elegir
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default SubjectsPage;
