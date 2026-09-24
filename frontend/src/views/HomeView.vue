<script setup>
import { onMounted, ref } from 'vue'
import { ArrowRight, Code2, MapPin, Tag } from 'lucide-vue-next'
import { api } from '../api'
import PostCard from '../components/PostCard.vue'

const posts = ref([])
const tags = ref([])
const profile = ref({ name: '白泽', initials: 'BZ', title: 'Full-stack Engineer', hero_intro: '你好，我是白泽，全栈工程师与技术写作者。这里分享前端架构、AI 编程、工程效率，以及值得被认真记录的技术思考。', hero_skills: ['React', 'Next.js', 'AI'], bio: '热衷于把复杂问题讲清楚。' })
const stats = ref({ published_posts: 0, total_views: 0, writing_years: 1 })
const formatMetric = (value) => {
  const number = Number(value || 0)
  if (number >= 10000) return `${(number / 10000).toFixed(number >= 100000 ? 0 : 1).replace(/\.0$/, '')}w`
  if (number >= 1000) return `${(number / 1000).toFixed(1).replace(/\.0$/, '')}k`
  return number.toLocaleString('zh-CN')
}
onMounted(async () => {
  const [postData, tagData, profileData, statsData] = await Promise.all([api.posts({ page_size: 3 }), api.tags(), api.profile(), api.siteStats()])
  posts.value = postData.items
  tags.value = tagData.slice(0, 10)
  profile.value = { ...profile.value, ...profileData, initials: profileData.initials || 'BZ' }
  stats.value = statsData
})
</script>

<template>
  <main>
    <section class="relative overflow-hidden border-b border-zinc-200 dark:border-zinc-800">
      <div class="app-grid absolute inset-0" />
      <div class="absolute -right-32 -top-32 h-96 w-96 rounded-full bg-teal-300/10 blur-3xl dark:bg-teal-500/10" />
      <div class="relative mx-auto grid max-w-7xl gap-12 px-4 pb-7 pt-10 sm:px-6 sm:pb-8 sm:pt-12 lg:grid-cols-[1.04fr_.96fr] lg:items-center lg:px-8 lg:pb-8 lg:pt-12">
        <div>
          <div class="mb-5 inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50/80 px-3 py-1 text-xs font-medium text-teal-800 dark:border-teal-900 dark:bg-teal-950/60 dark:text-teal-300"><span class="h-1.5 w-1.5 rounded-full bg-teal-500" /> INDEPENDENT BUILDER / 2026</div>
          <h1 class="text-4xl font-black leading-[1.08] tracking-[-.055em] sm:text-6xl lg:text-[4.65rem]">代码之外，<br><span class="bg-gradient-to-r from-teal-600 via-sky-600 to-zinc-400 bg-clip-text text-transparent dark:from-teal-300 dark:via-sky-300 dark:to-zinc-500">还有更大的世界。</span></h1>
          <p class="mt-6 max-w-xl whitespace-pre-line text-base leading-8 text-zinc-600 dark:text-zinc-400 sm:text-lg">{{ profile.hero_intro }}</p>
          <div class="mt-8 flex flex-wrap gap-3"><RouterLink to="/articles" class="primary-button">开始阅读 <ArrowRight /></RouterLink><RouterLink to="/about" class="secondary-button">关于作者</RouterLink></div>
          <div class="mt-10 flex flex-wrap gap-6 text-xs text-zinc-500"><span class="flex items-center gap-2"><i class="h-2 w-2 rounded-full bg-emerald-500" /> Currently shipping</span><span class="flex items-center gap-2"><MapPin />Hangzhou / Remote</span><span class="flex items-center gap-2"><Code2 />Java first</span></div>
        </div>
        <div class="tech-orb relative overflow-hidden rounded-2xl border border-zinc-200/80 p-5 dark:border-zinc-800/80">
          <div class="tech-grid absolute inset-0 opacity-60" /><div class="terminal-sheen absolute inset-0" />
          <div class="relative"><div class="flex items-center justify-between border-b border-zinc-200 pb-3 dark:border-zinc-800"><div class="flex items-center gap-2 text-xs font-semibold"><span class="flex gap-1"><i class="dot bg-rose-400" /><i class="dot bg-amber-400" /><i class="dot bg-emerald-400" /></span>baize-dev / now</div><span class="rounded border border-teal-300/40 bg-teal-100/60 px-2 py-0.5 font-mono text-[10px] text-teal-700 dark:bg-teal-950">ONLINE</span></div>
            <div class="grid gap-4 py-6 sm:grid-cols-[1.15fr_.85fr]"><div><p class="font-mono text-[11px] text-teal-700 dark:text-teal-300">$ cat /current-focus</p><h2 class="mt-3 text-2xl font-bold">Building useful<br><span class="text-zinc-400">things for the web.</span></h2><p class="mt-3 text-sm leading-6 text-zinc-500">把复杂问题拆成清晰的界面，把想法变成可以被使用的产品。</p><div class="mt-5 flex flex-wrap gap-2"><span v-for="item in profile.hero_skills" :key="item" class="tech-chip">{{ item }}</span></div></div><div class="flex items-end justify-end"><div class="radar"><i /><span class="right-[-8px] top-7">ship fast</span><span class="bottom-[-8px] left-2">stay curious</span></div></div></div>
            <div class="signal-line" /><div class="mt-4 grid grid-cols-3"><div v-for="item in [{value:stats.published_posts,label:'posts'},{value:formatMetric(stats.total_views),label:'reads'},{value:`${stats.writing_years}y`,label:'writing'}]" :key="item.label"><b class="font-mono text-lg">{{ item.value }}</b><p class="text-[10px] uppercase tracking-[.14em] text-zinc-400">{{ item.label }}</p></div></div>
          </div>
        </div>
      </div>
    </section>
    <section class="mx-auto max-w-7xl px-4 pb-10 pt-8 sm:px-6 sm:pb-12 sm:pt-8 lg:px-8">
      <div class="mb-8 flex items-end justify-between"><div><p class="eyebrow">Latest writing</p><h2 class="mt-2 text-2xl font-bold">最新文章</h2></div><RouterLink to="/articles" class="flex items-center gap-1 text-sm text-zinc-500">查看全部 <ArrowRight class="h-4 w-4" /></RouterLink></div>
      <div class="grid gap-10 lg:grid-cols-[1fr_300px]"><div class="grid gap-4"><PostCard v-for="post in posts" :key="post.id" :post="post" /></div><aside class="space-y-5"><div class="panel"><div class="flex items-center gap-3"><div class="avatar">{{ profile.initials }}</div><div><b>{{ profile.name }}</b><p class="text-xs text-zinc-500">{{ profile.title }}</p></div></div><p class="mt-4 text-sm leading-6 text-zinc-500">{{ profile.bio }}</p></div><div class="panel"><h3 class="flex items-center gap-2 text-sm font-semibold"><Tag />标签云</h3><div class="mt-4 flex flex-wrap gap-2"><RouterLink v-for="item in tags" :key="item.name" :to="{path:'/tags',query:{tag:item.name}}" class="tag-pill">{{ item.name }}</RouterLink></div></div></aside></div>
    </section>
  </main>
</template>
