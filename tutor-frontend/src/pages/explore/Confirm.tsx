/* ------------------------------------------------------------------
   src/pages/explore/ConfirmPage.tsx
------------------------------------------------------------------- */
import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, fetchCourse, enrollSubject } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

const ConfirmPage: React.FC = () => {
  /* ---------------- params & nav ---------------- */
  const { id } = useParams<{ id: string }>();              // courseId
  const [sp] = useSearchParams();
  const subjectId = Number(sp.get("subject"));             // asignatura elegida
  const nav = useNavigate();

  /* ---------------- estado ---------------- */
  const [course, setCourse] = useState<Course | null>(null);
  const [status, setStatus] = useState<"idle" | "done">("idle");

  /* ---------------- carga de datos ---------------- */
  useEffect(() => {
    if (id) fetchCourse(Number(id)).then(setCourse);
  }, [id]);

  /* ---------------- confirmación ---------------- */
  const onConfirm = async () => {
    if (!subjectId) return;
    try {
      await enrollSubject(subjectId);   // POST /subject/{subjectId}/enroll
      setStatus("done");
      setTimeout(() => nav("/dashboard"), 1200);
    } catch {
      alert("No se pudo completar la inscripción (quizá ya estabas matriculado).");
    }
  };

  if (!course) return null;

  const subj = course.subjects.find((s) => s.id === subjectId);

  /* ---------------- UI ---------------- */
  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        <div className={styles.wrapper}>
          <StepIndicator current={3} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]} />

          <h2>Confirma tu inscripción</h2>
          <p>
            Curso: <strong>{course.title}</strong>
          </p>
          {subj && (
            <p>
              Asignatura: <strong>{subj.name}</strong>
            </p>
          )}

          {status === "done" ? (
            <p className={styles.feedback}>¡Inscripción completada!</p>
          ) : (
            <div style={{ marginTop: "1rem" }}>
              <button className={`${styles.btn} ${styles.outline}`} onClick={() => nav(-1)}>
                Volver
              </button>
              <button
                className={`${styles.btn} ${styles.primary}`}
                onClick={onConfirm}
              >
                Confirmar
              </button>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ConfirmPage;
