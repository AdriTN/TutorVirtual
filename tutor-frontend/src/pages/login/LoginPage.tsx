import React from "react";
import LoginForm from "../../components/login/Login"; // Asegúrate de que la ruta y nombre del componente sean correctos
import styles from "./LoginPage.module.css";
import MyGoogleButton from "../../components/google/MyGoogleButton";

const LoginPage: React.FC = () => {
  const baseURL = import.meta.env.VITE_BACKEND_URL;
  const loginEndpoint = `${baseURL}/api/login`;
  const googleLoginEndpoint = `${baseURL}/api/google`;

  return (
    <div className={styles.pageContainer}>
      <LoginForm endpointUrl={loginEndpoint} />
      <MyGoogleButton endpointUrl={googleLoginEndpoint} />
    </div>
  );
};

export default LoginPage;
