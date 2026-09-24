<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { CalendarDays, Clock3, Eye, Heart, Send } from 'lucide-vue-next'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import { api } from '../api'

hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('tsx', typescript)
hljs.registerLanguage('python', python)

const route=useRoute(),post=ref(null),comments=ref([]),comment=ref(''),message=ref(''),profile=ref({name:'白泽',initials:'BZ',title:'全栈工程师与技术写作者'})
const html=computed(()=>post.value?marked.parse(post.value.content):'')
const headings=computed(()=>[...((post.value?.content||'').matchAll(/^## (.+)$/gm))].map((match,index)=>({title:match[1],id:`section-${index}`})))
const liked=ref(false)
const liking=ref(false)
async function load(){const [postData,commentData,profileData]=await Promise.all([api.post(route.params.id),api.comments(route.params.id),api.profile()]);post.value=postData;comments.value=commentData;profile.value=profileData;await nextTick();document.querySelectorAll('.article-body h2').forEach((el,index)=>el.id=`section-${index}`);document.querySelectorAll('pre code').forEach(el=>hljs.highlightElement(el))}
async function like(){if(liking.value)return;liking.value=true;try{const result=await api.likePost(route.params.id);post.value.likes=result.likes;liked.value=true}finally{liking.value=false}}
async function submit(){if(!comment.value.trim())return;comments.value.unshift(await api.comment(route.params.id,{name:'访客',content:comment.value}));comment.value='';message.value='评论已添加'}
onMounted(load);watch(()=>route.params.id,load)
</script>
<template><main v-if="post"><section class="border-b border-zinc-200 bg-zinc-50/70 dark:border-zinc-800 dark:bg-zinc-900/30"><div class="mx-auto max-w-4xl px-4 py-14 text-center"><p class="text-sm text-zinc-500">文章 / {{ post.category }}</p><h1 class="mt-5 text-3xl font-black tracking-[-.035em] sm:text-5xl">{{ post.title }}</h1><p class="mx-auto mt-5 max-w-2xl leading-7 text-zinc-500">{{ post.excerpt }}</p><div class="mt-7 flex flex-wrap justify-center gap-4 text-sm text-zinc-500"><span class="flex items-center gap-1"><CalendarDays />{{ post.date }}</span><span class="flex items-center gap-1" :title="`${post.word_count} 个有效字词`"><Clock3 />预计 {{ post.read_time }}</span><span class="flex items-center gap-1"><Eye />{{ post.views }}</span><button type="button" class="flex items-center gap-1 transition hover:text-rose-500 disabled:opacity-60" :class="liked ? 'text-rose-500' : ''" :disabled="liking" title="点击一次增加一个赞" @click="like"><Heart :fill="liked ? 'currentColor' : 'none'" />{{ post.likes || 0 }}</button></div></div></section><div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 lg:grid-cols-[minmax(0,760px)_240px]"><article><div class="article-body" v-html="html"/><div class="mt-12 panel"><div class="flex gap-4"><div class="avatar">{{ profile.initials }}</div><div><b>{{ profile.name }}</b><p class="mt-1 text-sm leading-6 text-zinc-500">{{ profile.title }}，关注现代 Web 开发、AI 工具与工程效率。</p></div></div></div><section class="mt-14 border-t border-zinc-200 pt-10 dark:border-zinc-800"><h2 class="text-xl font-bold">评论 <span class="text-sm text-zinc-400">{{ comments.length }}</span></h2><div class="mt-5 rounded-xl border border-zinc-200 p-4"><textarea v-model="comment" rows="3" class="w-full resize-none bg-transparent text-sm outline-none" placeholder="友善交流，分享你的想法..."/><div class="mt-3 flex justify-end border-t pt-3 dark:border-zinc-800"><button class="primary-button h-8" @click="submit"><Send />发表评论</button></div></div><p v-if="message" class="mt-2 text-sm text-teal-600">{{ message }}</p><div class="mt-7 space-y-6"><div v-for="item in comments" :key="item.id" class="flex gap-3"><div class="avatar h-9 w-9 text-xs">{{ item.name.slice(0,2) }}</div><div><b class="text-sm">{{ item.name }}</b><span class="ml-2 text-xs text-zinc-400">{{ item.created_at }}</span><p class="mt-1 text-sm leading-6 text-zinc-500">{{ item.content }}</p></div></div></div></section></article><aside class="hidden lg:block"><nav class="sticky top-24 border-l border-zinc-200 dark:border-zinc-800"><p class="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-zinc-400">本页目录</p><a v-for="heading in headings" :key="heading.id" :href="`#${heading.id}`" class="block px-3 py-1.5 text-xs leading-5 text-zinc-500 hover:text-teal-600">{{ heading.title }}</a></nav></aside></div></main></template>
