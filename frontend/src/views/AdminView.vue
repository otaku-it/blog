<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, Clock3, FileText, PenLine, Plus, Search, Send, Trash2, X } from 'lucide-vue-next'
import { api } from '../api'
import { auth } from '../auth'

const router = useRouter()
const posts = ref([])
const filter = ref('all')
const query = ref('')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const allTotal = ref(0)
const publishedTotal = ref(0)
const draftTotal = ref(0)
const loading = ref(true)
const error = ref('')
const pendingDelete = ref(null)
const deleting = ref(false)
let searchTimer
let requestId = 0

const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const visiblePages = computed(() => {
  const start = Math.max(1, Math.min(page.value - 2, pages.value - 4))
  const end = Math.min(pages.value, start + 4)
  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
})
const filters = computed(() => [
  { value: 'all', label: '全部', count: allTotal.value },
  { value: 'draft', label: '草稿', count: draftTotal.value },
  { value: 'published', label: '已发布', count: publishedTotal.value },
])

async function load() {
  const currentRequest = ++requestId
  loading.value = true
  error.value = ''
  try {
    const result = await api.adminPosts({
      status: filter.value,
      page: page.value,
      page_size: pageSize,
      query: query.value.trim(),
    })
    if (currentRequest !== requestId) return
    posts.value = result.items
    total.value = result.total
    allTotal.value = result.all_total
    publishedTotal.value = result.published_total
    draftTotal.value = result.draft_total
  } catch (requestError) {
    if (currentRequest !== requestId) return
    if (!localStorage.getItem('admin_token')) {
      auth.clear()
      router.replace('/admin/login')
      return
    }
    error.value = requestError.message || '文章列表加载失败'
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

function setFilter(value) {
  if (filter.value === value) return
  filter.value = value
  page.value = 1
  load()
}

function goPage(value) {
  if (value < 1 || value > pages.value || value === page.value) return
  page.value = value
  load()
}

function requestDelete(post) {
  pendingDelete.value = post
}

function closeDeleteDialog() {
  if (!deleting.value) pendingDelete.value = null
}

async function confirmDelete() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  error.value = ''
  try {
    await api.deletePost(pendingDelete.value.id)
    pendingDelete.value = null
    if (posts.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (requestError) {
    if (!localStorage.getItem('admin_token')) {
      auth.clear()
      router.replace('/admin/login')
      return
    }
    error.value = requestError.message || '文章删除失败'
  } finally {
    deleting.value = false
  }
}

watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
})

onMounted(load)
onBeforeUnmount(() => clearTimeout(searchTimer))
</script>

<template>
  <main class="min-h-[calc(100vh-4rem)] bg-zinc-50 px-4 py-8 dark:bg-zinc-950 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div>
          <p class="eyebrow">Content studio</p>
          <h1 class="mt-1 text-3xl font-bold">内容管理后台</h1>
          <p class="mt-2 text-sm text-zinc-500">欢迎回来，{{ auth.state.user?.username }}。管理草稿和已发布文章。</p>
        </div>
        <RouterLink to="/admin/write" class="primary-button sm:ml-auto"><Plus />新建文章</RouterLink>
      </div>

      <section class="mt-8 grid gap-4 sm:grid-cols-3">
        <div class="panel"><FileText class="text-teal-600"/><b class="mt-5 block text-3xl">{{ allTotal }}</b><p class="text-sm text-zinc-500">全部内容</p></div>
        <div class="panel"><Send class="text-sky-600"/><b class="mt-5 block text-3xl">{{ publishedTotal }}</b><p class="text-sm text-zinc-500">已发布</p></div>
        <div class="panel"><Clock3 class="text-amber-600"/><b class="mt-5 block text-3xl">{{ draftTotal }}</b><p class="text-sm text-zinc-500">草稿箱</p></div>
      </section>

      <section class="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div class="border-b border-zinc-200 p-4 dark:border-zinc-800">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div><b>文章管理</b><p class="mt-0.5 text-xs text-zinc-400">按更新时间倒序排列</p></div>
            <div class="relative lg:ml-auto lg:w-64">
              <Search class="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
              <input v-model="query" class="h-9 w-full rounded-md border border-zinc-200 bg-zinc-50 pl-9 pr-3 text-sm outline-none focus:border-teal-500 dark:border-zinc-700 dark:bg-zinc-950" placeholder="搜索标题或正文" />
            </div>
            <div class="flex gap-1 overflow-x-auto">
              <button v-for="item in filters" :key="item.value" class="filter-pill" :class="{ active: filter === item.value }" @click="setFilter(item.value)">{{ item.label }} <span class="ml-1 opacity-60">{{ item.count }}</span></button>
            </div>
          </div>
        </div>

        <div v-if="loading" class="p-10 text-center text-sm text-zinc-400">正在加载内容...</div>
        <div v-else-if="error" class="p-10 text-center"><p class="text-sm text-rose-500">{{ error }}</p><button class="secondary-button mt-4" @click="load">重新加载</button></div>
        <div v-else-if="!posts.length" class="p-12 text-center text-sm text-zinc-400">{{ query ? '没有找到匹配的文章' : '当前没有内容' }}</div>
        <div v-else class="divide-y divide-zinc-100 dark:divide-zinc-800">
          <div v-for="post in posts" :key="post.id" class="flex flex-col gap-3 p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 sm:flex-row sm:items-center">
            <span class="w-fit rounded-full px-2 py-1 text-[11px] font-medium" :class="post.status === 'published' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950' : 'bg-amber-50 text-amber-700 dark:bg-amber-950'">{{ post.status === 'published' ? '已发布' : '草稿' }}</span>
            <div class="min-w-0 flex-1"><b class="block truncate">{{ post.title }}</b><p class="mt-1 truncate text-xs text-zinc-400">{{ post.category }} · 更新于 {{ new Date(post.updated_at).toLocaleString('zh-CN') }}</p></div>
            <div class="flex items-center gap-2">
              <RouterLink :to="`/admin/write/${post.id}`" class="secondary-button h-8"><PenLine />编辑</RouterLink>
              <button class="secondary-button h-8 px-3 text-rose-600 dark:text-rose-400" title="删除文章" @click="requestDelete(post)"><Trash2 />删除</button>
            </div>
          </div>
        </div>

        <div v-if="!loading && !error && total" class="flex flex-col gap-3 border-t border-zinc-200 p-4 dark:border-zinc-800 sm:flex-row sm:items-center">
          <p class="text-sm text-zinc-500">第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 篇</p>
          <div class="flex items-center gap-2 overflow-x-auto sm:ml-auto">
            <button class="secondary-button h-9 px-3" :disabled="page === 1" @click="goPage(page - 1)">上一页</button>
            <button v-for="number in visiblePages" :key="number" class="page-button h-9 w-9" :class="{ active: page === number }" @click="goPage(number)">{{ number }}</button>
            <button class="secondary-button h-9 px-3" :disabled="page === pages" @click="goPage(page + 1)">下一页</button>
          </div>
        </div>
      </section>
    </div>

    <div v-if="pendingDelete" class="fixed inset-0 z-[70] grid place-items-center bg-zinc-950/50 p-4 backdrop-blur-sm" @click.self="closeDeleteDialog">
      <section class="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-5 shadow-2xl dark:border-zinc-800 dark:bg-zinc-900" role="dialog" aria-modal="true" aria-labelledby="delete-title">
        <div class="flex items-start gap-3">
          <span class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400"><AlertTriangle /></span>
          <div class="min-w-0 flex-1"><h2 id="delete-title" class="text-lg font-bold">确认删除文章？</h2><p class="mt-1 text-sm leading-6 text-zinc-500">“{{ pendingDelete.title }}”删除后将从前台和后台同时消失，相关评论也会一并删除，此操作无法撤销。</p></div>
          <button class="icon-button shrink-0" aria-label="关闭" :disabled="deleting" @click="closeDeleteDialog"><X /></button>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <button class="secondary-button" :disabled="deleting" @click="closeDeleteDialog">取消</button>
          <button class="inline-flex h-10 items-center gap-2 rounded-md bg-rose-600 px-4 text-sm font-medium text-white disabled:opacity-50" :disabled="deleting" @click="confirmDelete"><Trash2 />{{ deleting ? '删除中...' : '确认删除' }}</button>
        </div>
      </section>
    </div>
  </main>
</template>
