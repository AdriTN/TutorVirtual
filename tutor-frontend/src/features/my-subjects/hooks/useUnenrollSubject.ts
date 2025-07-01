import { useMutation, useQueryClient } from "@tanstack/react-query";
import { unenrollSubject }             from "@services/api/endpoints/subjects";
import { useNotifications }            from "@hooks/useNotifications";

export const useUnenrollSubject = (courseId: number) => {
  const qc = useQueryClient();
  const { notifySuccess } = useNotifications();

  return useMutation<void, Error, number>({ 
    mutationFn: async (subjectId: number) => {
      await unenrollSubject(subjectId, courseId); 
    },
    onSuccess : () => {
      qc.invalidateQueries({ queryKey: ["my-course", courseId] });
      qc.invalidateQueries({ queryKey: ["my-courses"] });
      qc.invalidateQueries({ queryKey: ["courses/all"] });
      qc.invalidateQueries({ queryKey: ["my-subjects"] }); 
      notifySuccess("Te has desmatriculado de la asignatura correctamente.");
    },
    onError: (error) => {
      console.error("Error al desmatricular la asignatura:", error);
    }
  });
};
