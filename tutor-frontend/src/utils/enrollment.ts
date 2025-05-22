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

/* Asignaturas */
export const enrollSubject = (id: number) =>
  api.post(`/api/subject/${id}/enroll`);

export const unenrollSubject = (subjectId: number) =>
  api.delete(`/api/subject/${subjectId}/unenroll`);

/* Temas */
export const fetchThemes = (subjectId: number) =>
  api.get<Theme[]>(`/api/subject/${subjectId}/themes`).then((r) => r.data);
