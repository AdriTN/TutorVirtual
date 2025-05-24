/* ------------------------------------------------------------------
   src/pages/study/StudyPage.tsx
------------------------------------------------------------------ */
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import NavBar from "../utils/NavBar/NavBar";
import Footer from "../utils/Footer/Footer";
import {
  fetchCourse,
  fetchThemes,
  fetchAIQuestion,
  AIRequest,
  Theme,
  Course,
  Subject,
} from "../../utils/enrollment";
import styles from "./study.module.css";

/* -------- respuesta esperada de la IA -------- */
interface AIExercise {
  tema: string;
  enunciado: string;
  respuesta: string;
  dificultad: string;
  tipo?: string;
  explicacion: string;
}

const DIFFICULTIES = ["fácil", "intermedia", "difícil"] as const;
type Difficulty = (typeof DIFFICULTIES)[number];

const StudyPage: React.FC = () => {
  /* ---------------- routing ---------------- */
  const { courseId, subjectId } = useParams<{
    courseId: string;
    subjectId: string;
  }>();
  const nav = useNavigate();

  /* ---------------- datos curso / asignatura ---------------- */
  const [course, setCourse]     = useState<Course | null>(null);
  const [subject, setSubject]   = useState<Subject | null>(null);

  /* ---------------- temas & dificultad ---------------------- */
  const [themes, setThemes]               = useState<Theme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [difficulty, setDifficulty]       = useState<Difficulty>("fácil");

  /* ---------------- ejercicio & UI state -------------------- */
  const [exercise, setExercise] = useState<AIExercise | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [checked, setChecked]       = useState(false);
  const [isCorrect, setIsCorrect]   = useState<boolean | null>(null);

  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  /* ──────────────────────────────────────────
     1) Cargar curso y asignatura
     ────────────────────────────────────────── */
  useEffect(() => {
    if (!courseId || !subjectId) return;
    fetchCourse(Number(courseId))
      .then((c) => {
        setCourse(c);
        const sub =
          c.subjects.find((s) => s.id === Number(subjectId)) ?? null;
        setSubject(sub);
        return sub;
      })
      .catch(console.error);
  }, [courseId, subjectId]);

  /* ──────────────────────────────────────────
     2) Cargar temas de la asignatura
     ────────────────────────────────────────── */
  useEffect(() => {
    if (!subject) return;
    fetchThemes(subject.id)
      .then(setThemes)
      .catch(console.error);
  }, [subject]);

  /* ──────────────────────────────────────────
     3) Reset cuando cambia tema o dificultad
     ────────────────────────────────────────── */
  useEffect(() => {
    setExercise(null);
    setChecked(false);
    setIsCorrect(null);
    setUserAnswer("");
  }, [selectedTheme, difficulty]);

  /* ──────────────────────────────────────────
     Generar / recargar ejercicio
     ────────────────────────────────────────── */
  const generateExercise = async () => {
    if (!selectedTheme) return;

    /* limpiar antes de fetch */
    setExercise(null);
    setChecked(false);
    setIsCorrect(null);
    setUserAnswer("");
    setError(null);
    setLoading(true);

    const body: AIRequest = {
      model: "profesor",
      response_format: { type: "json_object" },
      messages: [
        {
          role: "user",
          content: `Genera un ejercicio sobre "${selectedTheme.title}" en dificultad ${difficulty}`,
        },
      ],
    };

    try {
      const ex = (await fetchAIQuestion(body)) as AIExercise;
      setExercise(ex);
    } catch (e: any) {
      setError(e.message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  /* ──────────────────────────────────────────
     Comprobar respuesta del usuario
     ────────────────────────────────────────── */
  const handleCheck = () => {
    if (!exercise) return;
    setChecked(true);
    setIsCorrect(
      userAnswer.trim().toLowerCase() === exercise.respuesta.trim().toLowerCase()
    );
  };

  /* navegación (prev sin lógica aún) */
  const handlePrev = () => {};
  const handleNext = () => generateExercise();

  /* si aún no tenemos los datos mínimos */
  if (!course || !subject) return null;

  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        {/* ---------- encabezado ---------- */}
        <header className={styles.header}>
          <div className={styles.courseInfo}>
            {course.title} – {subject.name}
          </div>

          <div className={styles.selectWrapper}>
            <label htmlFor="difficultySelect" className={styles.selectLabel}>
              Dificultad:
            </label>
            <select
              id="difficultySelect"
              className={styles.select}
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as Difficulty)}
            >
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>
                  {d[0].toUpperCase() + d.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </header>

        {/* ---------- selector tema + generar ---------- */}
        <div className={styles.generateBox}>
          <label htmlFor="themeSelect" className={styles.selectLabel}>
            Tema:
          </label>

          <select
            id="themeSelect"
            aria-label="Selecciona tema"
            className={styles.select}
            value={selectedTheme?.id ?? ""}
            onChange={(e) => {
              const t = themes.find((t) => t.id === Number(e.target.value))!;
              setSelectedTheme(t);
            }}
          >
            <option value="" disabled>
              Selecciona un tema…
            </option>
            {themes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title}
              </option>
            ))}
          </select>

          {!exercise && selectedTheme && (
            <button
              className={styles.generateBtn}
              onClick={generateExercise}
              disabled={loading}
            >
              {loading ? "Generando…" : "Generar pregunta"}
            </button>
          )}
        </div>

        {/* ---------- mensajes de estado ---------- */}
        {loading && !exercise && (
          <p className={styles.status}>Generando pregunta…</p>
        )}
        {error && <p className={styles.status}>Error: {error}</p>}

        {/* ---------- ejercicio ---------- */}
        {exercise && (
          <section className={styles.contentBox}>
            <p className={styles.question}>{exercise.enunciado}</p>

            <input
              type="text"
              className={styles.answerInput}
              placeholder="Tu respuesta…"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              disabled={checked}
            />

            <button
              className={styles.checkBtn}
              onClick={handleCheck}
              disabled={checked || userAnswer.trim() === ""}
            >
              Comprobar
            </button>

            {checked && (
              <div
                className={
                  isCorrect ? styles.feedbackCorrect : styles.feedbackIncorrect
                }
              >
                {isCorrect ? "¡Correcto!" : "Incorrecto"}
              </div>
            )}

            {checked && (
              <div className={styles.explanation}>
                <p>
                  <strong>Respuesta correcta:</strong> {exercise.respuesta}
                </p>
                <p>{exercise.explicacion}</p>
              </div>
            )}
          </section>
        )}

        {/* ---------- navegación ---------- */}
        {exercise && (
          <footer className={styles.navBtns}>
            <button
              className={styles.navBtn}
              onClick={handlePrev}
              disabled={loading}
            >
              ← Anterior
            </button>
            <button
              className={styles.navBtn}
              onClick={handleNext}
              disabled={loading}
            >
              Siguiente →
            </button>
          </footer>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default StudyPage;
