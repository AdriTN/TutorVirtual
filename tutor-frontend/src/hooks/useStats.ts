import { useQuery } from "@tanstack/react-query";
import { getStatsOverview } from "../utils/enrollment";

export const useStats = () =>
  useQuery({ queryKey: ["stats", "overview"], queryFn: getStatsOverview });
