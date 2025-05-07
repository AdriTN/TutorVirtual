import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar   from "../utils/NavBar/NavBar";
import Footer   from "../utils/Footer/Footer";
import styles   from "./MyCourses.module.css";
import { Course, fetchMyCourses, unenrollCourse } from "../../utils/enrollment";
import { Trash2 } from "lucide-react";

const MyCoursesPage: React.FC = () => {
  const nav = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [q, setQ] = useState("");

  const load = () => fetchMyCourses().then(setCourses).catch(console.error);
  useEffect(() => {
    load();
  }, []);

  const filtered = courses.filter((c) =>
    c.title.toLowerCase().includes(q.toLowerCase())
  );

  const handleDelete = async (id: number) => {
    if (!confirm("¿Eliminar este curso y sus asignaturas?")) return;
    await unenrollCourse(id).catch(console.error);
    load();
  };

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>

        <div className={styles.searchContainer}>
          <input
            className={styles.search}
            placeholder="Buscar curso…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>Aún no tienes cursos con asignaturas matriculadas.</p>
        ) : (
          <ul className={styles.grid}>
            {filtered.map((c) => {
              const mySubjects = c.subjects.filter((s) => s.enrolled);
              return (
                <li key={c.id} className={styles.card}>
                  {/* botón papelera */}
                  <button
                    className={styles.deleteBtn}
                    onClick={() => handleDelete(c.id)}
                    aria-label="Eliminar curso"
                  >
                    <Trash2 size={18} />
                  </button>

                  <h3 className={styles.title}>{c.title}</h3>
                  <p className={styles.desc}>{c.description ?? "Sin descripción"}</p>

                  <div className={styles.subjects}>
                    {mySubjects.map((s) => (
                      <span key={s.id} className={styles.badge}>{s.name}</span>
                    ))}
                  </div>

                  {/* botón para ver asignaturas */}
                  <button
                    className={styles.viewBtn}
                    onClick={() => nav(`/my-subjects/${c.id}`)}
                  >
                    Ver asignaturas
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        {/* botón explorar cursos */}
        <button className={styles.cta} onClick={() => nav('/courses')}>
            <span className={styles.hoverunderlineanimation}> Explorar Cursos </span>
        </button>
      </main>
      <Footer />
    </div>
  );
};

export default MyCoursesPage;
