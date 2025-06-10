import { useQuery } from "@tanstack/react-query";
import { listThemesBySubj } from "../utils/enrollment";

export const useThemes = (subjectId: string) =>
  useQuery({
    queryKey: ["themes", subjectId],
    queryFn: () => listThemesBySubj(Number(subjectId)),
    enabled: subjectId !== "",
  });
