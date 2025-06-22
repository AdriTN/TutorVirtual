import { useQuery } from "@tanstack/react-query";
import { api }       from "@services/api";
import { Course } from "@types";

export const useMyCourses = () =>
  useQuery({
    staleTime: 0,
    queryKey: ["myCourses"],
    queryFn : () => api.get<Course[]>("/api/courses/my").then(r => r.data),
  });
