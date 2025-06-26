import { api } from "../backend";
import { Course } from "@/types";

/* CRUD + queries --------------------------------------------------------- */
export const fetchCourses = () =>
  api.get<Course[]>("/api/courses/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/courses/${id}`).then((r) => r.data);

export const fetchMyCourses = () =>
  api.get<Course[]>("/api/courses/my").then((r) => r.data);

export const unenrollCourse = (courseId: number) =>
  api.delete(`/api/courses/${courseId}/unenroll`);

/* ---------- Administración ---------- */
export const adminCreateCourse = (title: string, description?: string) =>
  api.post("/api/courses", { title, description });

/* editar (title / description / subject_ids opcional) */
export const adminUpdateCourse = (
  courseId: number,
  payload: { title?: string; description?: string; subject_ids?: number[] }
) => api.put(`/api/courses/${courseId}`, payload);

/* eliminar */
export const adminDeleteCourse = (courseId: number) =>
  api.delete(`/api/courses/${courseId}`);

/* desvincular varias asignaturas de un curso */
export const adminDetachSubjectsFromCourse = (
  courseId: number,
  subjectIds: number[]
) =>
  api.delete(`/api/courses/${courseId}/subjects`, {
    data: { subject_ids: subjectIds },
  });
