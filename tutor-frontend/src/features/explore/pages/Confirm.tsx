import { useSearchParams, useParams, useNavigate } from "react-router-dom";

import NavBar        from "@components/organisms/NavBar/NavBar";
import Footer        from "@components/organisms/Footer/Footer";
import StepIndicator from "@components/molecules/StepIndicator";
import { useNotifications } from "@hooks/useNotifications";

import { useCourse }        from "../hooks/useCourse";
import { useEnrollSubject } from "../hooks/useEnrollSubject";

import styles       from "./Explore.module.css";

export default function ConfirmPage() {
  const { id }       = useParams<{ id: string }>();
  const courseId     = Number(id);
  const [sp]         = useSearchParams();
  const subjectId    = Number(sp.get("subject"));

  const { data: course } = useCourse(courseId);
  const enroll           = useEnrollSubject();
  const nav              = useNavigate();
  const { notifySuccess } = useNotifications();

  if (!course) return null;
  const subject = course.subjects.find(s => s.id === subjectId);

  const confirm = async () => {
    await enroll.mutateAsync({ subjectId, courseId });
    notifySuccess(`Te has inscrito correctamente en ${subject ? subject.name : 'la asignatura'} del curso ${course.title}.`);
    nav("/dashboard", { replace: true });
  };

  return (
    <>
      <NavBar />

      <div className={styles.page}>
        <main className={styles.main}>
          <header className={styles.headerRow}>
            <button className={styles.backBtn} onClick={() => nav(-1)}>← Volver</button>
            <StepIndicator current={3} steps={["Curso", "Asignatura", "Confirmar"]} />
          </header>

          <section className={styles.confirmBox}>
            <h2 className={styles.confirmTitle}>Confirmar inscripción</h2>

            <ul className={styles.confirmList}>
              <li className={styles.row}>
                <span className={styles.key}>Curso:</span>
                <span className={styles.val}>{course.title}</span>
              </li>
              {subject && (
                <li className={styles.row}>
                  <span className={styles.key}>Asignatura:</span>
                  <span className={styles.val}>{subject.name}</span>
                </li>
              )}
            </ul>

            <div className={styles.actions}>
              <button className={styles.btnOutline} onClick={() => nav(-1)}>
                Cancelar
              </button>
              <button
                className={styles.btnPrimary}
                disabled={enroll.isPending}
                onClick={confirm}
              >
                {enroll.isPending ? "Matriculando…" : "Confirmar"}
              </button>
            </div>
          </section>
        </main>

        <Footer />
      </div>
    </>
  );
}
