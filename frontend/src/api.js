async function request(path, options) {
  const token = localStorage.getItem('admin_token')
  const isFormData = options?.body instanceof FormData
  const response = await fetch(path, {
    headers: { ...(isFormData ? {} : { 'Content-Type': 'application/json' }), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    ...options,
  })
  if (!response.ok) {
    if (response.status === 401 && path !== '/api/auth/login') {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
    }
    throw new Error((await response.json()).detail || '请求失败')
  }
  return response.status === 204 ? null : response.json()
}

export const api = {
  posts: (params = {}) => request(`/api/posts?${new URLSearchParams(Object.entries(params).filter(([, v]) => v))}`),
  post: (id) => request(`/api/posts/${id}`),
  likePost: (id) => request(`/api/posts/${id}/like`, { method: 'POST' }),
  tags: () => request('/api/tags'),
  categories: () => request('/api/categories'),
  comments: (id) => request(`/api/posts/${id}/comments`),
  comment: (id, payload) => request(`/api/posts/${id}/comments`, { method: 'POST', body: JSON.stringify(payload) }),
  createPost: (payload) => request('/api/posts', { method: 'POST', body: JSON.stringify(payload) }),
  updatePost: (id, payload) => request(`/api/posts/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  uploadResource: (file) => { const body = new FormData(); body.append('file', file); return request('/api/admin/uploads', { method: 'POST', body }) },
  login: (payload) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => request('/api/auth/me'),
  adminPosts: (params = {}) => request(`/api/admin/posts?${new URLSearchParams(Object.entries(params).filter(([, value]) => value !== '' && value !== undefined && value !== null))}`),
  adminPost: (id) => request(`/api/admin/posts/${id}`),
  deletePost: (id) => request(`/api/admin/posts/${id}`, { method: 'DELETE' }),
  profile: () => request('/api/profile'),
  siteStats: () => request('/api/stats'),
  updateProfile: (payload) => request('/api/admin/profile', { method: 'PUT', body: JSON.stringify(payload) }),
  changePassword: (payload) => request('/api/auth/password', { method: 'PUT', body: JSON.stringify(payload) }),
  adminCategories: () => request('/api/admin/categories'),
  createCategory: (payload) => request('/api/admin/categories', { method: 'POST', body: JSON.stringify(payload) }),
  updateCategory: (slug, payload) => request(`/api/admin/categories/${slug}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCategory: (slug) => request(`/api/admin/categories/${slug}`, { method: 'DELETE' }),
  adminTags: () => request('/api/admin/tags'),
  createTag: (payload) => request('/api/admin/tags', { method: 'POST', body: JSON.stringify(payload) }),
  updateTag: (slug, payload) => request(`/api/admin/tags/${slug}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTag: (slug) => request(`/api/admin/tags/${slug}`, { method: 'DELETE' }),
}
