import { api } from "../backend";
import { Course } from "@/types";

/* CRUD + queries --------------------------------------------------------- */
export const adminCreateCourse = (title: string, description?: string) =>
  api.post("/api/courses", { title, description });

export const fetchCourses = () =>
  api.get<Course[]>("/api/courses/courses").then((r) => r.data);

export const fetchCourse = (id: number) =>
  api.get<Course>(`/api/courses/${id}`).then((r) => r.data);

export const fetchMyCourses = () =>
  api.get<Course[]>("/api/courses/my").then((r) => r.data);

export const unenrollCourse = (courseId: number) =>
  api.delete(`/api/courses/${courseId}/unenroll`);
