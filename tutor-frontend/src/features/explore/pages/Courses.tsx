import { useState }              from "react";
import { useNavigate }           from "react-router-dom";
import NavBar                    from "@components/organisms/NavBar/NavBar";
import Footer                    from "@components/organisms/Footer/Footer";
import StepIndicator             from "@components/molecules/StepIndicator";
import { useCourses }            from "../hooks/useCourses";
import type { Course }           from "@types";
import css                       from "./explore.module.css";

export default function CoursesPage() {
  const { data = [], isLoading } = useCourses();
  const [query, setQuery]        = useState("");
  const navigate                 = useNavigate();

  if (isLoading) return <p className={css.loading}>Cargando…</p>;
  const courses = data as Course[];

  const filtered = courses.filter(c =>
    c.title.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className={css.page}>
      <NavBar />
      <main className={css.main}>
        <div className={css.wrapper}>
          <StepIndicator current={1} steps={["Curso","Asignatura","Confirmar"]} />
          <div className={css.searchContainer}>
            <input
              className={css.search}
              placeholder="Buscar curso…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
        </div>

        <ul className={css.grid}>
          {filtered.map(course => {
            const { id, title, description, subjects } = course;
            const fullyEnrolled =
              subjects.length > 0 && subjects.every(s => s.enrolled);

            return (
              <li key={id} className={css.card}>
                <h3 className={css.title}>{title}</h3>
                <p  className={css.desc}>{description ?? "Sin descripción"}</p>

                {!!subjects.length && (
                  <div className={css.subjects}>
                    {subjects.slice(0,3).map(s =>
                      <span key={s.id} className={css.badge}>{s.name}</span>
                    )}
                    {subjects.length > 3 && <span className={css.badge}>…</span>}
                  </div>
                )}

                {fullyEnrolled ? (
                  <span className={css.feedback}>Ya cursas todas</span>
                ) : (
                  <button
                    className={`${css.btn} ${css.primary}`}
                    onClick={() => navigate(`/courses/${id}`)}
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
}
