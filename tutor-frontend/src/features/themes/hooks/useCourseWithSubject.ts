import { useQuery } from "@tanstack/react-query";
import { fetchCourse } from "@services/api";

export const useCourseWithSubject = (courseId?: number) =>
  useQuery({
    queryKey : ["course", courseId],
    queryFn  : () => fetchCourse(courseId!),
    enabled  : !!courseId,
  });
