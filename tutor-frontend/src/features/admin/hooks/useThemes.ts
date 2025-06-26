import { useQuery } from "@tanstack/react-query";
import { fetchThemes, getAllThemes } from "@/services/api/endpoints/themes";


export const useThemes = (subjectId: number | undefined | null) =>
  useQuery({
    queryKey: ["themes", subjectId],
    queryFn:   () => fetchThemes(subjectId!),
    enabled:   !!subjectId,
    staleTime: 0,
  });

export const useAllThemes = () =>
  useQuery({
    staleTime:0,
    queryKey: ["all-themes"],
    queryFn:   () => getAllThemes(),
  });
