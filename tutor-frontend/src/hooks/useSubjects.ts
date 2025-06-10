import { useQuery } from "@tanstack/react-query";
import { listAllSubjects } from "../utils/enrollment";

export const useSubjects = () =>
  useQuery({ queryKey: ["subjects"], queryFn: listAllSubjects });
