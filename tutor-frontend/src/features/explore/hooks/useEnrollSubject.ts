import { useQuery } from "@tanstack/react-query";
import { enrollSubject }               from "@/services/api";



export const useEnrollSubject = () =>
  useQuery({ 
    staleTime:0,
    queryKey: ["courses/all"], queryFn: ({ queryKey }) => {
      const subjectId = queryKey[1] as unknown as number;
      return enrollSubject(subjectId);
    },
  });
