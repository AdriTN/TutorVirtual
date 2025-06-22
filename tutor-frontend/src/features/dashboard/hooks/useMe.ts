import { useQuery } from "@tanstack/react-query";
import { api }       from "@services/api";

export interface Me {
  id: number;
  username: string;
  email: string;
}

export const useMe = () =>
  useQuery({
    queryKey: ["me"],
    queryFn : () => api.get<Me>("/api/users/me").then(r => r.data),
  });
