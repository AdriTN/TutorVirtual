import { useMutation, useQueryClient } from "@tanstack/react-query";
import { unenrolSubject }             from "@services/api/endpoints/subjects";

export const useUnenrollSubject = (courseId: number) => {
  const qc = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: async (subjectId) => {
      await unenrolSubject(subjectId);
    },
    onSuccess : () => {
      qc.invalidateQueries({ queryKey: ["my-course", courseId] });
    },
  });
};
