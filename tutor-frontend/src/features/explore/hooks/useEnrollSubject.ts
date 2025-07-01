import { useMutation, useQueryClient } from "@tanstack/react-query";
import { enrollSubject } from "@/services/api";
import { AxiosError } from "axios";


interface EnrollSubjectParams {
  subjectId: number;
  courseId: number;
}


export const useEnrollSubject = () => {
  const qc = useQueryClient();

  return useMutation<
    unknown,
    Error,
    EnrollSubjectParams
  >({
    mutationKey: ["enrollSubject"],
    mutationFn: (params: EnrollSubjectParams) =>
      enrollSubject(params.subjectId, params.courseId),

    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["my-courses"] });
    },
    onError: (error: Error) => {
      if (error instanceof AxiosError && error.response?.status === 409) {
        const detailMessage = error.response?.data?.detail;
        if (detailMessage) {
          error.message = detailMessage;
        }
      }
    },
  });
};