import { useQuery }      from "@tanstack/react-query";
import { getStatsTimeline } from "@services/api/endpoints/stats";
import { StatsDaily } from "@types";

export const useStatsTimeline = () =>
  useQuery<StatsDaily[]>({
    queryKey: ["stats", "daily"],
    queryFn : getStatsTimeline,
  });
