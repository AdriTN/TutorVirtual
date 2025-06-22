import { useQuery }      from "@tanstack/react-query";
import { getStatsByTheme } from "@services/api/endpoints/stats";
import { ThemeStat } from "@types";

export const useStatsTheme = () =>
  useQuery<ThemeStat[]>({
    queryKey: ["stats", "theme"],
    queryFn : getStatsByTheme,
  });
