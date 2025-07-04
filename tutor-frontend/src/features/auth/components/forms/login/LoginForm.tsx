import { useForm } from "react-hook-form";
import { useLoginMutation } from "../../../hooks/useLoginMutation";
import { useAuth } from "@context/auth/AuthContext";
import styles from "./LoginForm.module.css";
import { Link } from "react-router-dom";

type FormValues = { email: string; password: string };

const LoginForm: React.FC = () => {
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>();
  const mutation = useLoginMutation();

  const onSubmit = async (data: FormValues) => {
    const tokens = await mutation.mutateAsync(data);
    login(tokens.access_token, tokens.refresh_token);
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
      <h2 className={styles.title}>Iniciar sesión</h2>

      <label className={styles.field}>
        <input
          type="email"
          placeholder="Correo electrónico"
          autoComplete="email"
          {...register("email", { required: "Obligatorio" })}
        />
        {errors.email && <small>{errors.email.message}</small>}
      </label>

      <label className={styles.field}>
        <input
          type="password"
          placeholder="Contraseña"
          autoComplete="current-password"
          {...register("password", { required: "Obligatorio" })}
        />
        {errors.password && <small>{errors.password.message}</small>}
      </label>

      <button
        type="submit"
        className={styles.botons}
        disabled={mutation.isPending}
      >
        {mutation.isPending ? "Iniciando Sesión…" : "Iniciar Sesión"}
      </button>

      <div className={styles.haveAccount}>
        <Link to="/register">¿No tienes cuenta? Regístrate</Link>
      </div>
    </form>
  );
};

export default LoginForm;
