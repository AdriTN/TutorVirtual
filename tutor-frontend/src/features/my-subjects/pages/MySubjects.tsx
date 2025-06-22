import { useState }               from "react";
import { useParams, useNavigate } from "react-router-dom";
import NavBar                     from "@components/organisms/NavBar/NavBar";
import Footer                     from "@components/organisms/Footer/Footer";
import Spinner                    from "@components/atoms/Spinner/Spinner";
import SubjectCard                from "../components/SubjectCard/SubjectCard";
import { useCourseSubjects }      from "../hooks/useCourseSubjects";
import { useUnenrollSubject }     from "../hooks/useUnenrollSubject";
import styles                     from "./MySubjects.module.css";

const MyCourseSubjectsPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate        = useNavigate();
  const [search, setSearch] = useState("");

  const { data: course, isLoading } = useCourseSubjects(Number(courseId));
  const unenroll = useUnenrollSubject(Number(courseId));

  const handleDelete = (subjectId: number) => {
    if (confirm("¿Eliminar esta asignatura?")) {
      unenroll.mutate(subjectId);
    }
  };

  if (isLoading || !course) {
    return (
      <div className={styles.center}>
        <Spinner size={40}/>
      </div>
    );
  }

  const subjects = course.subjects.filter(s => s.enrolled);
  const filtered = subjects.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <NavBar />
      <main className={styles.main}>
        <header className={styles.wrapper}>
          <h1 className={styles.heading}>{course.title}</h1>
        </header>

        <div className={styles.searchContainer}>
          <input
            className={styles.search}
            placeholder="Buscar asignatura…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>Sin asignaturas que coincidan.</p>
        ) : (
          <ul className={styles.grid}>
            {filtered.map(s => (
              <SubjectCard
                key={s.id}
                subject={s}
                onDelete={handleDelete}
                onThemes={sid => navigate(`/my-subjects/${courseId}/${sid}/themes`)}
                onStudy ={sid => navigate(`/study/${courseId}/${sid}`)}
              />
            ))}
          </ul>
        )}
      </main>

      <button
        className={styles.backBtn}
        onClick={() => navigate("/my-courses")}
      >
        ← Volver
      </button>

      <Footer />
    </>
  );
};

export default MyCourseSubjectsPage;
