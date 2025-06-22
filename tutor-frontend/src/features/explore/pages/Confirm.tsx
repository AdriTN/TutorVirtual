import { useSearchParams, useParams, useNavigate } from "react-router-dom";
import NavBar                    from "@components/organisms/NavBar/NavBar";
import Footer                    from "@components/organisms/Footer/Footer";
import StepIndicator             from "@components/molecules/StepIndicator";
import { useCourse }             from "../hooks/useCourse";
import { useEnrollSubject }      from "../hooks/useEnrollSubject";
import css                       from "./explore.module.css";

export default function ConfirmPage() {
  const { id }                = useParams<{ id: string }>();
  const courseId              = Number(id);
  const [sp]                  = useSearchParams();
  const subjectId             = Number(sp.get("subject"));
  const { data: course }      = useCourse(courseId);
  const enrollMutation        = useEnrollSubject();
  const navigate              = useNavigate();

  if (!course) return null;
  const subject = course.subjects.find(s => s.id === subjectId);

  const confirm = async () => {
    await enrollMutation.mutateAsync(subjectId);
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className={css.page}>
      <NavBar />
      <main className={css.main}>
        <div className={css.wrapper}>
          <StepIndicator current={3} steps={["Curso","Asignatura","Confirmar"]}/>
        </div>

        <section className={css.confirmBox}>
          <h2 className={css.confirmTitle}>Confirmar inscripción</h2>

          <ul className={css.confirmList}>
            <li className={css.row}>
              <span className={css.key}>Curso:</span>
              <span className={css.val}>{course.title}</span>
            </li>
            {subject && (
              <li className={css.row}>
                <span className={css.key}>Asignatura:</span>
                <span className={css.val}>{subject.name}</span>
              </li>
            )}
          </ul>

          <div className={css.actions}>
            <button className={css.btnOutline} onClick={() => navigate(-1)}>
              Cancelar
            </button>
            <button
              className={css.btnPrimary}
              disabled={enrollMutation.isPending}
              onClick={confirm}
            >
              {enrollMutation.isPending ? "Matriculando…" : "Confirmar"}
            </button>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
