import { useQuery }        from "@tanstack/react-query";
import { fetchCourses }    from "@/services/api";

export const useCourses = () =>
  useQuery({ 
    staleTime:0,
    queryKey: ["courses/all"], queryFn: fetchCourses 
  });
