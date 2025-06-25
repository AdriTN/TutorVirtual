import { useState }                   from "react";
import { useNavigate, useParams }     from "react-router-dom";
import NavBar                         from "@components/organisms/NavBar/NavBar";
import Footer                         from "@components/organisms/Footer/Footer";
import ThemeCard                      from "../components/ThemeCard";
import { useCourseWithSubject }       from "../hooks/useCourseWithSubject";
import { useThemes }                  from "../hooks/useThemes";
import styles                         from "./Themes.module.css";

export default function ThemesPage() {
  const { courseId, subjectId } = useParams();
  const nav  = useNavigate();
  const [q, setQ] = useState("");

  const { data: course }    = useCourseWithSubject(Number(courseId));
  const { data: themes = [] } = useThemes(Number(subjectId));

  if (!course) return null;
  const subject   = course.subjects.find(s => s.id === Number(subjectId));
  const filtered  = themes.filter(t => t.title.toLowerCase().includes(q.toLowerCase()));

  return (
    <>
      <NavBar />

      {/* Wrapper flex para empujar el footer abajo */}
      <div className={styles.page}>
        <main className={styles.main}>
          {/* Cabecera con botón volver */}
          <header className={styles.headerRow}>
            <button
              className={styles.backBtn}
              onClick={() => nav(-1)}
              aria-label="Volver"
            >
              ← Volver
            </button>
            <h1 className={styles.heading}>
              {course.title} – {subject?.name ?? "Asignatura"}
            </h1>
          </header>

          {/* Buscador */}
          <div className={styles.searchContainer}>
            <input
              className={styles.search}
              placeholder="Buscar tema…"
              value={q}
              onChange={e => setQ(e.target.value)}
            />
          </div>

          {/* Lista o estado vacío */}
          {filtered.length === 0 ? (
            <p className={styles.empty}>
              {themes.length === 0
                ? "Esta asignatura aún no tiene temas."
                : "No hay temas que coincidan con tu búsqueda."}
            </p>
          ) : (
            <ul className={styles.grid}>
              {filtered.map(t => <ThemeCard key={t.id} theme={t} />)}
            </ul>
          )}
        </main>

        <Footer />
      </div>
    </>
  );
}
