import { useState }      from "react";

import NavBar            from "@components/organisms/NavBar/NavBar";
import Footer            from "@components/organisms/Footer/Footer";
import StepIndicator     from "@components/molecules/StepIndicator";

import { useCourses }    from "../hooks/useCourses";
import CourseCard        from "../components/courseCard/CourseCard";

import styles            from "./explore.module.css";

export default function CoursesPage() {
  const { data = [], isLoading } = useCourses();
  const [query, setQuery]        = useState("");

  if (isLoading) return <p className={styles.loading}>Cargando…</p>;

  const filtered = data.filter(c =>
    c.title.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <>
      <NavBar />

      <div className={styles.page}>
        <main className={styles.main}>
          <header className={styles.headerRow}>
            <StepIndicator current={1} steps={["Curso", "Asignatura", "Confirmar"]} />
          </header>

          {/* buscador */}
          <div className={styles.searchContainer}>
            <input
              className={styles.search}
              placeholder="Buscar curso…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>

          {/* grid de cursos */}
          <ul className={styles.grid}>
            {filtered.map(course => (
              <CourseCard key={course.id} course={course} />
            ))}
          </ul>
        </main>

        <Footer />
      </div>
    </>
  );
}
