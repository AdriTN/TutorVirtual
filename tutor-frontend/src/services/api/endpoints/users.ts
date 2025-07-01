import { api } from "@services/api/backend";
import type { UserData } from "@context/auth/auth.types";


export const getUserMe = async (): Promise<UserData> => {
  const response = await api.get<UserData>("/api/users/me");
  return response.data;
};
