<script setup>
import { onMounted, ref } from 'vue'
import { Folder } from 'lucide-vue-next'
import { api } from '../api'
import PostCard from '../components/PostCard.vue'
const categories=ref([]),selected=ref(''),posts=ref([])
async function select(name){
  selected.value=name
  posts.value=name ? (await api.posts({category:name,page_size:20})).items : []
}
onMounted(async()=>{
  categories.value=await api.categories()
  await select(categories.value[0]?.name || '')
})
</script>
<template><main class="page-shell"><p class="eyebrow">Collections</p><h1 class="page-title">文章分类</h1><p class="page-subtitle">按知识领域整理的长期写作集合。</p><div class="mt-10 grid gap-8 lg:grid-cols-[280px_1fr]"><aside class="space-y-2"><button v-for="item in categories" :key="item.slug || item.name" class="flex w-full items-center rounded-lg border border-zinc-200 px-4 py-3 dark:border-zinc-800" :class="{'bg-zinc-900 text-white dark:bg-white dark:text-zinc-950':selected===item.name}" @click="select(item.name)"><Folder class="h-4 w-4"/><span class="ml-3 text-sm font-medium">{{ item.name }}</span><span class="ml-auto text-xs opacity-60">{{ item.count }} 篇</span></button><p v-if="!categories.length" class="rounded-lg border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-400 dark:border-zinc-800">暂无分类</p></aside><section><h2 class="text-2xl font-bold">{{ selected || '暂无分类' }}</h2><div v-if="posts.length" class="mt-5 grid gap-4"><PostCard v-for="post in posts" :key="post.id" :post="post" /></div><div v-else-if="selected" class="mt-5 rounded-xl border border-dashed border-zinc-200 px-5 py-12 text-center dark:border-zinc-800"><p class="font-medium">该分类暂时没有已发布文章</p><p class="mt-2 text-sm text-zinc-400">分类已经同步到前台，发布关联文章后会显示在这里。</p></div></section></div></main></template>
