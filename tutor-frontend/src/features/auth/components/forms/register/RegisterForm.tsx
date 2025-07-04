import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@services/api/backend";
import { useNotifications } from "@hooks/useNotifications";
import styles from "./RegisterForm.module.css";

interface Props {
  endpointUrl?: string;
}

const RegisterForm = ({ endpointUrl = "/api/auth/register" }: Props) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [pwd2, setPwd2] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const [nameError, setNameError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [pwdError, setPwdError] = useState("");
  const [pwd2Error, setPwd2Error] = useState("");
  const [agreedError, setAgreedError] = useState("");

  const navigate = useNavigate();
  const { notifyError, notifySuccess } = useNotifications();

  const validateForm = () => {
    let isValid = true;
    setNameError("");
    setEmailError("");
    setPwdError("");
    setPwd2Error("");
    setAgreedError("");

    if (name.trim().length < 3) {
      setNameError("El nombre de usuario debe tener al menos 3 caracteres.");
      isValid = false;
    }

    if (!email) {
      setEmailError("El correo electrónico es obligatorio.");
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError("El formato del correo electrónico no es válido.");
      isValid = false;
    }

    if (pwd.length < 8) {
      setPwdError("La contraseña debe tener al menos 8 caracteres.");
      isValid = false;
    } else {
      let errorParts = [];
      if (!/[a-z]/.test(pwd)) errorParts.push("minúscula");
      if (!/[A-Z]/.test(pwd)) errorParts.push("mayúscula");
      if (!/\d/.test(pwd)) errorParts.push("dígito");
      if (!/[^a-zA-Z0-9]/.test(pwd)) errorParts.push("símbolo");
      
      if (errorParts.length > 0) {
        setPwdError(`La contraseña debe incluir al menos una ${errorParts.join(", ")}.`);
        isValid = false;
      }
    }
    

    if (pwd !== pwd2) {
      setPwd2Error("Las contraseñas no coinciden.");
      isValid = false;
    }
     if (!pwd2 && !pwdError && isValid) {
      setPwd2Error("Por favor, confirma la contraseña.");
      isValid = false;
    }


    if (!agreed) {
      setAgreedError("Debes aceptar los términos y condiciones.");
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      await api.post(endpointUrl, {
        username: name.trim(),
        email,
        password: pwd,
        confirm_password: pwd2,
      });
      notifySuccess("¡Registro exitoso! Ahora puedes iniciar sesión.");
      navigate("/login", { replace: true });
    } catch (error: any) {
      if (error?.response?.status === 422) {
        const errorDetails = error?.response?.data?.detail;
        if (Array.isArray(errorDetails)) {
          errorDetails.forEach((err: { loc: string[], msg: string }) => {
            if (err.loc.includes("username")) setNameError(err.msg);
            else if (err.loc.includes("email")) setEmailError(err.msg);
            else if (err.loc.includes("password")) setPwdError(err.msg);
            else notifyError(err.msg); 
          });
        } else if (typeof errorDetails === 'string') {
           notifyError(errorDetails);
        }else {
          notifyError("Error de validación. Revisa los datos e inténtalo de nuevo.");
        }
      } else if (error?.response?.status === 409) {
        notifyError(error?.response?.data?.detail || "El usuario o email ya está registrado.");
      }
       else {
        notifyError("Error inesperado en el registro. Por favor, inténtalo más tarde.");
      }
      console.error("Error en registro:", error?.response?.data || error?.message || error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <h1 className={styles.title}>Crear cuenta</h1>

      <input
        className={`${styles.input} ${nameError ? styles.inputError : ""}`}
        type="text"
        placeholder="Nombre de usuario"
        autoComplete="username"
        value={name}
        onChange={e => { setName(e.target.value); setNameError(""); }}
        required
      />
      {nameError && <p className={styles.errorMessage}>{nameError}</p>}

      <input
        className={`${styles.input} ${emailError ? styles.inputError : ""}`}
        type="email"
        placeholder="Correo electrónico"
        autoComplete="email"
        value={email}
        onChange={e => { setEmail(e.target.value); setEmailError(""); }}
        required
      />
      {emailError && <p className={styles.errorMessage}>{emailError}</p>}

      <input
        className={`${styles.input} ${pwdError ? styles.inputError : ""}`}
        type="password"
        placeholder="Contraseña"
        autoComplete="new-password"
        value={pwd}
        onChange={e => { setPwd(e.target.value); setPwdError(""); }}
        required
      />
      {pwdError && <p className={styles.errorMessage}>{pwdError}</p>}

      <input
        className={`${styles.input} ${pwd2Error ? styles.inputError : ""}`}
        type="password"
        placeholder="Repite la contraseña"
        autoComplete="new-password"
        value={pwd2}
        onChange={e => { setPwd2(e.target.value); setPwd2Error(""); }}
        required
      />
      {pwd2Error && <p className={styles.errorMessage}>{pwd2Error}</p>}

      <div className={styles.agreementWrapper}>
        <label className={styles.checkboxContainer}>
          <input type="checkbox" checked={agreed} onChange={(e) => { setAgreed(e.target.checked); setAgreedError(""); }}/>
          <div className={styles.checkmark} />
          <span className={styles.checkboxLabel}>
            Estoy de acuerdo con <a href="#">Terminos y Condiciones</a>
          </span>
        </label>
      </div>
      {agreedError && <p className={styles.errorMessageAgreed}>{agreedError}</p>}


      <button className={styles.submit} type="submit" disabled={loading}>
        {loading ? "Registrando…" : "Registrarse"}
      </button>
      
      <div className={styles.haveAccount}>
        <Link to="/login">Ya tengo cuenta</Link>
      </div>
    </form>
  );
};

export default RegisterForm;
