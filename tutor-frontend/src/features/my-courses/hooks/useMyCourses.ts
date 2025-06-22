import { useQuery }      from "@tanstack/react-query";
import { fetchMyCourses }     from "@services/api/endpoints/courses";


export const useMyCourses = () => {
  return useQuery({
    staleTime: 0,
    queryKey: ["my-courses"],
    queryFn: () => fetchMyCourses(),
    refetchOnWindowFocus: false,
  });
};
