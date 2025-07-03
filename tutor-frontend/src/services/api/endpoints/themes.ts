import { Theme } from "@/types";
import { api } from "../backend";

export const adminCreateTheme = (name: string, description: string, subjectId: number) =>
  api.post("/api/themes", { name: name, description: description, subject_id: subjectId });

export const adminAddThemeToSubject = (subjectId: number, themeId: number) =>
  api.post(`/api/themes/subject/${subjectId}/add`, { theme_id: themeId });

/* editar (name / description / mover a otra asignatura) */
export const adminUpdateTheme = (
  themeId: number,
  payload: {
    name?: string;
    description?: string;
    subject_id?: number;
  }
) => api.put(`/api/themes/${themeId}`, payload);

/* eliminar */
export const adminDeleteTheme = (themeId: number) =>
  api.delete(`/api/themes/${themeId}`);

/* mover un tema a otra asignatura: adminUpdateTheme(themeId,{subject_id:nuevoId}) */

/* ---------- query pública (ya existente) ---------- */
export const fetchThemes = (subjectId: number) =>
  api.get<Theme[]>(`/api/subjects/${subjectId}/themes`).then(r => r.data);

export const getAllThemes = () =>
  api.get<Theme[]>("/api/themes").then(r => r.data);
