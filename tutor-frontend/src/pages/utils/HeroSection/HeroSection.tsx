import React from "react";
import styles from "./HeroSection.module.css";

interface HeroSectionProps {
  title: string;
  subtitle: string;
  buttonLabel: string;
  imageUrl?: string;
  onButtonClick?: () => void;
}

/**
 * HeroSection es un componente reutilizable 
 * con título, subtítulo, botón y una imagen opcional.
 */
const HeroSection: React.FC<HeroSectionProps> = ({
  title,
  subtitle,
  buttonLabel,
  imageUrl,
  onButtonClick,
}) => {
  return (
    <div className={styles.hero}>
      <div className={styles.heroText}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.subtitle}>{subtitle}</p>
        <button className={styles.ctaButton} onClick={onButtonClick}>
          {buttonLabel}
        </button>
      </div>
      {imageUrl && (
        <div className={styles.heroImage}>
          <img src={imageUrl} alt="Hero" />
        </div>
      )}
    </div>
  );
};

export default HeroSection;
