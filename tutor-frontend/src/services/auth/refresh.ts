import { api } from "@/services/api/backend";
import {
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "./tokens";


export const refreshAccessToken = async (): Promise<boolean> => {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  try {
    const { data } = await api.post("/api/auth/refresh", { refresh_token: refresh });

    setAccessToken(data.access_token);
    if (data.refresh_token) setRefreshToken(data.refresh_token);

    return true;
  } catch (err) {
    return false;
  }
};
