import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import styles from "./explore.module.css";
import { Course, enroll, fetchCourse } from "../../utils/enrollment";
import StepIndicator from "../../components/stepIndicator/StepIndicator";

const ConfirmPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [sp] = useSearchParams();
  const subId = Number(sp.get("subject"));
  const nav = useNavigate();

  const [course, setCourse] = useState<Course | null>(null);
  const [status, setStatus] = useState<"idle" | "done">("idle");

  useEffect(() => {
    fetchCourse(Number(id)).then(setCourse);
  }, [id]);

  const onConfirm = async () => {
    try {
      await enroll(Number(id), subId);
      setStatus("done");
      setTimeout(() => nav("/dashboard"), 1200);
    } catch (e) {
      alert("Ya estás matriculado.");
    }
  };

  if (!course) return null;

  const subj = course.subjects.find((s) => s.id === subId);

  return (
    <div className={styles.page}>
      <NavBar />
      <main className={styles.main}>
        <div className={styles.wrapper}>
        <StepIndicator current={3} steps={["CURSO", "ASIGNATURA", "CONFIRMAR"]}
        />

          <h2>Confirma tu inscripción</h2>
          <p>Curso: <strong>{course.title}</strong></p>
          <p>Asignatura: <strong>{subj?.name}</strong></p>

          {status === "done" ? (
            <p className={styles.feedback}>¡Inscripción completada!</p>
          ) : (
            <div style={{ marginTop: "1rem" }}>
              <button className={`${styles.btn} ${styles.outline}`} onClick={() => nav(-1)}>
                Volver
              </button>
              <button className={`${styles.btn} ${styles.primary}`} onClick={onConfirm}>
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
