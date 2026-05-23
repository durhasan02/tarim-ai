import client from "./client";

export const stockApi = {
  list: () => client.get("/stock"),
  create: (data) => client.post("/stock", data),
  update: (id, data) => client.put(`/stock/${id}`, data),
  move: (id, data) => client.post(`/stock/${id}/move`, data),
  alerts: () => client.get("/stock/alerts"),
};
