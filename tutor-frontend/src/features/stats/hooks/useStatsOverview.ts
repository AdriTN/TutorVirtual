import { useQuery }      from "@tanstack/react-query";
import { getStatsOverview } from "@services/api/endpoints/stats";
import { StatsOverview } from "@types";

export const useStatsOverview = () =>
  useQuery<StatsOverview>({
    queryKey: ["stats", "overview"],
    queryFn : getStatsOverview,
  });
