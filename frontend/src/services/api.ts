import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const analyzeMetadata = async (data: {
  problem_statement: string;
  challenges: string[];
  connector_config: any;
  org_metadata: any;
}) => {
  const response = await axios.post(`${API_BASE_URL}/training/analyze-metadata`, data);
  return response.data;
};

export const generateSheets = async (dataset_cols: any, sql_queries: any) => {
  const response = await axios.post(`${API_BASE_URL}/training/generate-sheets`, {
    dataset_cols,
    sql_queries
  });
  return response.data;
};

export const startAutoML = async (formData: FormData) => {
  const response = await axios.post(`${API_BASE_URL}/training/start-automl`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};
