import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./Dashboard.module.css";
import { api } from "../../services/apis/backend-api/api";

interface Course {
  id: number;
  title: string;
  description?: string | null;
}

interface UserData {
  id: number;
  name: string;
  email: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const [userData, setUserData] = useState<UserData | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [uRes, cRes] = await Promise.all([
          api.get<UserData>("/api/users/me"),
          api.get<Course[]>("/api/course/my"),
        ]);
        setUserData(uRes.data);
        setCourses(cRes.data);
      } catch (err) {
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className={styles.loading}>Cargando…</div>;

  return (
    <>
      <NavBar />

      <main className={styles.wrapper}>
        {/* Encabezado */}
        {userData && (
          <header className={styles.hero}>
            <h1>
              ¡Bienvenido, <span>{userData.name}</span>!
            </h1>
            <p className={styles.subtitle}>
              Este es tu panel de control: gestiona tus cursos, revisa tu
              progreso y descubre recomendaciones personalizadas.
            </p>
          </header>
        )}

        {/* MIS CURSOS */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Mis Cursos</h2>

          {courses.length === 0 ? (
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
              {courses.map((c) => (
                <li key={c.id} className={styles.courseCard}>
                  {/* cabecera con gradiente y un icono/emoji */}
                  <header className={styles.cardHeader}>
                    <span className={styles.courseEmoji}>📚</span>
                    <h3 className={styles.cardTitle}>{c.title}</h3>
                  </header>
                
                  {/* descripción corta */}
                  <p className={styles.description}>
                    {c.description ?? "Sin descripción"}
                  </p>
                
                  {/* barra de progreso */}
                  <div className={styles.progressWrap}>
                    <div
                      className={styles.progressFill}
                      style={{ width: "45%" }} /* sustituye por c.progress */
                    />
                  </div>
                  <span className={styles.progressText}>45 % completado</span>
                
                  {/* CTA */}
                  <button
                    className={styles.continueBtn}
                    onClick={() => navigate(`/courses/${c.id}`)}
                  >
                    Continuar →
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* RECOMENDACIONES */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Recomendaciones</h2>
          <div className={styles.recoCard}>
            <h3>Ejemplo de recomendación</h3>
            <p>
              🎯 Completa el módulo <strong>“Funciones Cuadráticas”</strong> para
              fortalecer tu base antes del examen.
            </p>
          </div>
        </section>

        {/* ESTADÍSTICAS */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Estadísticas</h2>
          <div className={styles.statsBox}>
            <p>Gráfica de progreso próximamente 📈</p>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
};

export default Dashboard;
