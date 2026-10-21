export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081",
  apiTimeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || "30000"),
  environment: process.env.NEXT_PUBLIC_ENV || "development",
};
