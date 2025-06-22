import { useForm } from "react-hook-form";
import { useLoginMutation } from "../../../hooks/useLoginMutation";
import { useAuth } from "@context/auth/AuthContext";
import styles from "./LoginForm.module.css";

type FormValues = { email: string; password: string };

const LoginForm: React.FC = () => {
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>();
  const mutation = useLoginMutation();

  const onSubmit = async (data: FormValues) => {
    try {
      const tokens = await mutation.mutateAsync(data);
      login(tokens.access_token, tokens.refresh_token);
    } catch (err) {
      alert("Credenciales incorrectas");
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
      <h2 className={styles.title}>Iniciar sesión</h2>

      <label className={styles.field}>
        <span>Email</span>
        <input
          type="email"
          {...register("email", { required: "Obligatorio" })}
        />
        {errors.email && <small>{errors.email.message}</small>}
      </label>

      <label className={styles.field}>
        <span>Contraseña</span>
        <input
          type="password"
          {...register("password", { required: "Obligatorio" })}
        />
        {errors.password && <small>{errors.password.message}</small>}
      </label>

      <button
        type="submit"
        className={styles.btn}
        disabled={mutation.isPending}
      >
        {mutation.isPending ? "Entrando…" : "Entrar"}
      </button>
    </form>
  );
};

export default LoginForm;
