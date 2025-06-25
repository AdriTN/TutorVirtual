import { useQuery } from "@tanstack/react-query";
import { getAllSubjects } from "@/services/api/endpoints/subjects";


export const useSubjects = () =>
  useQuery({
    queryKey: ["subjects"],
    queryFn:   getAllSubjects,
    staleTime: 1000 * 60 * 5,
  });
