import axios from "axios";

/* helpers para sessionStorage */
export const getAccessToken  = () => sessionStorage.getItem("accessToken");
export const setAccessToken  = (t: string) => sessionStorage.setItem("accessToken", t);
export const getRefreshToken = () => sessionStorage.getItem("refreshToken");
export const setRefreshToken = (t: string) => sessionStorage.setItem("refreshToken", t);

/* refresca el access-token usando el refresh-token almacenado */
export const refreshAccessToken = async (): Promise<boolean> => {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  try {
    const { data } = await axios.post("/api/refresh", { refresh_token: refresh });
    setAccessToken(data.new_access_token);
    if (data.new_refresh_token) setRefreshToken(data.new_refresh_token);
    return true;
  } catch {
    return false;
  }
};
