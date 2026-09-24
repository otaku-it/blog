<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import PostCard from '../components/PostCard.vue'
const route=useRoute(), tags=ref([]), selected=ref(route.query.tag||''), posts=ref([])
async function select(name){
  selected.value=name
  posts.value=name ? (await api.posts({tag:name,page_size:20})).items : []
}
onMounted(async()=>{
  tags.value=await api.tags()
  const requested = tags.value.some(tag => tag.name === selected.value) ? selected.value : ''
  await select(requested || tags.value[0]?.name || '')
})
watch(()=>route.query.tag,(tag)=>tag&&select(tag))
</script>
<template><main class="page-shell"><p class="eyebrow">Topics</p><h1 class="page-title">标签</h1><p class="page-subtitle">循着关键词，找到感兴趣的内容。</p><div class="mt-10 grid gap-8 lg:grid-cols-[300px_1fr]"><aside class="grid grid-cols-2 gap-2 rounded-xl border border-zinc-200 p-3 dark:border-zinc-800 lg:grid-cols-2"><button v-for="tag in tags" :key="tag.slug || tag.name" class="rounded-lg border border-transparent bg-zinc-50 p-3 text-left dark:bg-zinc-900" :class="{'!border-teal-500 !bg-teal-50 dark:!bg-teal-950/40':selected===tag.name}" @click="select(tag.name)"><b class="text-sm"># {{ tag.name }}</b><p class="text-xs text-zinc-400">{{ tag.count }} 篇文章</p></button><p v-if="!tags.length" class="col-span-2 py-8 text-center text-sm text-zinc-400">暂无标签</p></aside><section><h2 class="text-2xl font-bold">{{ selected ? `# ${selected}` : '暂无标签' }}</h2><div v-if="posts.length" class="mt-5 grid gap-4"><PostCard v-for="post in posts" :key="post.id" :post="post" /></div><div v-else-if="selected" class="mt-5 rounded-xl border border-dashed border-zinc-200 px-5 py-12 text-center dark:border-zinc-800"><p class="font-medium">该标签暂时没有已发布文章</p><p class="mt-2 text-sm text-zinc-400">标签已经同步到前台，发布关联文章后会显示在这里。</p></div></section></div></main></template>
