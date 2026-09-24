<script setup>
import { ref } from 'vue'
import { Clock3, Eye, Heart, ArrowRight } from 'lucide-vue-next'
import { api } from '../api'
const props = defineProps({ post: { type: Object, required: true } })
const likes = ref(Number(props.post.likes || 0))
const liked = ref(false)
const liking = ref(false)
async function like(event) {
  event.preventDefault()
  event.stopPropagation()
  if (liking.value) return
  liking.value = true
  try {
    const result = await api.likePost(props.post.id)
    likes.value = result.likes
    liked.value = true
  } catch {}
  finally { liking.value = false }
}
const formatDate = (date) => new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(date))
const formatViews = (views) => Number(views || 0).toLocaleString('zh-CN')
</script>
<template>
  <article class="group rounded-xl border border-zinc-200 bg-white p-5 transition hover:-translate-y-0.5 hover:border-zinc-300 hover:shadow-soft dark:border-zinc-800 dark:bg-zinc-900/50">
    <RouterLink :to="`/articles/${post.id}`" class="block">
      <div class="flex items-center gap-2 text-xs text-zinc-500"><span class="font-medium text-teal-700 dark:text-teal-400">{{ post.category }}</span><span>·</span><time>{{ formatDate(post.date) }}</time><span class="ml-auto flex items-center gap-1" :title="`根据正文 ${formatViews(post.word_count)} 个有效字词估算`"><Clock3 class="h-3.5 w-3.5" />预计 {{ post.read_time }}</span></div>
      <h3 class="mt-3 text-lg font-bold tracking-tight group-hover:text-teal-700 dark:group-hover:text-teal-400">{{ post.title }}</h3>
      <p class="mt-2 line-clamp-2 text-sm leading-6 text-zinc-500">{{ post.excerpt }}</p>
    </RouterLink>
    <div class="mt-4 flex items-center gap-2 border-t border-zinc-100 pt-4 dark:border-zinc-800">
      <span v-for="tag in post.tags.slice(0, 3)" :key="tag" class="text-xs text-zinc-500">#{{ tag }}</span>
      <span class="ml-auto flex items-center gap-1 text-xs text-zinc-400" title="真实浏览次数"><Eye class="h-3.5 w-3.5" />{{ formatViews(post.views) }}</span>
      <button type="button" class="flex items-center gap-1 text-xs text-zinc-400 transition hover:text-rose-500 disabled:opacity-60" :class="liked ? 'text-rose-500' : ''" :disabled="liking" title="点击一次增加一个赞" @click="like"><Heart class="h-3.5 w-3.5" :fill="liked ? 'currentColor' : 'none'" />{{ formatViews(likes) }}</button>
      <RouterLink :to="`/articles/${post.id}`" title="阅读文章"><ArrowRight class="h-4 w-4 text-teal-600 opacity-0 transition group-hover:translate-x-1 group-hover:opacity-100" /></RouterLink>
    </div>
  </article>
</template>
