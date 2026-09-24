<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, Moon, Search, Sun, X } from 'lucide-vue-next'

const router = useRouter()
const dark = ref(false)
const open = ref(false)
const query = ref('')
const nav = [['/', '首页'], ['/articles', '文章'], ['/categories', '分类'], ['/tags', '标签'], ['/about', '关于我']]

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
function search() {
  router.push({ path: '/articles', query: { q: query.value } })
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-zinc-200/80 bg-white/90 backdrop-blur-xl dark:border-zinc-800 dark:bg-zinc-950/90">
    <div class="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
      <RouterLink to="/" class="flex items-center gap-2.5 font-bold"><span class="grid h-8 w-8 rounded-lg bg-zinc-900 text-sm text-white dark:bg-white dark:text-zinc-950 place-items-center">BZ</span>Baize<span class="-ml-2.5 text-teal-600">.dev</span></RouterLink>
      <nav class="ml-5 hidden items-center gap-1 lg:flex">
        <RouterLink v-for="[path, label] in nav" :key="path" :to="path" class="rounded-md px-3 py-2 text-sm font-medium text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800" active-class="!bg-zinc-100 !text-zinc-950 dark:!bg-zinc-800 dark:!text-white">{{ label }}</RouterLink>
      </nav>
      <form class="relative ml-auto hidden w-full max-w-xs md:block" @submit.prevent="search">
        <Search class="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
        <input v-model="query" placeholder="搜索文章..." class="h-9 w-full rounded-md border border-zinc-200 bg-zinc-50 pl-9 pr-3 text-sm outline-none focus:border-teal-500 dark:border-zinc-800 dark:bg-zinc-900" />
      </form>
      <button class="icon-button" aria-label="切换主题" @click="toggleTheme"><Sun v-if="dark" /><Moon v-else /></button>
      <button class="icon-button lg:hidden" @click="open = !open"><X v-if="open" /><Menu v-else /></button>
    </div>
    <nav v-if="open" class="grid border-t border-zinc-200 p-3 lg:hidden dark:border-zinc-800">
      <RouterLink v-for="[path, label] in nav" :key="path" :to="path" class="rounded-md px-3 py-2 text-sm text-zinc-500" @click="open = false">{{ label }}</RouterLink>
    </nav>
  </header>
</template>
