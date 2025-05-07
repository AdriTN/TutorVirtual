import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./MySubjects.module.css";
import { Course, fetchCourse, unenrollSubject } from "../../utils/enrollment";
import { Trash2 } from "lucide-react";

const MyCourseSubjectsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [q, setQ] = useState("");

  const load = () => {
    if (id) {
      fetchCourse(Number(id))
        .then(setCourse)
        .catch(console.error);
    }
  };

  useEffect(load, [id]);

  if (!course) return null;

  const mySubjects = course.subjects.filter((s) => s.enrolled);
  const filtered = mySubjects.filter((s) =>
    s.name.toLowerCase().includes(q.toLowerCase())
  );

  const handleDelete = async (subjectId: number) => {
    if (!confirm("¿Eliminar esta asignatura?")) return;
    await unenrollSubject(subjectId).catch(console.error);
    load();
  };

  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        <div className={styles.wrapper}>
          <h1 className={styles.heading}>Curso: {course.title}</h1>
        </div>

        <div className={styles.searchContainer}>
          <input
            className={styles.search}
            placeholder="Buscar asignatura…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>
            {mySubjects.length === 0
              ? "No estás matriculado en ninguna asignatura de este curso."
              : "No hay asignaturas que coincidan con tu búsqueda."}
          </p>
        ) : (
          <ul className={styles.grid}>
            {filtered.map((s) => (
              <li key={s.id} className={styles.card}>
                <button
                  className={styles.deleteBtn}
                  onClick={() => handleDelete(s.id)}
                  aria-label="Eliminar asignatura"
                >
                  <Trash2 size={16} />
                </button>
                <h3 className={styles.title}>{s.name}</h3>
                <p className={styles.desc}>
                  {s.description ?? "Sin descripción"}
                </p>
              </li>
            ))}
          </ul>
        )}
      </main>

        <button
          className={styles.backBtn}
          onClick={() => nav("/my-courses")}
          aria-label="Volver a cursos"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 1024 1024"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M874.7 495.5c0 11.3-9.17 20.47-20.47 20.47H249.4l188.1 188.08c7.99 7.99 7.99 20.95 0 28.94-4 3.99-9.24 5.99-14.47 5.99-5.24 0-10.48-1.99-14.48-5.99L185.4 509.45c-3.84-3.84-5.99-9.05-5.99-14.47s2.15-10.63 5.99-14.47l223.02-223.03c7.99-7.99 20.96-7.99 28.95 0 7.99 8 7.99 20.95 0 28.95L249.4 474.6h604.8c11.3 0 20.47 9.16 20.47 20.9z"/>
          </svg>
          <span>Back</span>
        </button>

      <Footer />
    </div>
  );
};

export default MyCourseSubjectsPage;
