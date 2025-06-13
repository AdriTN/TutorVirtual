// src/pages/mycourses/MyCourseSubjectsPage.tsx
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar   from "../utils/NavBar/NavBar";
import Footer   from "../utils/Footer/Footer";
import styles   from "./MySubjects.module.css";
import { Course, fetchCourse, unenrollSubject } from "../../utils/enrollment";
import { Trash2 } from "lucide-react";

const MyCourseSubjectsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // courseId
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
                {/* botón papelera */}
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

                <div className={styles.themes}>
                  {s.themes.map((t) => (
                    <span key={t.id} className={styles.badge}>
                      {t.title}
                    </span>
                  ))}
                </div>
                <div className={styles.level}>
                  {/* botón “Ver temas” */}
                  <button
                    className={styles.viewBtn}
                    onClick={() => nav(`/my-subjects/${id}/${s.id}/themes`)}
                  >
                    Ver temas
                  </button>

                  {/* botón “Estudiar” */}
                  <button
                    className={styles.studyBtn}
                    onClick={() => nav(`/study/${id}/${s.id}`)}
                  >
                    Estudiar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>

      {/* Botón volver al listado de cursos */}
      <button
        className={styles.backBtn}
        onClick={() => nav("/my-courses")}
        aria-label="Volver a cursos"
      >
        ← Volver
      </button>

      <Footer />
    </div>
  );
};

export default MyCourseSubjectsPage;
