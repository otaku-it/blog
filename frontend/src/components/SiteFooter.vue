<script setup>
import { onMounted, ref } from 'vue'
import { Github, Mail, Rss } from 'lucide-vue-next'
import { api } from '../api'
const profile = ref({ github: 'https://github.com', email: 'hello@example.com' })
onMounted(async () => { try { profile.value = await api.profile() } catch {} })
</script>
<template><footer class="border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950"><div class="mx-auto flex max-w-7xl flex-col gap-5 px-4 py-10 md:flex-row md:items-center"><div><b>Baize.dev</b><p class="mt-1 text-sm text-zinc-500">记录技术，也记录思考。</p></div><div class="flex gap-2 md:ml-auto"><a class="icon-button" :href="profile.github" target="_blank"><Github /></a><a class="icon-button" :href="`mailto:${profile.email}`"><Mail /></a><button class="icon-button"><Rss /></button></div><p class="text-sm text-zinc-500">© 2026 Baize.dev · Vue · FastAPI · MySQL</p></div></footer></template>
