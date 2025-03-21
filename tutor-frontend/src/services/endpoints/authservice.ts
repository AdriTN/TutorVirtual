import { api } from "../apis/api";

export async function registerUser(username: string, email: string, password: string) {
    return await api.post("/api/register", {
        username,
        email,
        password,
    });
}