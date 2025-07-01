import { api } from "../backend";
import { Subject, Theme } from "@/types";

const BASE = "/api/subjects";

/* ------------------------------------------------------------------ */
/*  Subjects (público / alumno)                                       */
/* ------------------------------------------------------------------ */
export const getAllSubjects = () =>
  api.get<Subject[]>(`${BASE}/all`).then(r => r.data);

export const enrollSubject = (subjectId: number, courseId: number) =>
  api.post(`${BASE}/${subjectId}/enroll`, { course_id: courseId });

export const unenrollSubject = (subjectId: number, courseId: number) =>
  api.delete(`${BASE}/${subjectId}/unenroll`, { data: { course_id: courseId } });

/* ------------------------------------------------------------------ */
/*  Themes de una asignatura                                          */
/* ------------------------------------------------------------------ */
export const getThemesBySubject = (subjectId: number) =>
  api
    .get<Theme[]>(`${BASE}/${subjectId}/themes`)
    .then(r => r.data);

/* ------------------------------------------------------------------ */
/*  Administración de asignaturas                                     */
/* ------------------------------------------------------------------ */
export const adminCreateSubject = (name: string, description = "") =>
  api.post(`${BASE}/create`, { name, description });

export const adminAddSubjectToCourse = (courseId: number, subjectId: number) =>
  api.post(`${BASE}/courses/${courseId}/subjects/add`, {
    subject_id: subjectId,
  });

export const adminRemoveSubjectFromCourse = (
  courseId: number,
  subjectId: number
) =>
  api.delete(
    `${BASE}/courses/${courseId}/subjects/${subjectId}/remove`
  );

/* editar (name / description) */
export const adminUpdateSubject = (
  subjectId: number,
  payload: { name?: string; description?: string }
) => api.put(`${BASE}/${subjectId}/update`, payload);

/* eliminar */
export const adminDeleteSubject = (subjectId: number) =>
  api.delete(`${BASE}/${subjectId}/delete`);

/* desvincular o eliminar varios temas de una asignatura */
export const adminDetachThemesFromSubject = (
  subjectId: number,
  themeIds: number[]
) =>
  api.delete(`${BASE}/${subjectId}/themes/detach`, {
    data: { theme_ids: themeIds },
  });
