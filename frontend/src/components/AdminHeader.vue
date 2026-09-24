<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ExternalLink, FileText, LogOut, Menu, Moon, PenLine, Settings, Sun, X } from 'lucide-vue-next'
import { auth } from '../auth'

const router = useRouter()
const route = useRoute()
const dark = ref(false)
const open = ref(false)
const nav = [
  ['/admin', '文章管理', FileText],
  ['/admin/write', '新建文章', PenLine],
  ['/admin/settings', '站点设置', Settings],
]

onMounted(() => {
  const saved = localStorage.getItem('theme')
  dark.value = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches
  document.documentElement.classList.toggle('dark', dark.value)
})

function toggleTheme() {
  dark.value = !dark.value
  document.documentElement.classList.toggle('dark', dark.value)
  localStorage.setItem('theme', dark.value ? 'dark' : 'light')
}

function logout() {
  auth.clear()
  open.value = false
  router.replace('/admin/login')
}

function isActive(path) {
  if (path === '/admin') return route.path === path
  return route.path.startsWith(path)
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-zinc-200/80 bg-white/95 backdrop-blur-xl dark:border-zinc-800 dark:bg-zinc-950/95">
    <div class="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-6 lg:px-8">
      <RouterLink to="/admin" class="flex shrink-0 items-center gap-2.5">
        <span class="grid h-8 w-8 place-items-center rounded-lg bg-zinc-900 text-sm font-bold text-white dark:bg-white dark:text-zinc-950">BZ</span>
        <span class="leading-tight"><b class="block text-sm">Baize Admin</b><span class="block text-[10px] uppercase tracking-[.16em] text-zinc-400">Content studio</span></span>
      </RouterLink>

      <nav class="ml-5 hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="[path, label, icon] in nav"
          :key="path"
          :to="path"
          class="inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
          :class="{ '!bg-zinc-100 !text-zinc-950 dark:!bg-zinc-800 dark:!text-white': isActive(path) }"
        ><component :is="icon" />{{ label }}</RouterLink>
      </nav>

      <div class="ml-auto hidden items-center gap-2 md:flex">
        <a href="/" target="_blank" rel="noopener" class="secondary-button h-9"><ExternalLink />查看前台</a>
        <button class="icon-button" aria-label="切换主题" @click="toggleTheme"><Sun v-if="dark" /><Moon v-else /></button>
        <button class="secondary-button h-9" @click="logout"><LogOut />退出</button>
      </div>
      <button class="icon-button ml-auto md:hidden" aria-label="打开后台菜单" @click="open = !open"><X v-if="open" /><Menu v-else /></button>
    </div>

    <nav v-if="open" class="grid gap-1 border-t border-zinc-200 p-3 md:hidden dark:border-zinc-800">
      <RouterLink v-for="[path, label, icon] in nav" :key="path" :to="path" class="flex items-center gap-2 rounded-md px-3 py-2.5 text-sm text-zinc-500" :class="{ 'bg-zinc-100 text-zinc-950 dark:bg-zinc-800 dark:text-white': isActive(path) }" @click="open = false"><component :is="icon" />{{ label }}</RouterLink>
      <a href="/" target="_blank" rel="noopener" class="flex items-center gap-2 rounded-md px-3 py-2.5 text-sm text-zinc-500" @click="open = false"><ExternalLink />查看前台（新标签）</a>
      <div class="mt-1 flex gap-2 border-t border-zinc-200 pt-3 dark:border-zinc-800">
        <button class="secondary-button flex-1 justify-center" @click="toggleTheme"><Sun v-if="dark" /><Moon v-else />切换主题</button>
        <button class="secondary-button flex-1 justify-center" @click="logout"><LogOut />退出</button>
      </div>
    </nav>
  </header>
</template>
