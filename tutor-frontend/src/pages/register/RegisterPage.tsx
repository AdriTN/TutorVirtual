import React from "react";
import RegisterForm from "../../components/register/Register";
import styles from "./RegisterPage.module.css";

import.meta.env.VITE_API_URL;

const RegisterPage: React.FC = () => {
    const baseURL = import.meta.env.VITE_BACKEND_URL
    const registerEndpoint = `${baseURL}/api/register`;

  return (
    <div className={styles.pageContainer}>
      <RegisterForm endpointUrl={registerEndpoint} />
    </div>
  );
};

export default RegisterPage;
