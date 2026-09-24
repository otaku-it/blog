<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bold, Code2, FileCode2, Heading1, Heading2, Heading3, Image, Italic, Link, List, ListOrdered, LoaderCircle, Maximize2, Minimize2, Minus, Quote, Save, Send, Sparkles, Table2 } from 'lucide-vue-next'
import { marked } from 'marked'
import { api } from '../api'

const route = useRoute()
const router = useRouter()
const editor = ref(null)
const fileInput = ref(null)
const slug = ref(route.params.id || '')
const title = ref('')
const excerpt = ref('')
const category = ref('技术随笔')
const tags = ref([])
const categoryOptions = ref([])
const tagOptions = ref([])
const tagInput = ref('')
const content = ref('')
const status = ref('draft')
const saving = ref(false)
const loading = ref(Boolean(slug.value))
const notice = ref('')
const error = ref('')
const activeTab = ref('split')
const fullscreen = ref(false)
const uploading = ref(false)
const imageWidth = ref('100%')

const preview = computed(() => marked.parse(content.value || '*开始写作，右侧会实时显示预览*'))
const wordCount = computed(() => content.value.replace(/\s/g, '').length)
const readingTime = computed(() => `${Math.max(1, Math.ceil(wordCount.value / 450))} 分钟阅读`)
const headings = computed(() => [...content.value.matchAll(/^#{1,2}\s+(.+)$/gm)].map(match => match[1]))
const availableTagOptions = computed(() => tagOptions.value.filter(item => !tags.value.includes(item.name)).slice(0, 12))
const starter = '# 一篇值得被认真记录的文章\n\n从一个真实问题开始，写下你的判断、过程和结论。\n\n## 背景\n\n> 好的技术文章，不只给出答案，也解释为什么。\n\n## 实践\n\n```ts\nconst result = await buildSomethingUseful()\n```\n\n## 总结\n\n把复杂问题讲清楚，让经验可以被复用。'

async function load() {
  const [categoryData, tagData] = await Promise.all([api.adminCategories(), api.adminTags()])
  categoryOptions.value = categoryData; tagOptions.value = tagData
  if (!slug.value) { title.value = '未命名文章'; content.value = starter; category.value = categoryOptions.value[0]?.name || '技术随笔'; return }
  try {
    const post = await api.adminPost(slug.value)
    title.value = post.title; excerpt.value = post.excerpt; category.value = post.category === '未分类' ? '技术随笔' : post.category
    tags.value = [...post.tags]; content.value = post.content; status.value = post.status
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}
function addTag() { const value = tagInput.value.trim(); if (value && !tags.value.includes(value) && tags.value.length < 5) tags.value.push(value); tagInput.value = '' }
function selectTag(value) { if (!tags.value.includes(value) && tags.value.length < 5) tags.value.push(value) }
function removeTag(value) { tags.value = tags.value.filter(item => item !== value) }
function insert(before, after = '') {
  const target = editor.value; const start = target.selectionStart; const end = target.selectionEnd; const selected = content.value.slice(start, end) || '文本'
  content.value = `${content.value.slice(0, start)}${before}${selected}${after}${content.value.slice(end)}`
  nextTick(() => { target.focus(); target.setSelectionRange(start + before.length, start + before.length + selected.length) })
}
function insertLine(value) {
  const target = editor.value
  const start = target.selectionStart
  const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
  content.value = `${content.value.slice(0, lineStart)}${value}${content.value.slice(lineStart)}`
  nextTick(() => { target.focus(); target.setSelectionRange(start + value.length, start + value.length) })
}
function openFilePicker() { fileInput.value?.click() }
function escapeAttribute(value) {
  return String(value || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
function resourceMarkup(resource) {
  if (!resource.content_type?.startsWith('image/')) return resource.markdown
  return `<img src="${resource.url}" alt="${escapeAttribute(resource.name)}" style="width: ${imageWidth.value}; max-width: 100%; height: auto;" />`
}
function normalizeClipboardFile(file) {
  if (/\.[a-z0-9]+$/i.test(file.name || '')) return file
  const extension = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/webp': 'webp', 'image/avif': 'avif' }[file.type] || 'png'
  return new File([file], `clipboard-${Date.now()}.${extension}`, { type: file.type })
}
async function uploadAndInsert(file, position = editor.value?.selectionStart ?? content.value.length) {
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const resource = await api.uploadResource(file)
    const target = editor.value
    const markup = resourceMarkup(resource)
    content.value = `${content.value.slice(0, position)}${markup}${content.value.slice(position)}`
    await nextTick()
    target?.focus()
    const nextPosition = position + markup.length
    target?.setSelectionRange(nextPosition, nextPosition)
    notice.value = `${file.name} 已上传并插入正文${resource.content_type?.startsWith('image/') ? `，显示宽度 ${imageWidth.value}` : ''}`
  } catch (e) { error.value = e.message }
  finally { uploading.value = false }
}
async function uploadResource(event) {
  const file = event.target.files?.[0]
  const position = editor.value?.selectionStart ?? content.value.length
  event.target.value = ''
  await uploadAndInsert(file, position)
}
async function pasteResource(event) {
  const imageItem = [...(event.clipboardData?.items || [])].find(item => item.type.startsWith('image/'))
  if (!imageItem) return
  event.preventDefault()
  const position = event.target.selectionStart ?? content.value.length
  await uploadAndInsert(normalizeClipboardFile(imageItem.getAsFile()), position)
}
async function dropResource(event) {
  const file = [...(event.dataTransfer?.files || [])].find(item => item.type.startsWith('image/') || /\.(pdf|txt|csv|zip)$/i.test(item.name))
  if (!file) return
  const position = editor.value?.selectionStart ?? content.value.length
  await uploadAndInsert(file, position)
}
async function save(nextStatus = 'draft') {
  error.value = ''; notice.value = ''
  if (!title.value.trim() || !content.value.trim()) { error.value = '标题和正文不能为空'; return }
  saving.value = true
  try {
    const payload = { title: title.value.trim(), excerpt: excerpt.value.trim(), content: content.value, tags: tags.value, category: category.value.trim() || '技术随笔', status: nextStatus }
    const article = slug.value ? await api.updatePost(slug.value, payload) : await api.createPost(payload)
    slug.value = article.id; status.value = nextStatus
    notice.value = nextStatus === 'published' ? '文章已发布，正在打开文章页...' : '草稿已保存到 MySQL，可以稍后在后台继续编辑。'
    if (!route.params.id) await router.replace(`/admin/write/${article.id}`)
    if (nextStatus === 'published') setTimeout(() => router.push(`/articles/${article.id}`), 450)
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}
onMounted(load)
</script>

<template>
  <main class="min-h-[calc(100vh-4rem)] bg-zinc-50 px-3 py-5 dark:bg-zinc-950 sm:px-6 lg:px-8">
    <div v-if="loading" class="mx-auto max-w-7xl py-24 text-center text-sm text-zinc-400"><LoaderCircle class="mx-auto mb-3 animate-spin" />正在加载草稿...</div>
    <div v-else class="mx-auto max-w-[1540px]">
      <header class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center"><div class="min-w-0"><div class="flex items-center gap-2 text-xs text-zinc-400"><RouterLink to="/admin" class="hover:text-teal-600">内容后台</RouterLink><span>/</span><span>{{ slug ? '编辑文章' : '新建文章' }}</span></div><h1 class="mt-2 truncate text-2xl font-bold">{{ title || '新建文章' }}</h1><p class="mt-1 text-xs text-zinc-400">{{ status === 'published' ? '已发布 · 修改后会同步更新线上文章' : '草稿 · 只有管理员可以查看和编辑' }}</p></div><div class="flex flex-wrap gap-2 lg:ml-auto"><RouterLink to="/admin" class="secondary-button">返回文章管理</RouterLink><button class="secondary-button" :disabled="saving" @click="save('draft')"><Save />{{ saving ? '保存中...' : '保存草稿' }}</button><button class="primary-button" :disabled="saving" @click="save('published')"><Send />发布文章</button></div></header>
      <p v-if="notice" class="mb-4 rounded-lg border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-700 dark:border-teal-900 dark:bg-teal-950/50 dark:text-teal-300">{{ notice }}</p><p v-if="error" class="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-300">{{ error }}</p>
      <section class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_330px]"><div class="space-y-4"><label class="block rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900"><span class="field-label">文章标题</span><input v-model="title" class="mt-2 w-full bg-transparent text-2xl font-bold tracking-tight outline-none placeholder:text-zinc-300 dark:placeholder:text-zinc-700" placeholder="输入一个清晰的标题" /></label><label class="block rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900"><span class="field-label">文章摘要</span><textarea v-model="excerpt" rows="2" class="mt-2 w-full resize-none bg-transparent text-sm leading-6 outline-none placeholder:text-zinc-300 dark:placeholder:text-zinc-700" placeholder="用一两句话告诉读者，这篇文章解决什么问题" /></label>
          <section class="overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900" :class="fullscreen ? 'fixed inset-3 z-[80] flex flex-col shadow-2xl dark:shadow-black/50' : ''"><div class="flex flex-wrap items-center gap-1 border-b border-zinc-200 px-3 py-2 dark:border-zinc-800"><span class="mr-2 text-xs font-semibold uppercase tracking-widest text-zinc-400">编辑器</span><button class="editor-tool" title="一级标题" @click="insertLine('# ')"><Heading1 /></button><button class="editor-tool" title="二级标题" @click="insertLine('## ')"><Heading2 /></button><button class="editor-tool" title="三级标题" @click="insertLine('### ')"><Heading3 /></button><button class="editor-tool" title="粗体" @click="insert('**', '**')"><Bold /></button><button class="editor-tool" title="斜体" @click="insert('*', '*')"><Italic /></button><button class="editor-tool" title="引用" @click="insertLine('> ')"><Quote /></button><button class="editor-tool" title="行内代码" @click="insert('`', '`')"><Code2 /></button><button class="editor-tool" title="代码块" @click="insert('```ts\n', '\n```')"><FileCode2 /></button><button class="editor-tool" title="链接" @click="insert('[', '](https://)')"><Link /></button><select v-model="imageWidth" class="h-8 rounded-md border border-zinc-200 bg-transparent px-1.5 text-xs outline-none dark:border-zinc-700" title="新插入图片的显示宽度"><option value="25%">图片 25%</option><option value="50%">图片 50%</option><option value="75%">图片 75%</option><option value="100%">图片 100%</option><option value="320px">图片 320px</option><option value="480px">图片 480px</option><option value="720px">图片 720px</option></select><button class="editor-tool" title="上传图片或资源；也可直接粘贴图片" :disabled="uploading" @click="openFilePicker"><LoaderCircle v-if="uploading" class="animate-spin"/><Image v-else /></button><input ref="fileInput" type="file" class="hidden" accept="image/*,.pdf,.txt,.csv,.zip" @change="uploadResource" /><button class="editor-tool" title="无序列表" @click="insertLine('- ')"><List /></button><button class="editor-tool" title="有序列表" @click="insertLine('1. ')"><ListOrdered /></button><button class="editor-tool" title="表格" @click="insert('\n| 列 1 | 列 2 |\n| --- | --- |\n| 内容 | 内容 |\n', '')"><Table2 /></button><button class="editor-tool" title="分割线" @click="insertLine('---\n')"><Minus /></button><span class="ml-auto flex items-center gap-1"><button class="editor-tool" :title="fullscreen ? '退出全屏' : '全屏编辑'" @click="fullscreen=!fullscreen"> <Minimize2 v-if="fullscreen"/><Maximize2 v-else/></button><span class="flex rounded-md bg-zinc-100 p-0.5 text-xs dark:bg-zinc-800"><button class="rounded px-2 py-1" :class="activeTab==='write'?'bg-white shadow dark:bg-zinc-700':''" @click="activeTab='write'">写作</button><button class="rounded px-2 py-1" :class="activeTab==='split'?'bg-white shadow dark:bg-zinc-700':''" @click="activeTab='split'">分屏</button><button class="rounded px-2 py-1" :class="activeTab==='preview'?'bg-white shadow dark:bg-zinc-700':''" @click="activeTab='preview'">预览</button></span></span></div><div class="grid min-h-[620px] flex-1" :class="activeTab==='split'?'lg:grid-cols-2':''"><textarea v-show="activeTab !== 'preview'" ref="editor" v-model="content" spellcheck="false" class="min-h-[620px] w-full resize-none bg-transparent p-5 font-mono text-sm leading-7 outline-none lg:border-r lg:border-zinc-200 dark:lg:border-zinc-800" placeholder="使用 Markdown 开始写作；可直接粘贴或拖入图片..." @paste="pasteResource" @drop.prevent="dropResource" @dragover.prevent/><div v-show="activeTab !== 'write'" class="article-body min-h-[620px] overflow-auto p-6" v-html="preview"/></div><div class="flex flex-wrap items-center gap-4 border-t border-zinc-200 px-4 py-2 text-xs text-zinc-400 dark:border-zinc-800"><span>{{ wordCount.toLocaleString() }} 字</span><span>{{ readingTime }}</span><span>{{ headings.length }} 个章节</span><span>可粘贴/拖入图片 · 当前图片宽度 {{ imageWidth }}</span><span class="ml-auto flex items-center gap-1 text-teal-600"><Sparkles class="h-3.5 w-3.5"/>实时预览已开启</span></div></section></div>
        <aside class="space-y-4"><section class="panel"><h2 class="panel-title">发布设置</h2><label class="mt-4 block"><span class="field-label">文章分类</span><select v-model="category" class="mt-2 h-10 w-full rounded-lg border border-zinc-200 bg-transparent px-3 text-sm outline-none focus:border-teal-500 dark:border-zinc-700"><option v-for="item in categoryOptions" :key="item.id" :value="item.name">{{ item.name }}</option></select></label><RouterLink :to="{path:'/admin/settings',query:{tab:'categories'}}" class="mt-2 inline-block text-xs text-teal-600">维护文章分类 →</RouterLink><div class="mt-4"><span class="field-label">文章标签 <em>最多 5 个</em></span><div class="mt-2 flex min-h-10 flex-wrap gap-1.5 rounded-lg border border-zinc-200 p-2 dark:border-zinc-700"><span v-for="item in tags" :key="item" class="tag-pill">{{ item }} <button @click="removeTag(item)">×</button></span><input v-model="tagInput" class="min-w-20 flex-1 bg-transparent px-1 text-sm outline-none" placeholder="输入后回车" @keydown.enter.prevent="addTag" /></div><div v-if="availableTagOptions.length" class="mt-2 flex flex-wrap gap-1.5"><button v-for="item in availableTagOptions" :key="item.id" class="rounded-md bg-zinc-100 px-2 py-1 text-[11px] text-zinc-500 hover:bg-teal-50 hover:text-teal-700 dark:bg-zinc-800 dark:hover:bg-teal-950" @click="selectTag(item.name)">+ {{ item.name }}</button></div><RouterLink :to="{path:'/admin/settings',query:{tab:'tags'}}" class="mt-2 inline-block text-xs text-teal-600">维护文章标签 →</RouterLink></div></section><section class="panel"><h2 class="panel-title">文章目录</h2><div v-if="headings.length" class="mt-4 space-y-2"><p v-for="(heading, index) in headings" :key="index" class="truncate text-sm text-zinc-500"><span class="mr-2 font-mono text-xs text-teal-600">0{{ index + 1 }}</span>{{ heading }}</p></div><p v-else class="mt-4 text-sm text-zinc-400">添加 ## 标题后，会自动生成目录。</p></section><section class="rounded-xl border border-dashed border-teal-300 bg-teal-50/60 p-4 dark:border-teal-900 dark:bg-teal-950/30"><p class="text-sm font-semibold text-teal-800 dark:text-teal-300">后台权限已启用</p><p class="mt-2 text-xs leading-5 text-teal-700/80 dark:text-teal-400">只有管理员登录后才能保存或发布。草稿不会出现在公开文章列表中。</p></section></aside>
      </section>
    </div>
  </main>
</template>
