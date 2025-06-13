import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./themes.module.css";
import {
  Course,
  Theme,
  fetchCourse,
  fetchThemes,
} from "../../utils/enrollment";

const ThemesPage: React.FC = () => {
  const { courseId, subjectId } = useParams<{
    courseId: string;
    subjectId: string;
  }>();
  const nav = useNavigate();

  const [course, setCourse] = useState<Course | null>(null);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [q, setQ] = useState("");

  // Carga curso (para título/asignatura) y temas
  const load = () => {
    if (!courseId || !subjectId) return;
    fetchCourse(Number(courseId))
      .then(setCourse);
    fetchThemes(Number(subjectId))
      .then(setThemes);
  };

  useEffect(load, [courseId, subjectId]);

  if (!course) return null;

  // Nombre de la asignatura
  const subj = course.subjects.find((s) => s.id === Number(subjectId));
  const subjectName = subj?.name ?? "Asignatura";

  // Filtrado
  const filtered = themes.filter((t) =>
    t.title.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        {/* Encabezado */}
        <div className={styles.wrapper}>
          <h1 className={styles.heading}>
            {course.title} – {subjectName}
          </h1>
        </div>

        {/* Buscador */}
        <div className={styles.searchContainer}>
          <input
            className={styles.search}
            placeholder="Buscar tema…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        {/* Estado vacío o grid */}
        {filtered.length === 0 ? (
          <p className={styles.empty}>
            {themes.length === 0
              ? "Esta asignatura aún no tiene temas."
              : "No hay temas que coincidan con tu búsqueda."}
          </p>
        ) : (
          <ul className={styles.grid}>
            {filtered.map((t) => (
              <li key={t.id} className={styles.card}>
                <h3 className={styles.title}>{t.title}</h3>
                <p className={styles.desc}>
                  {t.description ?? "Sin descripción"}
                </p>
              </li>
            ))}
          </ul>
        )}
      </main>

      {/* Botón volver */}
      <button
        className={styles.backBtn}
        onClick={() => nav(-1)}
        aria-label="Volver atrás"
      >
        ← Volver
      </button>

      <Footer />
    </div>
  );
};

export default ThemesPage;
