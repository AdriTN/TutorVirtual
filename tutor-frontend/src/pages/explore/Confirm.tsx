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
  /* ---------- params & nav ---------- */
  const { id } = useParams<{ id: string }>();      // courseId
  const [sp] = useSearchParams();
  const subjectId = Number(sp.get("subject"));
  const nav = useNavigate();

  /* ---------- state ---------- */
  const [course, setCourse] = useState<Course | null>(null);
  const [status, setStatus] = useState<"idle" | "done">("idle");

  /* ---------- load data ---------- */
  useEffect(() => {
    if (id) fetchCourse(Number(id)).then(setCourse);
  }, [id]);

  /* ---------- confirm ---------- */
  const onConfirm = async () => {
    if (!subjectId) return;
    try {
      await enrollSubject(subjectId);
      setStatus("done");
      setTimeout(() => nav("/dashboard"), 1200);
    } catch {
      alert("No se pudo completar la inscripción.");
    }
  };

  if (!course) return null;
  const subj = course.subjects.find((s) => s.id === subjectId);

  /* ---------- UI ---------- */
  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        <div className={styles.wrapper}>
          <StepIndicator current={3} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]} />
        </div>

        {/* caja minimalista */}
        <section className={styles.confirmBox}>
          <h2 className={styles.confirmTitle}>Confirmar inscripción</h2>

          <ul className={styles.confirmList}>
            <li className={styles.row}>
              <span className={styles.key}>Curso:</span>
              <span className={styles.val}>{course.title}</span>
            </li>
            {subj && (
              <li className={styles.row}>
                <span className={styles.key}>Asignatura:</span>
                <span className={styles.val}>{subj.name}</span>
              </li>
            )}
          </ul>

          {status === "done" ? (
            <p className={styles.feedbackCenter}>¡Inscripción completada!</p>
          ) : (
            <div className={styles.actions}>
              <button className={styles.btnOutline} onClick={() => nav(-1)}>
                Cancelar
              </button>
              <button className={styles.btnPrimary} onClick={onConfirm}>
                Confirmar
              </button>
            </div>
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default ConfirmPage;
