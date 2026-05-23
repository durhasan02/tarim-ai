import client from "./client";

export const authApi = {
  register: (data) => client.post("/auth/register", data),
  login: (data) => client.post("/auth/login", data),
  logout: () => client.post("/auth/logout"),
  me: () => client.get("/auth/me"),
  refresh: (refreshToken) =>
    client.post("/auth/refresh", { refresh_token: refreshToken }),
};
