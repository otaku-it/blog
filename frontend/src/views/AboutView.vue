<script setup>
import { onMounted, ref } from 'vue'
import { Github, Mail, MapPin } from 'lucide-vue-next'
import { api } from '../api'

const profile = ref({ name: '白泽', initials: 'BZ', title: '全栈工程师与技术写作者', bio: '', story: '', location: '中国 · 上海', email: '', github: '', principles: [], stack: [] })
const loading = ref(true)
onMounted(async () => {
  try { profile.value = await api.profile() } finally { loading.value = false }
})
</script>

<template>
  <main v-if="!loading"><section class="border-b border-zinc-200 dark:border-zinc-800"><div class="mx-auto grid max-w-5xl gap-10 px-4 py-16 md:grid-cols-[220px_1fr]"><div><div class="flex aspect-square items-end rounded-2xl bg-gradient-to-br from-teal-100 via-zinc-100 to-sky-200 p-5 dark:from-teal-950 dark:via-zinc-800 dark:to-sky-950"><b class="text-6xl text-teal-700 dark:text-teal-300">{{ profile.initials }}.</b></div><p class="mt-4 flex items-center gap-2 text-sm text-zinc-500"><MapPin/>{{ profile.location }}</p></div><div><p class="eyebrow">About me</p><h1 class="mt-2 text-5xl font-black tracking-tight">你好，我是{{ profile.name }}。</h1><p class="mt-6 text-lg leading-8 text-zinc-600 dark:text-zinc-300">{{ profile.title }}</p><p class="mt-4 leading-7 text-zinc-500">{{ profile.bio }}</p><div class="mt-5 space-y-4 leading-7 text-zinc-500"><p v-for="paragraph in profile.story.split('\n').filter(Boolean)" :key="paragraph">{{ paragraph }}</p></div><div class="mt-7 flex gap-3"><a :href="profile.github" target="_blank" rel="noopener" class="primary-button"><Github/>GitHub</a><a href="https://mail.163.com/" target="_blank" rel="noopener" class="secondary-button"><Mail/>联系我</a></div></div></div></section><section class="mx-auto max-w-5xl px-4 py-16"><div class="grid gap-12 md:grid-cols-2"><div><p class="eyebrow">Principles</p><h2 class="mt-2 text-2xl font-bold">我在意的事情</h2><div class="mt-6 space-y-5"><div v-for="(item,index) in profile.principles" :key="item.title" class="flex gap-4"><b class="text-xs text-teal-600">{{ String(index+1).padStart(2,'0') }}</b><div><h3 class="text-sm font-semibold">{{ item.title }}</h3><p class="mt-1 text-sm text-zinc-500">{{ item.description }}</p></div></div></div></div><div><p class="eyebrow">Stack</p><h2 class="mt-2 text-2xl font-bold">技术栈</h2><div class="mt-6 space-y-3"><div v-for="group in profile.stack" :key="group.group" class="panel"><b>{{ group.group }}</b><div class="mt-3 flex flex-wrap gap-2"><span v-for="item in group.items" :key="item" class="tech-chip">{{ item }}</span></div></div></div></div></div></section></main>
</template>
