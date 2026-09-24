import { createRouter, createWebHistory } from 'vue-router'
const HomeView = () => import('./views/HomeView.vue')
const ArticlesView = () => import('./views/ArticlesView.vue')
const ArticleView = () => import('./views/ArticleView.vue')
const TagsView = () => import('./views/TagsView.vue')
const CategoriesView = () => import('./views/CategoriesView.vue')
const AboutView = () => import('./views/AboutView.vue')
const WriteView = () => import('./views/WriteView.vue')
const LoginView = () => import('./views/LoginView.vue')
const AdminView = () => import('./views/AdminView.vue')
const SettingsView = () => import('./views/SettingsView.vue')

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: (to) => to.hash ? { el: to.hash, top: 90, behavior: 'smooth' } : { top: 0 },
  routes: [
    { path: '/', component: HomeView },
    { path: '/articles', component: ArticlesView },
    { path: '/articles/:id', component: ArticleView },
    { path: '/tags', component: TagsView },
    { path: '/categories', component: CategoriesView },
    { path: '/about', component: AboutView },
    { path: '/admin/login', component: LoginView, meta: { guest: true } },
    { path: '/admin', component: AdminView, meta: { requiresAuth: true } },
    { path: '/admin/settings', component: SettingsView, meta: { requiresAuth: true } },
    { path: '/admin/write/:id?', component: WriteView, meta: { requiresAuth: true } },
    { path: '/write', redirect: '/admin/write' },
  ],
})

router.beforeEach((to) => {
  const authenticated = Boolean(localStorage.getItem('admin_token'))
  if (to.meta.requiresAuth && !authenticated) return { path: '/admin/login', query: { redirect: to.fullPath } }
  if (to.meta.guest && authenticated) return '/admin'
})

export default router
