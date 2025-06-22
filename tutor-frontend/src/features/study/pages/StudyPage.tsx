import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useExercise } from "../hooks/useExercise";
import HeaderBar    from "../components/HeaderBar";
import ExerciseCard from "../components/ExerciseCard";
import Controls     from "../components/Controls";
import NavBar       from "@/components/organisms/NavBar/NavBar";
import Footer       from "@/components/organisms/Footer/Footer";
import { fetchCourse, fetchThemes } from "@services/api";


export default function StudyPage() {
  const { courseId, subjectId } = useParams<{courseId:string;subjectId:string}>();
  const navigate = useNavigate();
  const { exercise, loading, error, checked, isCorrect, generate, check } = useExercise();

  const [course, setCourse]   = useState<any>(null);
  const [subject, setSubject] = useState<any>(null);
  const [themes, setThemes]   = useState<any[]>([]);
  const [theme, setTheme]     = useState<any|null>(null);
  const [difficulty, setDifficulty] = useState("fácil");
  const [answer, setAnswer]   = useState("");

  useEffect(() => {
    if (!courseId||!subjectId) return;
    fetchCourse(+courseId)
      .then(c => {
        setCourse(c);
        setSubject(c.subjects.find((s:any)=>s.id===+subjectId) || null);
      })
      .catch(() => navigate("/error", { replace:true }));
  }, [courseId, subjectId, navigate]);

  useEffect(() => {
    if (!subject) return;
    fetchThemes(subject.id).then(setThemes);
  }, [subject]);

  const onGenerate = () => {
    if (!theme) return;
    const body = {
      model: "profesor",
      response_format: { type: "json_object" },
      messages: [
        { role:"user", content:`Genera un ejercicio sobre "${theme.title}" en dificultad ${difficulty}` }
      ]
    };
    generate(body);
    setAnswer("");
  };

  return (
    <div style={{ display:"flex", flexDirection:"column", minHeight:"100vh" }}>
      <NavBar/>
      {course && subject && (
        <main style={{ flex:1, padding:"2rem" }}>
          <HeaderBar 
            course={course} subject={subject}
            difficulty={difficulty}
            onDifficultyChange={setDifficulty}
          />

          <div style={{ textAlign:"center", margin:"2rem 0" }}>
            <select
              value={theme?.id||""}
              onChange={e => {
                const t = themes.find(t=>t.id===+e.target.value);
                setTheme(t||null);
              }}
            >
              <option value="">Selecciona tema…</option>
              {themes.map(t=>(
                <option key={t.id} value={t.id}>{t.title}</option>
              ))}
            </select>
            {!exercise && theme && (
              <button onClick={onGenerate} disabled={loading}>
                {loading ? "Generando…" : "Generar pregunta"}
              </button>
            )}
          </div>

          {error && <p style={{ color:"red" }}>{error}</p>}

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
      <Footer/>
    </div>
  );
}
