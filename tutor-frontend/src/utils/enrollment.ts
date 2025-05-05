import { api } from "../services/apis/backend-api/api";

export interface Subject {
  id: number;
  name: string;
}

export interface Course {
  id: number;
  title: string;
  description?: string | null;
  subjects: Subject[];
}

/* ---------------- API ---------------- */
export const fetchCourses = () =>
  api.get<Course[]>("/api/course/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/course/${id}`).then((r) => r.data);

export const enroll = (courseId: number, subjectId: number) =>
  api.post(`/api/course/${courseId}/enroll`, { subject_id: subjectId });
