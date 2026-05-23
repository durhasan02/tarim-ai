import client from "./client";

export const aiApi = {
  detectDisease: (formData) =>
    client.post("/ai/disease-detection", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  irrigationRecommendation: (fieldId, plantingId) =>
    client.get("/ai/irrigation/recommendation", {
      params: { field_id: fieldId, planting_id: plantingId },
    }),
};
