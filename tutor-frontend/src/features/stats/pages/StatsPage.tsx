import { format } from "date-fns";
import { Line, Doughnut } from "react-chartjs-2";
import "chart.js/auto";

import NavBar  from "@components/organisms/NavBar/NavBar";
import Footer  from "@components/organisms/Footer/Footer";

import { useStatsOverview }  from "../hooks/useStatsOverview";
import { useStatsTimeline }  from "../hooks/useStatsTimeline";
import { useStatsTheme }     from "../hooks/useStatsByTheme";

import StatCard  from "../components/StatCard/StatCard";
import styles    from "./StatsPage.module.css";

const n = (x: number) => x.toLocaleString("es-ES");

const StatsPage: React.FC = () => {

  /* ---------- queries ---------- */
  const { data: ovw }      = useStatsOverview();
  const { data: timeline } = useStatsTimeline();
  const { data: byTheme }  = useStatsTheme();

  /* ---------- loader ---------- */
  if (!ovw || !timeline || !byTheme) {
    return (
      <>
        <NavBar />
        <div className={styles.page}>
          <main className={styles.loading}>Cargando estadísticas…</main>
          <Footer />
        </div>
      </>
    );
  }

  /* ---------- datasets ---------- */
  const lineData = {
    labels  : timeline.map(t => format(new Date(t.date), "dd/MM")),
    datasets: [{ data: timeline.map(t => t.correctRatio), tension: .3 }],
  };

  const donutData = {
    labels  : ["Correctas", "Fallos"],
    datasets: [{ data: [ovw.correctos, ovw.hechos - ovw.correctos] }],
  };

  /* ---------- render ---------- */
  return (
    <>
      <NavBar />

      {/* wrapper que empuja el footer al fondo */}
      <div className={styles.page}>
        <main className={styles.container}>
          {/* cabecera */}
          <header className={styles.headerRow}>
            <h2 className={styles.heading}>Estadísticas globales</h2>
          </header>

          {/* KPI cards */}
          <section className={styles.gridCards}>
            <StatCard title="Ejercicios hechos" value={n(ovw.hechos)} />
            <StatCard title="Aciertos"          value={n(ovw.correctos)} />
            <StatCard
              title="Precisión"
              value={`${ovw.porcentaje.toFixed(1)} %`}
              trend={parseFloat(ovw.trend24h)}
            />
          </section>

          {/* Evolución diaria */}
          <section className={styles.block}>
            <h4>Evolución diaria</h4>
            {timeline.length
              ? <Line data={lineData} />
              : <p className={styles.empty}>No hay datos aún.</p>}
          </section>

          {/* Donut + tabla */}
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
                    <tr><th>Tema</th><th>Completados</th><th>Correctos</th><th>% Aciertos</th></tr>
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
                <p className={styles.empty}>No hay datos.</p>
              )}
            </div>
          </section>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default StatsPage;
