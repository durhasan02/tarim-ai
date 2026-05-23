import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { authApi } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export function useLogin() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  return useMutation({
    mutationFn: (data) => authApi.login(data),
    onSuccess: (res) => {
      const { access_token, refresh_token } = res.data.data;
      login(access_token, refresh_token, null);
      navigate("/dashboard");
      toast.success("Giriş yapıldı");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Giriş başarısız");
    },
  });
}

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data) => authApi.register(data),
    onSuccess: () => {
      toast.success("Kayıt başarılı! Giriş yapabilirsiniz.");
      navigate("/login");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Kayıt başarısız");
    },
  });
}

export function useLogout() {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSettled: () => {
      logout();
      navigate("/login");
    },
  });
}

export function useMe() {
  const setUser = useAuthStore((s) => s.setUser);
  const isAuthenticated = useAuthStore((s) => !!s.accessToken);

  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await authApi.me();
      setUser(res.data.data);
      return res.data.data;
    },
    enabled: isAuthenticated,
    staleTime: Infinity,
  });
}
