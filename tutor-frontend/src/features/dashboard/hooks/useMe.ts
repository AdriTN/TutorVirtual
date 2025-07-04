import { useQuery } from "@tanstack/react-query";
import { api }      from "@services/api";
import { useAuth }  from "@context/auth/AuthContext";
import type { UserData } from "@context/auth/auth.types";

export interface Me {
  id: number;
  username: string;
  email: string;
}

export const useMe = () => {
  const { user: authUser } = useAuth();

  return useQuery<Me, Error>({
    queryKey: ["me"],
    queryFn: () => api.get<Me>("/api/users/me").then(r => r.data),

    initialData: authUser ? (authUser as UserData as Me) : undefined,
    // enabled: !authLoading && (authUser ? someConditionToRefetch : true) // Más control si se necesita
  });
};
