import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
// Note: Auth token is automatically set by the useAuth() hook
// which calls setAuthToken() when the user signs in
api.interceptors.request.use(
  async (config) => {
    // Token is set via api.defaults.headers.common['Authorization']
    // by the setAuthToken helper function below
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
    }
    return Promise.reject(error);
  }
);

// Helper to set auth token (to be called from client components)
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// ==========================================
// CLIENT API METHODS
// ==========================================

export const clientsApi = {
  list: (params?: { page?: number; page_size?: number; status?: string }) =>
    api.get('/clients', { params }),
  
  get: (id: string) => api.get(`/clients/${id}`),
  
  create: (data: any) => api.post('/clients', data),
  
  update: (id: string, data: any) => api.patch(`/clients/${id}`, data),
  
  delete: (id: string) => api.delete(`/clients/${id}`),
};

// ==========================================
// DISPUTE API METHODS
// ==========================================

export const disputesApi = {
  list: (params?: { page?: number; page_size?: number; client_id?: string }) =>
    api.get('/disputes', { params }),
  
  get: (id: string) => api.get(`/disputes/${id}`),
  
  create: (data: any) => api.post('/disputes', data),
  
  generateLetter: (id: string) => api.post(`/disputes/${id}/generate`),
};

// ==========================================
// BILLING API METHODS
// ==========================================

export const billingApi = {
  getSubscription: () => api.get('/billing/subscription'),
  
  createSubscription: (data: any) => api.post('/billing/subscribe', data),
  
  cancelSubscription: () => api.post('/billing/subscription/cancel'),
};

// ==========================================
// AUTH API METHODS
// ==========================================

export const authApi = {
  verify: () => api.post('/auth/verify'),
  
  me: () => api.get('/auth/me'),
  
  createOrganization: (data: { name: string; slug: string }) =>
    api.post('/auth/organizations', data),
  
  getCurrentOrganization: () => api.get('/auth/organizations/current'),
};

// ==========================================
// EMAIL NOTIFICATION API METHODS
// ==========================================

export const emailsApi = {
  // Email Templates
  listTemplates: (params?: { page?: number; page_size?: number; category?: string; active_only?: boolean }) =>
    api.get('/emails/templates', { params }),
  
  getTemplate: (id: string) => api.get(`/emails/templates/${id}`),
  
  createTemplate: (data: any) => api.post('/emails/templates', data),
  
  updateTemplate: (id: string, data: any) => api.patch(`/emails/templates/${id}`, data),
  
  deleteTemplate: (id: string) => api.delete(`/emails/templates/${id}`),
  
  // Email Logs
  listLogs: (params?: { page?: number; page_size?: number; client_id?: string; status_filter?: string }) =>
    api.get('/emails/logs', { params }),
  
  getAnalytics: (days?: number) => api.get('/emails/analytics', { params: { days } }),
  
  // Notification Settings
  getSettings: () => api.get('/emails/settings'),
  
  updateSettings: (data: any) => api.patch('/emails/settings', data),
  
  // Send Email
  sendEmail: (data: any) => api.post('/emails/send', data),
  
  // Test Email
  sendTestEmail: (data: { to_email: string; subject: string; body_html: string }) =>
    api.post('/emails/test', data),
};

export default api;
