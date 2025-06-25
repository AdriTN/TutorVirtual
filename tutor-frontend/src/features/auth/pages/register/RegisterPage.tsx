import RegisterForm from "../../components/forms/register/RegisterForm";
import MyGoogleButton from "../../components/buttons/google/MyGoogleButton";
import styles from "./Register.module.css";

const RegisterPage: React.FC = () => (
  <div className={styles.pageContainer}>
    <RegisterForm />
    <MyGoogleButton  />
  </div>
);

export default RegisterPage;
