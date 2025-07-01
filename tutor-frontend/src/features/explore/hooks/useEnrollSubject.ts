import { useMutation, useQueryClient } from "@tanstack/react-query";
import { enrollSubject } from "@/services/api";

// Nuevo tipo para los parámetros de mutación
interface EnrollSubjectParams {
  subjectId: number;
  courseId: number;
}

export const useEnrollSubject = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationKey: ["enrollSubject"],
    mutationFn : (params: EnrollSubjectParams) =>
      enrollSubject(params.subjectId, params.courseId),

    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["my-courses"] });
    },
  });
};