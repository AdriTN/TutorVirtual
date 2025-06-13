/* eslint-disable react-hooks/exhaustive-deps */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { Line, Doughnut } from "react-chartjs-2";
import "chart.js/auto";

import NavBar   from "../utils/NavBar/NavBar";
import Footer   from "../utils/Footer/Footer";
import StatCard from "./StatCard/StatCard";
import styles   from "./StatsPage.module.css";

import {
  getStatsOverview,
  getStatsTimeline,
  getStatsByTheme,
  StatsOverview,
  StatsDaily,
  ThemeStat,
} from "../../utils/enrollment";

/* util seguro para separar miles */
const n = (x: number) => x.toLocaleString("es-ES");

const StatsPage: React.FC = () => {
  /* --- 1. Queries (siempre GLOBAL) ----------------------------- */
  const { data: ovw } = useQuery<StatsOverview>({
    queryKey: ["stats", "overview"],
    queryFn : () => getStatsOverview(),
  });

  const { data: timeline } = useQuery<StatsDaily[]>({
    queryKey: ["stats", "timeline"],
    queryFn : () => getStatsTimeline(),
  });

  const { data: byTheme } = useQuery<ThemeStat[]>({
    queryKey: ["stats", "by-theme"],
    queryFn : () => getStatsByTheme(),
  });

  /* loader mínimo */
  if (!ovw || !timeline || !byTheme) {
    return (
      <div className={styles.page}>
        <NavBar />
        <main className={styles.loading}>Cargando estadísticas…</main>
        <Footer />
      </div>
    );
  }

  /* --- 2. Datasets Chart.js ------------------------------------ */
  const lineData = {
    labels   : timeline.map(t => format(new Date(t.date), "dd/MM")),
    datasets : [{ data: timeline.map(t => t.correctRatio), tension: .3, fill: false }],
  };

  const donutData = {
    labels   : ["Correctas", "Fallos"],
    datasets : [{ data: [ovw.correctos, ovw.hechos - ovw.correctos] }],
  };

  /* --- 3. Render ------------------------------------------------ */
  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.container}>

        {/* ─── KPI cards ─────────────────────────────────── */}
        <section className={styles.gridCards}>
          <StatCard title="Ejercicios hechos" value={n(ovw.hechos)} />
          <StatCard title="Aciertos"          value={n(ovw.correctos)} />
          <StatCard
            title="Precisión"
            value={`${ovw.porcentaje.toFixed(1)} %`}
            trend={parseFloat(ovw.trend24h)}
          />
        </section>

        {/* ─── Evolución diaria ─────────────────────────── */}
        <section className={styles.block}>
          <h4>Evolución diaria</h4>
          {timeline.length ? <Line data={lineData} /> : <p>No hay datos aún.</p>}
        </section>

        {/* ─── Donut + tabla por tema ───────────────────── */}
        <section className={styles.blockGrid}>
          <div>
            <h4>Correctas vs Fallos</h4>
            <Doughnut data={donutData} />
          </div>

          <div className={styles.themeTableWrapper}>
            <h4>Progreso por tema</h4>
            {byTheme.length ? (
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Tema</th><th>Completados</th><th>Correctos</th><th>%</th>
                  </tr>
                </thead>
                <tbody>
                  {byTheme.map(t => (
                    <tr key={t.theme_id}>
                      <td>{t.theme}</td>
                      <td>{n(t.done)}</td>
                      <td>{n(t.correct)}</td>
                      <td>{t.ratio.toFixed(1)} %</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No hay datos.</p>
            )}
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
};

export default StatsPage;
