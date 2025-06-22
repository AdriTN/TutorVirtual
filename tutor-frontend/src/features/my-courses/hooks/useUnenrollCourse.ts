import { useMutation, useQueryClient } from "@tanstack/react-query";
import { unenrollCourse } from "@services/api/endpoints/courses";

export const useUnenrollCourse = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (courseId: number) =>
      unenrollCourse(courseId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-courses"] }),
  });
};
