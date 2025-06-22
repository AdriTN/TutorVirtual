import { api } from "../backend";
import { Subject, Theme } from "@/types";

/* ------- subjects ------------------------------------------------------- */
export const getAllSubjects = () => api.get<Subject[]>("/api/subjects/subjects").then(r => r.data);
export const enrollSubject   = (id: number) => api.post(`/api/subjects/${id}/enroll`);
export const unenrolSubject = (id: number) => api.delete(`/api/subjects/${id}/unenroll`);

export const adminCreateSubject = (name: string, description = "") =>
  api.post("/api/subjects/nueva", { name, description });

export const adminAddSubjectToCourse    = (courseId: number, subjId: number) =>
  api.post(`/api/subjects/${courseId}/subjects`, { subject_id: subjId });

export const adminRemoveSubjectFromCourse = (courseId: number, subjId: number) =>
  api.delete(`/api/subjects/${courseId}/subjects/${subjId}`);

/* ------- themes (vía subject) ------------------------------------------ */
export const getThemesBySubject = (subjectId: number) =>
  api.get<Theme[]>(`/api/subjects/${subjectId}/themes`).then(r => r.data);
