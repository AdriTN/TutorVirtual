/* Almacenamiento seguro en sessionStorage
   -------------------------------------------------------------- */
const ACCESS  = "accessToken";
const REFRESH = "refreshToken";
   
export const getAccessToken  = () => sessionStorage.getItem(ACCESS);
export const setAccessToken  = (t: string) => sessionStorage.setItem(ACCESS, t);
   
export const getRefreshToken = () => sessionStorage.getItem(REFRESH);
export const setRefreshToken = (t: string) => sessionStorage.setItem(REFRESH, t);
   
export const clearTokens = () => {
    sessionStorage.removeItem(ACCESS);
    sessionStorage.removeItem(REFRESH);
};
   