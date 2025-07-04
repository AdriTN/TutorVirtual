import { useNavigate }     from "react-router-dom";
import NavBar              from "@components/organisms/NavBar/NavBar";
import Footer              from "@components/organisms/Footer/Footer";
import { Spinner }         from "@components/atoms/Spinner";
import { useMe }           from "../hooks/useMe";
import { useMyCourses }    from "../hooks/useMyCourses";
import styles              from "./Dashboard.module.css";

const Dashboard: React.FC = () => {
  const navigate      = useNavigate();
  const { data: me,       isLoading: meLoading }       = useMe();
  const { data: courses,  isLoading: coursesLoading }  = useMyCourses();

  if (meLoading || coursesLoading)
    return <div className={styles.loading}><Spinner size={32}/> Cargando…</div>;

  return (
    <>
      <NavBar />

      <main className={styles.wrapper}>
        {/* ───────── Hero ───────── */}
        {me && (
          <header className={styles.hero}>
            <h1>
              ¡Bienvenido, <span>{me.username}</span>!
            </h1>
            <p className={styles.subtitle}>
              Gestiona tus cursos, revisa tu progreso y descubre
              recomendaciones personalizadas.
            </p>
          </header>
        )}

        {/* ───────── Mis cursos ───────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Mis Cursos</h2>

          {!courses?.length ? (
            <div className={styles.emptyState}>
              <p>Aún no estás inscrito en ningún curso.</p>
              <button
                className={styles.primaryBtn}
                onClick={() => navigate("/courses")}
              >
                Explorar cursos
              </button>
            </div>
          ) : (
            <ul className={styles.cardGrid}>
              {courses.map(c => (
                <li key={c.id} className={styles.courseCard}>
                  <header className={styles.cardHeader}>
                    <span className={styles.courseEmoji}>📚</span>
                    <h3 className={styles.cardTitle}>{c.title}</h3>
                  </header>

                  <p className={styles.description}>
                    {c.description ?? "Sin descripción"}
                  </p>

                  {/* TODO: sustituir 45 % por c.progress cuando exista */}
                  <div className={styles.progressWrap}>
                    <div className={styles.progressFill} style={{ width: "99%" }}/>
                  </div>
                  <span className={styles.progressText}>99 % completado</span>

                  <button
                    className={styles.continueBtn}
                    onClick={() => navigate(`/my-subjects/${c.id}`)}
                  >
                    Continuar →
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <Footer />
    </>
  );
};

export default Dashboard;
