import { api } from "@services/api/backend";


export interface RegisterIn {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface TokenPair {
  access_token:  string;
  refresh_token: string;
}


export const registerUser = async (body: RegisterIn) =>
  api.post<TokenPair>("/api/auth/register", body).then(r => r.data);

export const loginUser = async (email: string, password: string) =>
  api.post<TokenPair>("/api/auth/login", { email, password }).then(r => r.data);

export const googleLogin = (token: string) =>
  api.post<TokenPair>("/api/auth/google", { token }).then(r => r.data);
