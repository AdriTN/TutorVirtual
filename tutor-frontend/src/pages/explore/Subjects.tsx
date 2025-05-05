import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, fetchCourse } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

const SubjectsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);

  useEffect(() => {
    fetchCourse(Number(id)).then(setCourse);
  }, [id]);

  if (!course) return null;

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        <div className={styles.wrapper}>
        <StepIndicator current={2} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]}
        />

          <h2>{course.title}</h2>

          <ul className={styles.grid}>
            {course.subjects.map((s) => (
              <li key={s.id} className={styles.card}>
                <h3 className={styles.title}>{s.name}</h3>
                <button
                  className={`${styles.btn} ${styles.primary}`}
                  onClick={() =>
                    nav(`/courses/${course.id}/confirm?subject=${s.id}`)
                  }
                >
                  Elegir
                </button>
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
