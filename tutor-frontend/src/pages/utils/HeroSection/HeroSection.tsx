import React from "react";
import styles from "./HeroSection.module.css";

interface HeroSectionProps {
  title: string;
  subtitle: string;
  imageUrl?: string;
  onButtonClick?: () => void;
}


const HeroSection: React.FC<HeroSectionProps> = ({
  title,
  subtitle,
  imageUrl,
  onButtonClick,
}) => {
  return (
    <section className={styles.hero}>
      <div className={styles.heroText}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.subtitle}>{subtitle}</p>
        <button className={styles.animatedbutton} onClick={onButtonClick}>
        <svg viewBox="0 0 24 24" className={styles.arr2}>
          <path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z" />
        </svg>
        <span className={styles.text}>Comenzar Ahora</span>
        <span className={styles.circle} />
        <svg viewBox="0 0 24 24" className={styles.arr1}>
          <path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z" />
        </svg>
        </button>
      </div>
      {imageUrl && (
        <div className={styles.heroImage}>
          <img src={imageUrl} alt="Hero" />
        </div>
      )}
    </section>
  );
};

export default HeroSection;
