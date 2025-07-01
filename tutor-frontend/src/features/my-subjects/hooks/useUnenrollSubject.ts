import { useMutation, useQueryClient } from "@tanstack/react-query";
import { unenrollSubject }             from "@services/api/endpoints/subjects";

export const useUnenrollSubject = (courseId: number) => {
  const qc = useQueryClient();

  return useMutation<void, Error, number>({ 
    mutationFn: async (subjectId: number) => {
      await unenrollSubject(subjectId, courseId); 
    },
    onSuccess : () => {
      qc.invalidateQueries({ queryKey: ["my-course", courseId] });
      qc.invalidateQueries({ queryKey: ["my-courses"] });
      qc.invalidateQueries({ queryKey: ["courses/all"] });
      qc.invalidateQueries({ queryKey: ["my-subjects"] }); 
    },
    onError: (error) => {
      console.error("Error al desmatricular la asignatura:", error);
    }
  });
};
