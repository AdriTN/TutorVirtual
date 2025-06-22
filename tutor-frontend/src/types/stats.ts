export interface StatsOverview {
    hechos: number;
    correctos: number;
    porcentaje: number;
    trend24h: string;
  }
  
  export interface StatsDaily {
    date: string;
    correctRatio: number;
  }
  
  export interface ThemeStat {
    theme_id: number;
    theme: string;
    done: number;
    correct: number;
    ratio: number;
  }
  