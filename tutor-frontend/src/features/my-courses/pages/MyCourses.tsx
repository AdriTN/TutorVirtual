import { useState }       from "react";
import { useNavigate }    from "react-router-dom";
import NavBar             from "@components/organisms/NavBar/NavBar";
import Footer             from "@components/organisms/Footer/Footer";
import Spinner            from "@components/atoms/Spinner/Spinner";
import CourseCard         from "../components/CourseCard/CourseCard";
import { useMyCourses }   from "../hooks/useMyCourses";
import { useUnenrollCourse } from "../hooks/useUnenrollCourse";
import styles             from "./MyCourses.module.css";

const MyCoursesPage: React.FC = () => {
  const nav = useNavigate();
  const [search, setSearch] = useState("");

  const { data: courses = [], isLoading } = useMyCourses();
  const unenroll = useUnenrollCourse();

  const filtered = courses.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = (id: number) => {
    if (confirm("¿Eliminar este curso y sus asignaturas?")) {
      unenroll.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.center}>
        <Spinner size={40}/>
      </div>
    );
  }

  return (
    <>
      <NavBar />

      <main className={styles.main}>
        <div className={styles.searchContainer}>
          <input
            className={styles.search}
            placeholder="Buscar curso…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>
            Aún no tienes cursos con asignaturas matriculadas.
          </p>
        ) : (
          <ul className={styles.grid}>
            {filtered.map(c => (
              <CourseCard
                key={c.id}
                course={c}
                onDelete={handleDelete}
                onView={ id => nav(`/my-subjects/${id}`)}
              />
            ))}
          </ul>
        )}

        <button className={styles.cta} onClick={() => nav("/courses")}>
          Explorar cursos
        </button>
      </main>

      <Footer />
    </>
  );
};

export default MyCoursesPage;
