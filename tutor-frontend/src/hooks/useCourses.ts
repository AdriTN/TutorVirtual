import { useQuery } from "@tanstack/react-query";
import { listAllCourses } from "../utils/enrollment";

export const useCourses = () =>
  useQuery({ queryKey: ["courses"], queryFn: listAllCourses });
