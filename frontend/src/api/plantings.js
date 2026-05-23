import client from "./client";

export const plantingsApi = {
  list: (params) => client.get("/plantings", { params }),
  get: (id) => client.get(`/plantings/${id}`),
  create: (data) => client.post("/plantings", data),
  update: (id, data) => client.put(`/plantings/${id}`, data),
  irrigationLogs: (id) => client.get(`/plantings/${id}/irrigation`),
  addIrrigation: (id, data) => client.post(`/plantings/${id}/irrigation`, data),
};
