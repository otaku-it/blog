<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-vue-next'
import { api } from '../api'
import { auth } from '../auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const route = useRoute()
const router = useRouter()

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const data = await api.login({ username: username.value, password: password.value })
    auth.setSession(data)
    router.replace(route.query.redirect || '/admin')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="relative grid min-h-[calc(100vh-4rem)] place-items-center overflow-hidden bg-zinc-50 px-4 dark:bg-zinc-950">
    <div class="app-grid absolute inset-0 opacity-60" />
    <section class="relative w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-7 shadow-xl shadow-zinc-200/40 dark:border-zinc-800 dark:bg-zinc-900 dark:shadow-black/20">
      <div class="mb-7 flex items-start justify-between">
        <div><p class="eyebrow">Admin console</p><h1 class="mt-2 text-2xl font-bold">登录内容后台</h1><p class="mt-2 text-sm text-zinc-500">写作、草稿和发布权限仅对管理员开放。</p></div>
        <div class="grid h-11 w-11 place-items-center rounded-xl bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300"><ShieldCheck /></div>
      </div>
      <form class="space-y-4" @submit.prevent="submit">
        <label class="block"><span class="mb-1.5 block text-xs font-medium text-zinc-500">管理员账号</span><input v-model="username" autocomplete="username" placeholder="输入管理员账号" class="h-11 w-full rounded-lg border border-zinc-200 bg-transparent px-3 outline-none focus:border-teal-500 dark:border-zinc-700" /></label>
        <label class="block"><span class="mb-1.5 block text-xs font-medium text-zinc-500">密码</span><div class="relative"><LockKeyhole class="absolute left-3 top-3 h-4 w-4 text-zinc-400"/><input v-model="password" type="password" autocomplete="current-password" class="h-11 w-full rounded-lg border border-zinc-200 bg-transparent pl-10 pr-3 outline-none focus:border-teal-500 dark:border-zinc-700" placeholder="输入管理员密码" /></div></label>
        <p v-if="error" class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600 dark:bg-rose-950/40">{{ error }}</p>
        <button class="primary-button h-11 w-full justify-center" :disabled="loading"><span>{{ loading ? '正在验证...' : '进入后台' }}</span><ArrowRight /></button>
      </form>
      <p class="mt-5 text-center text-xs leading-5 text-zinc-400">账号由部署环境变量配置，不在前端代码中保存密码。</p>
    </section>
  </main>
</template>
