import { api } from "../services/apis/backend-api/api";

export interface Subject {
  id: number;
  name: string;
  description?: string;
  enrolled: boolean;
}

export interface Course {
  id: number;
  title: string;
  description?: string | null;
  subjects: Subject[];
}

/* ---------------- API helpers ---------------- */
export const fetchCourses = () =>
  api.get<Course[]>("/api/course/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/course/${id}`).then((r) => r.data);

export const enrollSubject = (id: number) =>
  api.post(`/api/subject/${id}/enroll`);

export const fetchMyCourses = () =>
  api.get<Course[]>("/api/course/my").then((r) => r.data);

export const unenrollCourse = (courseId: number) =>
  api.delete(`/api/course/${courseId}/unenroll`);

export const unenrollSubject = (subjectId: number) =>
  api.delete(`/api/subject/${subjectId}/unenroll`);
