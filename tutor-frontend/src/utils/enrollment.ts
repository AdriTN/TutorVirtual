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

export interface AIExercise {
  tema: string;
  enunciado: string;
  respuesta: string;
  dificultad: string;
  tipo: string;
  explicacion: string;
}

/* ---------------- API helpers ---------------- */

/* Cursos */

export const fetchCourses = () =>
  api.get<Course[]>("/api/course/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/course/${id}`).then((r) => r.data);

export const fetchMyCourses = () =>
  api.get<Course[]>("/api/course/my").then((r) => r.data);

export const unenrollCourse = (courseId: number) =>
  api.delete(`/api/course/${courseId}/unenroll`);

export const adminCreateCourse = (title: string, description?: string) =>
  api.post("/api/course/create", { title, description });

/* Asignaturas */
export const enrollSubject = (id: number) =>
  api.post(`/api/subject/${id}/enroll`);

export const unenrollSubject = (subjectId: number) =>
  api.delete(`/api/subject/${subjectId}/unenroll`);

export const adminCreateSubject = (name: string, description: string) =>
  api.post("/api/subject/nueva", { name, description });

export const adminAddSubjectToCourse = (courseId: number, subjectId: number) =>
  api.post(`/api/subject/${courseId}/subjects`, { subject_id: subjectId });

export const adminRemoveSubjectFromCourse = (courseId: number, subjectId: number) =>
  api.delete(`/api/subject/${courseId}/subjects/${subjectId}`);

/* Temas */
export const fetchThemes = (subjectId: number) =>
  api.get<Theme[]>(`/api/subject/${subjectId}/themes`).then((r) => r.data);

export const adminCreateTheme = (
  nombre: string,
  descripcion: string,
  subjectId: number
) => api.post("/api/theme/new", { nombre, descripcion, subject_id: subjectId });

export const adminAddThemeToSubject = (subjectId: number, themeId: number) =>
  api.post(`/api/theme/subject/${subjectId}/add`, { theme_id: themeId });

/* IA */
export const fetchAIQuestion = (body: AIRequest) =>
  api.post<AIExercise>("/api/ai/ask", body).then(r => r.data);

/* Opciones de selector (listar) --------------------------------- */
export const listAllCourses   = () => api.get("/api/course/courses");
export const listAllSubjects  = () => api.get("/api/subject/subjects");
export const listThemesBySubj = (subjId: number) =>
  api.get(`/api/subject/${subjId}/themes`);