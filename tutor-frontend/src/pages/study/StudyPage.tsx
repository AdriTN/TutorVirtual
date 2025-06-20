/* ------------------------------------------------------------------
   StudyPage – genera ejercicios IA, envía la respuesta y refresca stats
------------------------------------------------------------------ */
import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

import NavBar   from "../utils/NavBar/NavBar";
import Footer   from "../utils/Footer/Footer";

import {
  Course, 
  Subject, 
  Theme, 
  AIRequest, 
  AIExerciseOut,
  fetchCourse,
  fetchThemes,
  askAI,
  sendAnswer,
} from "../../utils/enrollment";

import styles from "./study.module.css";

/* ───────────── constantes ───────────── */
const DIFFICULTIES = ["fácil", "intermedia", "difícil"] as const;
type Difficulty = (typeof DIFFICULTIES)[number];

/* ────────────────────────────────────── */
const StudyPage: React.FC = () => {
  /* ------- routing params ------- */
  const { courseId, subjectId } = useParams<{ courseId: string; subjectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  /* ------- datos base -------- */
  const [course,  setCourse]  = useState<Course|null>(null);
  const [subject, setSubject] = useState<Subject|null>(null);

  /* ------- temas + dificultad ------- */
  const [themes, setThemes] = useState<Theme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<Theme|null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>("fácil");

  /* ------- ejercicio & UI ------- */
  const [exercise, setExercise]   = useState<AIExerciseOut|null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [checked, setChecked] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean|null>(null);

  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string|null>(null);

  /* timestamp inicio ejercicio */
  const startTs = useRef<number|null>(null);

  /* ─── 1) cargar curso + asignatura ─── */
  useEffect(() => {
    if (!courseId || !subjectId) return;
    fetchCourse(+courseId)
      .then((c) => {
        setCourse(c);
        const sub = c.subjects.find((s) => s.id === +subjectId) ?? null;
        setSubject(sub);
      })
      .catch(() => navigate("/error", { replace: true }));
  }, [courseId, subjectId, navigate]);

  /* ─── 2) cargar temas ─── */
  useEffect(() => {
    if (!subject) return;
    fetchThemes(subject.id).then(setThemes).catch(console.error);
  }, [subject]);

  /* ─── 3) limpiar estado al cambiar tema o dificultad ─── */
  useEffect(() => {
    setExercise(null);
    setChecked(false);
    setIsCorrect(null);
    setUserAnswer("");
    startTs.current = null;
  }, [selectedTheme, difficulty]);

  /* ─── generar ejercicio ─── */
  const generateExercise = async () => {
    if (!selectedTheme) return;
  
    // ── limpiar UI del ejercicio anterior ──
    setExercise(null);
    setUserAnswer("");
    setChecked(false);
    setIsCorrect(null);
    startTs.current = null;
  
    setLoading(true);
    setError(null);
  
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
      const ex = await askAI(body);
      setExercise(ex);
      startTs.current = performance.now();
    } catch (e: any) {
      setError(e.message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  /* ─── comprobar respuesta ─── */
  const handleCheck = async () => {
    if (!exercise) return;
    const t = startTs.current
      ? Math.round((performance.now() - startTs.current) / 1000)
      : undefined;

    try {
      const res = await sendAnswer(exercise.id, userAnswer, t);
      setChecked(true);
      setIsCorrect(res.correcto);
      queryClient.invalidateQueries({ queryKey: ["stats", "overview"] });
    } catch (e:any) {
      setError(e.message ?? "Error al enviar respuesta");
    }
  };

  const handleNext = () => generateExercise();

  if (!course || !subject) return null;

  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        {/* ── cabecera ── */}
        <header className={styles.header}>
          <div className={styles.courseInfo}>{course.title} – {subject.name}</div>

          <label className={styles.selectWrapper}>
            <span className={styles.selectLabel}>Dificultad:</span>
            <select
              id="difficultySelect"
              className={styles.select}
              value={difficulty}
              onChange={(e)=>setDifficulty(e.target.value as Difficulty)}
            >
              {DIFFICULTIES.map(d=>(
                <option key={d} value={d}>{d[0].toUpperCase()+d.slice(1)}</option>
              ))}
            </select>
          </label>
        </header>

        {/* ── selector de tema ── */}
        <div className={styles.generateBox}>
          <label htmlFor="themeSelect" className={styles.selectLabel}>Tema:</label>
          <select
            id="themeSelect"
            className={styles.select}
            value={selectedTheme?.id ?? ""}
            onChange={e=>{
              const t = themes.find(t=>t.id===+e.target.value)!;
              setSelectedTheme(t);
            }}
          >
            <option value="" disabled>Selecciona un tema…</option>
            {themes.map(t=><option key={t.id} value={t.id}>{t.title}</option>)}
          </select>

          {!exercise && selectedTheme && (
            <button className={styles.generateBtn}
                    onClick={generateExercise}
                    disabled={loading}>
              {loading ? "Generando…" : "Generar pregunta"}
            </button>
          )}
        </div>

        {loading && !exercise && <p className={styles.status}>Generando…</p>}
        {error && <p className={styles.status}>Error: {error}</p>}

        {/* ── ejercicio ── */}
        {exercise && (
          <section className={styles.contentBox}>
            <p className={styles.question}>{exercise.enunciado}</p>

            <input
              className={styles.answerInput}
              placeholder="Tu respuesta…"
              value={userAnswer}
              onChange={e=>setUserAnswer(e.target.value)}
              disabled={checked}
            />

            <button className={styles.checkBtn}
                    onClick={handleCheck}
                    disabled={checked||userAnswer.trim()===""}>
              Comprobar
            </button>

            {checked && (
              <div className={isCorrect?styles.feedbackCorrect:styles.feedbackIncorrect}>
                {isCorrect ? "¡Correcto!" : "Incorrecto"}
              </div>
            )}

            {checked && (
              <div className={styles.explanation}>
                <p><strong>Respuesta correcta:</strong> {exercise.explicacion || "(ver solución)"}</p>
              </div>
            )}
          </section>
        )}

        {/* ── navegación ── */}
        {exercise && (
          <footer className={styles.navBtns}>
            <button className={styles.navBtn} disabled>← Anterior</button>
            <button className={styles.navBtn} onClick={handleNext} disabled={loading}>
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
