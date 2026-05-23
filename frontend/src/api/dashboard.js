import client from "./client";

export const dashboardApi = {
  summary: () => client.get("/dashboard/summary"),
  weather: (lat, lon) => client.get("/dashboard/weather", { params: { lat, lon } }),
  tasks: () => client.get("/dashboard/tasks"),
};
