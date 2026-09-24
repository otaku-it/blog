<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import PostCard from '../components/PostCard.vue'

const route = useRoute(), router = useRouter()
const posts = ref([]), tags = ref([]), total = ref(0), page = ref(1), selected = ref(''), query = ref(route.query.q || '')
const pages = computed(() => Math.max(1, Math.ceil(total.value / 6)))
async function load() { const data = await api.posts({ page: page.value, page_size: 6, tag: selected.value, query: query.value }); posts.value = data.items; total.value = data.total }
onMounted(async () => { tags.value = await api.tags(); await load() })
watch([page, selected], load)
let timer
watch(query, () => { clearTimeout(timer); page.value = 1; timer = setTimeout(() => { router.replace({ query: query.value ? { q: query.value } : {} }); load() }, 250) })
</script>
<template><main class="page-shell"><p class="eyebrow">Archive</p><h1 class="page-title">文章归档</h1><p class="page-subtitle">关于技术、产品和独立开发的长期记录。</p><div class="mt-10 flex flex-col gap-4 border-y border-zinc-200 py-5 dark:border-zinc-800 sm:flex-row"><div class="flex gap-2 overflow-auto"><button class="filter-pill" :class="{active:!selected}" @click="selected='';page=1">全部</button><button v-for="tag in tags.slice(0,8)" :key="tag.name" class="filter-pill" :class="{active:selected===tag.name}" @click="selected=tag.name;page=1">{{ tag.name }}</button></div><input v-model="query" class="ml-auto h-9 w-full rounded-md border border-zinc-200 bg-transparent px-3 text-sm outline-none sm:w-60 dark:border-zinc-800" placeholder="搜索文章" /></div><div class="mt-8 grid gap-4 md:grid-cols-2"><PostCard v-for="post in posts" :key="post.id" :post="post" /></div><div class="mt-10 flex items-center justify-between border-t border-zinc-200 pt-6 dark:border-zinc-800"><p class="text-sm text-zinc-500">第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 篇</p><div class="flex gap-2"><button class="secondary-button" :disabled="page===1" @click="page--">上一页</button><button v-for="n in pages" :key="n" class="page-button" :class="{active:page===n}" @click="page=n">{{ n }}</button><button class="secondary-button" :disabled="page===pages" @click="page++">下一页</button></div></div></main></template>
