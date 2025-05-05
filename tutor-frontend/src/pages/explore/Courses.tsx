import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, fetchCourses } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

const CoursesPage: React.FC = () => {
  const nav = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => { fetchCourses().then(setCourses); }, []);

  const filtered = courses.filter((c) =>
    c.title.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        <div className={styles.wrapper}>
        <StepIndicator current={1} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]}
        />

          <input
            placeholder="Buscar curso…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />

          <ul className={styles.grid}>
            {filtered.map((c) => (
              <li key={c.id} className={styles.card}>
                <h3 className={styles.title}>{c.title}</h3>
                <p className={styles.desc}>{c.description ?? "Sin descripción"}</p>
                <button
                  className={`${styles.btn} ${styles.primary}`}
                  onClick={() => nav(`/courses/${c.id}`)}
                >
                  Seleccionar
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

export default CoursesPage;
