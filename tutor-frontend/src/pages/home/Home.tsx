import React from "react";
import NavBar from "../utils/NavBar/NavBar";
import HeroSection from "../utils/HeroSection/HeroSection";
import HowItWorksSection from "../utils/HowItWorksSection/HowItWorksSection";
import BenefitsSection from "../utils/BenefitsSection/BenefitsSection";
import Footer from "../utils/Footer/Footer";

const HomePage: React.FC = () => {
  const handleHeroButtonClick = () => {
    alert("¡Funcionalidad próximamente!");
  };

  return (
    <>
      <NavBar/>

      <HeroSection
        title="Tu Tutor Inteligente."
        subtitle="Combina el poder de la inteligencia artificial con métodos de enseñanza personalizados. Aprende lo que quieras, cuando quieras, con una experiencia adaptada a tu nivel, ritmo y estilo. Di adiós al aprendizaje genérico y empieza a avanzar de verdad."
        imageUrl="/tutor-hero.png"
        onButtonClick={handleHeroButtonClick}
      />
      <HowItWorksSection />

      <BenefitsSection />

      <Footer />
    </>
    
  );
};

export default HomePage;
