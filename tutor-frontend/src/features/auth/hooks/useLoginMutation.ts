import { useMutation } from "@tanstack/react-query";
import { loginUser, TokenPair } from "@services/api";


export const useLoginMutation = () => {
  return useMutation<TokenPair, Error, { email: string; password: string }>(
    {
      mutationFn: async ({ email, password }: { email: string; password: string }): Promise<TokenPair> => {
        const response = await loginUser(email, password);
        return response as TokenPair;
      },
      onError: (error) => {
        console.error("Login failed:", error);
      },
    }
  );
}
