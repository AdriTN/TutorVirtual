import React from "react";
import RegisterForm from "../../components/register/Register";
import styles from "./RegisterPage.module.css";
import MyGoogleButton from "../../components/google/MyGoogleButton";

import.meta.env.VITE_API_URL;

const RegisterPage: React.FC = () => {
    const baseURL = import.meta.env.VITE_BACKEND_URL
    const registerEndpoint = `${baseURL}/api/register`;
    const googleRegisterEndpoint = `${baseURL}/api/google`;

  return (
    <div className={styles.pageContainer}>
      <RegisterForm endpointUrl={registerEndpoint} />

      <MyGoogleButton endpointUrl={googleRegisterEndpoint} />
    </div>
  );
};

export default RegisterPage;
