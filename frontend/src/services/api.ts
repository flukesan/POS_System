import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
});

// Attach token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ─── AUTH ─────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) => {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    return api.post('/auth/login', form);
  },
};

// ─── PRODUCTS ─────────────────────────────────────────────────
export const productApi = {
  list: (params?: object) => api.get('/products', { params }),
  get: (id: string) => api.get(`/products/${id}`),
  create: (data: object) => api.post('/products', data),
  update: (id: string, data: object) => api.put(`/products/${id}`, data),
  scan: (code: string) => api.get('/products/scan', { params: { code } }),
  uploadImage: (id: string, file: File, isPrimary: boolean) => {
    const form = new FormData();
    form.append('file', file);
    form.append('is_primary', String(isPrimary));
    return api.post(`/products/${id}/images`, form);
  },
  getQR: (id: string) => api.get(`/products/${id}/qr`),
};

// ─── STOCK ────────────────────────────────────────────────────
export const stockApi = {
  list: (params?: object) => api.get('/stock', { params }),
  createPO: (data: object) => api.post('/stock/purchase-orders', data),
  receiveGoods: (poId: string, items: object[]) => api.post(`/stock/purchase-orders/${poId}/receive`, items),
  adjust: (data: object) => api.post('/stock/adjust', data),
  lowStockAlerts: () => api.get('/stock/alerts/low-stock'),
  transactions: (params?: object) => api.get('/stock/transactions', { params }),
};

// ─── SALES ────────────────────────────────────────────────────
export const salesApi = {
  createOrder: (data: object) => api.post('/sales/orders', data),
  getOrder: (id: string) => api.get(`/sales/orders/${id}`),
  listOrders: (params?: object) => api.get('/sales/orders', { params }),
  initiatePayment: (data: object) => api.post('/sales/payment/initiate', data),
  confirmPayment: (data: object) => api.post('/sales/payment/confirm', data),
};

// ─── CUSTOMERS ────────────────────────────────────────────────
export const customerApi = {
  list: (params?: object) => api.get('/customers', { params }),
  get: (id: string) => api.get(`/customers/${id}`),
  create: (data: object) => api.post('/customers', data),
  update: (id: string, data: object) => api.put(`/customers/${id}`, data),
  creditSummary: (id: string) => api.get(`/customers/${id}/credit-summary`),
  recordPayment: (data: object) => api.post('/customers/credit/payment', data),
  history: (id: string, params?: object) => api.get(`/customers/${id}/history`, { params }),
  creditTransactions: (id: string) => api.get(`/customers/${id}/credit-transactions`),
};

// ─── CATEGORIES ───────────────────────────────────────────────
export const categoryApi = {
  list: () => api.get('/products/categories'),
};

// ─── REPORTS ──────────────────────────────────────────────────
export const reportApi = {
  dashboard: () => api.get('/reports/dashboard'),
  dailySales: (params?: object) => api.get('/reports/sales/daily', { params }),
  topProducts: (params?: object) => api.get('/reports/sales/top-products', { params }),
  outstandingCredit: () => api.get('/reports/credit/outstanding'),
  stockValuation: () => api.get('/reports/stock/valuation'),
};

export default api;
