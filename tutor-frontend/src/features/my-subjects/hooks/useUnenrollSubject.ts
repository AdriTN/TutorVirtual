import { useMutation, useQueryClient } from "@tanstack/react-query";
import { unenrollSubject }             from "@services/api/endpoints/subjects";

export const useUnenrollSubject = (courseId: number) => {
  const qc = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: async (subjectId) => {
      await unenrollSubject(subjectId);
    },
    onSuccess : () => {
      qc.invalidateQueries({ queryKey: ["my-course", courseId] });
    },
  });
};
