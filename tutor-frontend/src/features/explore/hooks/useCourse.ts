import { useQuery }       from "@tanstack/react-query";
import { fetchCourse }    from "@/services/api";

export const useCourse = (id: number | undefined) =>
  useQuery({
    staleTime:0,
    queryKey: ["courses", id],
    queryFn : () => fetchCourse(id!),
    enabled : !!id,
  });
