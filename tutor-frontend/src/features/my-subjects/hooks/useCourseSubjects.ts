import { useQuery }  from "@tanstack/react-query";
import { fetchCourse } from "@services/api/endpoints/courses";


export const useCourseSubjects = (courseId: number) =>
    useQuery({
    staleTime : 0,
    queryKey : ["my-course", courseId],
    enabled  : Number.isFinite(courseId) && courseId > 0,
    queryFn  : () => fetchCourse(courseId!),
    })
