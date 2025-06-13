import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, fetchCourses } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

interface Subject {
  id: number;
  name: string;
  enrolled: boolean;
}

const CoursesPage: React.FC = () => {
  const nav = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    fetchCourses().then(setCourses);
  }, []);

  const filtered = courses.filter((c) =>
    c.title.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        {/* encabezado: paso + buscador */}
        <div className={styles.wrapper}>
          <StepIndicator current={1} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]} />

          <div className={styles.searchContainer}>
            <input
              className={styles.search}
              placeholder="Buscar curso…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
        </div>

        {/* grid de cursos */}
        <ul className={styles.grid}>
          {filtered.map((c) => {
            const subjects: Subject[] = (c as any).subjects ?? [];
            const fullyEnrolled =
              subjects.length > 0 && subjects.every((s) => s.enrolled);
            const preview = subjects.slice(0, 3);

            return (
              <li key={c.id} className={styles.card}>
                <h3 className={styles.title}>{c.title}</h3>
                <p className={styles.desc}>{c.description ?? "Sin descripción"}</p>

                {/* mini-lista de asignaturas */}
                {subjects.length > 0 && (
                  <div className={styles.subjects}>
                    {preview.map((s) => (
                      <span key={s.id} className={styles.badge}>
                        {s.name}
                      </span>
                    ))}
                    {subjects.length > 3 && <span className={styles.badge}>…</span>}
                  </div>
                )}

                {/* CTA / feedback */}
                {fullyEnrolled ? (
                  <span className={styles.feedback}>
                    Ya cursas todas las asignaturas
                  </span>
                ) : (
                  <button
                    className={`${styles.btn} ${styles.primary}`}
                    onClick={() => nav(`/courses/${c.id}`)}
                  >
                    Seleccionar
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      </main>
      <Footer />
    </div>
  );
};

export default CoursesPage;
