import { useMutation, useQueryClient } from "@tanstack/react-query";
import { enrollSubject } from "@/services/api";

export const useEnrollSubject = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationKey: ["enrollSubject"],
    mutationFn : (subjectId: number) => enrollSubject(subjectId),

    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["my-courses"] });
    },
  });
};