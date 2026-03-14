import { http } from "./client";

export async function fetchCollection(endpoint, params = {}) {
  const response = await http.get(endpoint, { params });
  return {
    items: response.data,
    total: Number(response.headers["x-total-count"] || response.data.length || 0),
  };
}

export async function fetchEntity(endpoint, id) {
  const response = await http.get(`${endpoint}/${id}`);
  return response.data;
}

export async function createEntity(endpoint, payload) {
  const response = await http.post(endpoint, payload);
  return response.data;
}

export async function updateEntity(endpoint, id, payload) {
  const response = await http.put(`${endpoint}/${id}`, payload);
  return response.data;
}

export async function deleteEntity(endpoint, id) {
  await http.delete(`${endpoint}/${id}`);
}

export async function uploadMedia(formData, onUploadProgress) {
  const response = await http.post("/media/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  });
  return response.data;
}

export async function deleteMedia(fileUrl) {
  await http.delete("/media", {
    data: {
      file_url: fileUrl,
    },
  });
}
