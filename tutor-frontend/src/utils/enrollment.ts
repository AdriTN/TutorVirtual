import { api } from "../services/apis/backend-api/api";


export interface Theme {
  id: number;
  title: string;
  description?: string;
}

export interface Subject {
  id: number;
  name: string;
  description?: string;
  enrolled: boolean;
  themes : Theme[];
}

export interface Course {
  id: number;
  title: string;
  description?: string | null;
  subjects: Subject[];
}

export interface AIRequest {
  model: string;
  response_format: { type: string };
  messages: { role: string; content: string }[];
}

export interface AIResponse {
  content: string;
}

export interface AIExerciseOut {
  id: number;
  tema: string;
  enunciado: string;
  dificultad: string;
  tipo: string;
  explicacion: string;
}

export interface AnswerOut {
    correcto: boolean;
}

export interface StatsOverview {
  hechos: number;
  correctos: number;
  porcentaje: number;
  trend24h: string;
}

export interface StatsDaily { 
  date:string; 
  correctRatio:number;
}
export interface ThemeStat { 
  theme_id:number; 
  theme:string; 
  done:number; 
  correct:number; 
  ratio:number; 
}

/* ---------------- API helpers ---------------- */

/* Cursos */

export const fetchCourses = () =>
  api.get<Course[]>("/api/courses/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/courses/${id}`).then((r) => r.data);

export const fetchMyCourses = () =>
  api.get<Course[]>("/api/courses/my").then((r) => r.data);

export const unenrollCourse = (courseId: number) =>
  api.delete(`/api/courses/${courseId}/unenroll`);

export const adminCreateCourse = (title: string, description?: string) =>
  api.post("/api/courses/create", { title, description });

/* Asignaturas */
export const enrollSubject = (id: number) =>
  api.post(`/api/subjects/${id}/enroll`);

export const unenrollSubject = (subjectId: number) =>
  api.delete(`/api/subjects/${subjectId}/unenroll`);

export const adminCreateSubject = (name: string, description: string) =>
  api.post("/api/subjects/nueva", { name, description });

export const adminAddSubjectToCourse = (courseId: number, subjectId: number) =>
  api.post(`/api/subjects/${courseId}/subjects`, { subject_id: subjectId });

export const adminRemoveSubjectFromCourse = (courseId: number, subjectId: number) =>
  api.delete(`/api/subjects/${courseId}/subjects/${subjectId}`);

/* Temas */
export const fetchThemes = (subjectId: number) =>
  api.get<Theme[]>(`/api/subjects/${subjectId}/themes`).then((r) => r.data);

export const adminCreateTheme = (
  nombre: string,
  descripcion: string,
  subjectId: number
) => api.post("/api/themes/new", { nombre, descripcion, subject_id: subjectId });

export const adminAddThemeToSubject = (subjectId: number, themeId: number) =>
  api.post(`/api/themes/subject/${subjectId}/add`, { theme_id: themeId });

/* IA */
export const askAI = (body:AIRequest)=>api.post<AIExerciseOut>("/api/ai/request", body).then(r=>r.data);

/* Respuestas */
export const sendAnswer = (
  ejercicio_id: number,
  answer: string,
  tiempo_seg?: number
) =>
  api
    .post<AnswerOut>("/api/answer", { ejercicio_id, answer, tiempo_seg })
    .then((r) => r.data);

/* Estadísticas */
export const getStatsOverview = () =>
  api.get<StatsOverview>("/api/stats/overview").then((r) => r.data);

export const getStatsTimeline = () =>
  api.get<StatsDaily[]>("/api/stats/timeline").then(r=>r.data);

export const getStatsByTheme = () =>
  api.get<ThemeStat[]>("/api/stats/by-theme").then(r=>r.data);

/* Opciones de selector (listar) --------------------------------- */
export const listAllCourses   = () => api.get("/api/courses/courses");
export const listAllSubjects  = () => api.get("/api/subjects/subjects");
export const listThemesBySubj = (subjId: number) =>
  api.get(`/api/subjects/${subjId}/themes`);