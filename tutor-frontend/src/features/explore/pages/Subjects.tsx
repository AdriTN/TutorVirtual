import { useState }               from "react";
import { useNavigate, useParams } from "react-router-dom";

import NavBar           from "@components/organisms/NavBar/NavBar";
import Footer           from "@components/organisms/Footer/Footer";
import StepIndicator    from "@components/molecules/StepIndicator";

import { useCourse }    from "../hooks/useCourse";
import SubjectCard      from "../components/subjectCard/SubjectCard";

import styles           from "./Explore.module.css";

export default function SubjectsPage() {
  const { id }           = useParams<{ id: string }>();
  const courseId         = Number(id);
  const { data: course } = useCourse(courseId);
  const [query, setQuery]= useState("");
  const nav              = useNavigate();

  if (!course) return null;

  const filtered = course.subjects.filter(s =>
    s.name.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <>
      <NavBar />

      <div className={styles.page}>
        <main className={styles.main}>
          <header className={styles.headerRow}>
            <button
              className={styles.backBtn}
              onClick={() => nav("/courses")}
            >
              ← Volver
            </button>
            <StepIndicator current={2} steps={["Curso", "Asignatura", "Confirmar"]} />
          </header>

          <h2 className={styles.headingLeft}>{course.title}</h2>

          {/* buscador */}
          <div className={styles.searchContainer}>
            <input
              className={styles.search}
              placeholder="Buscar asignatura…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>

          {/* grid de asignaturas */}
          <ul className={styles.grid}>
            {filtered.map(subject => (
              <SubjectCard key={subject.id} subject={subject} />
            ))}
          </ul>
        </main>

        <Footer />
      </div>
    </>
  );
}
