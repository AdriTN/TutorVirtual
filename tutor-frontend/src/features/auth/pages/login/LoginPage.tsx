import LoginForm      from "../../components/forms/login/LoginForm";
import MyGoogleButton from "../../components/buttons/google/MyGoogleButton";
import styles         from "./Login.module.css";

const LoginPage: React.FC = () => (
  <div className={styles.pageContainer}>
    <LoginForm />
    <MyGoogleButton />
  </div>
);

export default LoginPage;
