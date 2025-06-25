import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import NavBar        from "@/components/organisms/NavBar/NavBar";
import Footer        from "@/components/organisms/Footer/Footer";
import HeaderBar     from "../components/HeaderBar/HeaderBar";
import ExerciseCard  from "../components/ExerciseCard/ExerciseCard";
import Controls      from "../components/Controls/Controls";

import { useExercise } from "../hooks/useExercise";
import { fetchCourse, fetchThemes } from "@services/api";

import styles from "./study.module.css";

export default function StudyPage() {
  const { courseId, subjectId } = useParams<{ courseId: string; subjectId: string }>();
  const nav = useNavigate();

  const {
    exercise, loading, error,
    checked, isCorrect, generate, check,
  } = useExercise();

  /* ---------- estado local ---------- */
  const [course, setCourse]   = useState<any>(null);
  const [subject, setSubject] = useState<any>(null);
  const [themes, setThemes]   = useState<any[]>([]);
  const [theme,  setTheme]    = useState<any | null>(null);
  const [difficulty, setDifficulty] = useState("fácil");
  const [answer, setAnswer]   = useState("");

  /* ---------- carga de curso & asignatura ---------- */
  useEffect(() => {
    if (!courseId || !subjectId) return;

    fetchCourse(+courseId)
      .then(c => {
        setCourse(c);
        setSubject(c.subjects.find((s: any) => s.id === +subjectId) || null);
      })
      .catch(() => nav("/error", { replace: true }));
  }, [courseId, subjectId, nav]);

  /* ---------- temas de la asignatura ---------- */
  useEffect(() => {
    if (!subject) return;
    fetchThemes(subject.id).then(setThemes);
  }, [subject]);

  /* ---------- generar ejercicio ---------- */
  const onGenerate = () => {
    if (!theme) return;

    generate({
      model: "profesor",
      response_format: { type: "json_object" },
      messages: [
        {
          role: "user",
          content: `Genera un ejercicio sobre "${theme.title}" en dificultad ${difficulty}`,
        },
      ],
    });

    setAnswer("");
  };

  /* ==================================================================== */
  return (
    <div className={styles.page}>
      <NavBar />

      {course && subject && (
        <main className={styles.main}>
          <HeaderBar
            course={course}
            subject={subject}
            difficulty={difficulty}
            onDifficultyChange={setDifficulty}
          />

          {/* selector de tema + botón */}
          <div className={styles.generateBox}>
            <select
              className={styles.select}
              value={theme?.id || ""}
              onChange={e => {
                const t = themes.find(t => t.id === +e.target.value);
                setTheme(t || null);
              }}
            >
              <option value="">Selecciona tema…</option>
              {themes.map(t => (
                <option key={t.id} value={t.id}>{t.title}</option>
              ))}
            </select>

            {!exercise && theme && (
              <button
                className={styles.generateBtn}
                onClick={onGenerate}
                disabled={loading}
              >
                {loading ? "Generando…" : "Generar pregunta"}
              </button>
            )}
          </div>

          {/* error backend */}
          {error && <p className={styles.statusError}>{error}</p>}

          {/* ejercicio actual */}
          {exercise && (
            <>
              <ExerciseCard
                enunciado={exercise.enunciado}
                explanation={exercise.explicacion}
                checked={checked}
                isCorrect={isCorrect}
              />

              <Controls
                userAnswer={answer}
                onAnswerChange={setAnswer}
                onCheck={() => check(answer)}
                onNext={onGenerate}
                loading={loading}
                checked={checked}
              />
            </>
          )}
        </main>
      )}

      <Footer />
    </div>
  );
}
