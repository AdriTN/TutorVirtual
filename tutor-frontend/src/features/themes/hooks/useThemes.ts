import { useQuery } from "@tanstack/react-query";
import { fetchThemes } from "@services/api";

export const useThemes = (subjectId: number | undefined) =>
  useQuery({
    queryKey : ["themes", subjectId],
    queryFn  : () => fetchThemes(subjectId!),
    enabled  : !!subjectId,
  });
