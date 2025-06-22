import { useQuery } from "@tanstack/react-query";
import { fetchThemes } from "@/services/api/endpoints/themes";


export const useThemes = (subjectId: number | undefined | null) =>
  useQuery({
    queryKey: ["themes", subjectId],
    queryFn:   () => fetchThemes(subjectId!),
    enabled:   !!subjectId,
    staleTime: 1000 * 60 * 5,
  });
