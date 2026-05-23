import client from "./client";

export const fieldsApi = {
  list: () => client.get("/fields"),
  get: (id) => client.get(`/fields/${id}`),
  create: (data) => client.post("/fields", data),
  update: (id, data) => client.put(`/fields/${id}`, data),
  delete: (id) => client.delete(`/fields/${id}`),
  stats: (id) => client.get(`/fields/${id}/stats`),
};
