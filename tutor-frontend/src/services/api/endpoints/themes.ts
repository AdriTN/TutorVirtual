import { Theme } from "@/types";
import { api } from "../backend";

export const adminCreateTheme = (title: string, description: string, subjectId: number) =>
  api.post("/api/themes/new", { nombre: title, descripcion: description, subject_id: subjectId });

export const adminAddThemeToSubject = (subjectId: number, themeId: number) =>
  api.post(`/api/themes/subject/${subjectId}/add`, { theme_id: themeId });

export const fetchThemes = (subjectId: number) =>
  api.get<Theme[]>(`/api/subjects/${subjectId}/themes`).then((r) => r.data);
