import { api } from "../backend";
import { StatsOverview, StatsDaily, ThemeStat } from "@/types";

export const getStatsOverview = ()       => api.get<StatsOverview>("/api/stats/overview").then(r => r.data);
export const getStatsTimeline = ()       => api.get<StatsDaily[]>("/api/stats/timeline").then(r => r.data);
export const getStatsByTheme  = ()       => api.get<ThemeStat[]>("/api/stats/by-theme").then(r => r.data);
