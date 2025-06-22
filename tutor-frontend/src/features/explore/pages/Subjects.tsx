import { useState }              from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar                    from "@components/organisms/NavBar/NavBar";
import Footer                    from "@components/organisms/Footer/Footer";
import StepIndicator             from "@components/molecules/StepIndicator";
import { useCourse }             from "../hooks/useCourse";
import css                       from "./explore.module.css";

export default function SubjectsPage() {
  const { id }                     = useParams<{ id: string }>();
  const courseId                   = Number(id);
  const { data: course, isLoading }= useCourse(courseId);
  const [query, setQuery]          = useState("");
  const navigate                   = useNavigate();

  if (isLoading || !course) return null;

  const filtered = course.subjects.filter(s =>
    s.name.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className={css.page}>
      <NavBar />
      <main className={css.main}>
        <div className={css.wrapper}>
          <StepIndicator current={2} steps={["Curso","Asignatura","Confirmar"]}/>
        </div>

        <h2 className={css.left}>{course.title}</h2>
        <div className={css.searchContainerLeft}>
          <input
            className={css.search}
            placeholder="Buscar asignatura…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>

        <ul className={css.gridFull}>
          {filtered.map(subject => (
            <li key={subject.id} className={css.card}>
              <h3 className={css.title}>{subject.name}</h3>
              <p  className={css.desc}>{subject.description ?? "Sin descripción"}</p>

              {subject.enrolled ? (
                <span className={css.feedback}>Matriculada</span>
              ) : (
                <button
                  className={`${css.btn} ${css.primary}`}
                  onClick={() =>
                    navigate(`/courses/${courseId}/confirm?subject=${subject.id}`)
                  }
                >
                  Elegir
                </button>
              )}
            </li>
          ))}
        </ul>
      </main>

      <button
        className={css.backBtn}
        onClick={() => navigate("/courses")}
      >
        ← Volver
      </button>

      <Footer />
    </div>
  );
}
