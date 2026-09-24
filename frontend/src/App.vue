<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminHeader from './components/AdminHeader.vue'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'

const route = useRoute()
const isAdmin = computed(() => route.path.startsWith('/admin'))
const showAdminHeader = computed(() => isAdmin.value && route.path !== '/admin/login')
</script>

<template>
  <div class="min-h-screen bg-white text-zinc-900 transition-colors dark:bg-zinc-950 dark:text-zinc-100">
    <AdminHeader v-if="showAdminHeader" />
    <SiteHeader v-else-if="!isAdmin" />
    <RouterView />
    <SiteFooter v-if="!isAdmin" />
  </div>
</template>
