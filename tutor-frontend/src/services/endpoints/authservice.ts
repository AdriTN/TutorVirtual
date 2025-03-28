import { api } from "../apis/backend-api/api";

export async function registerUser(username: string, email: string, password: string, confirmPassword: string) {
    return await api.post("/api/register", {
        username,
        email,
        password,
        confirmPassword,
    });
}