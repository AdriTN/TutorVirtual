import React from "react";
import styles from "./StatCard.module.css";

interface Props {
  title:   string;
  value?:  number | string;
  trend?:  number;
  loading?: boolean;
  children?: React.ReactNode;
}

const StatCard: React.FC<Props> = ({ title, value, trend, loading, children }) => {
  return (
    <article className={styles.card}>
      <header>
        <span className={styles.title}>{title}</span>

        {trend !== undefined && !loading && (
          <span className={trend >= 0 ? styles.trendUp : styles.trendDown}>
            {trend > 0 ? "▲" : trend < 0 ? "▼" : "•"} {Math.abs(trend)}%
          </span>
        )}
      </header>

      <strong className={styles.value}>
        {loading ? <span className={styles.skeleton} /> : value}
      </strong>

      {children && <div className={styles.chart}>{children}</div>}
    </article>
  );
};

export default StatCard;
