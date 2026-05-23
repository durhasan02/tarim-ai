import client from "./client";

export const harvestsApi = {
  list: () => client.get("/harvests"),
  create: (data) => client.post("/harvests", data),
  createSale: (data) => client.post("/sales", data),
  salesSummary: () => client.get("/sales/summary"),
};
