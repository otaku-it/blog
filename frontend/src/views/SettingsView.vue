<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, FolderCog, KeyRound, Plus, Save, Tag, Trash2, UserRound, X } from 'lucide-vue-next'
import { api } from '../api'
import { auth } from '../auth'

const router = useRouter()
const route = useRoute()
const tab = ref(['profile', 'categories', 'tags', 'password'].includes(route.query.tab) ? route.query.tab : 'profile')
const notice = ref('')
const error = ref('')
const profile = reactive({ name: '', initials: '', title: '', hero_intro: '', hero_skills: [], heroSkillsText: '', writing_since_year: 2021, views_baseline: 0, bio: '', story: '', location: '', email: '', github: '', principles: [], stack: [] })
const siteStats = ref({ published_posts: 0, actual_views: 0, views_baseline: 0, total_views: 0, writing_years: 1 })
const password = reactive({ current_password: '', new_password: '', confirm: '' })
const categories = ref([])
const tags = ref([])
const newCategory = ref('')
const newTag = ref('')
const editingCategory = ref('')
const editingTag = ref('')
const loading = ref(true)
const savingProfile = ref(false)

function flash(message) { notice.value = message; error.value = ''; setTimeout(() => { notice.value = '' }, 2800) }
function hydrateProfile(data) {
  Object.assign(profile, data, {
    hero_skills: Array.isArray(data.hero_skills) ? [...data.hero_skills] : [],
    heroSkillsText: Array.isArray(data.hero_skills) ? data.hero_skills.join(', ') : '',
    principles: (data.principles || []).map(item => ({ ...item })),
    stack: (data.stack || []).map(group => ({
      group: group.group || '',
      items: Array.isArray(group.items) ? [...group.items] : [],
      itemsText: Array.isArray(group.items) ? group.items.join(', ') : '',
    })),
  })
}
function parseStackItems(value) {
  return [...new Set((value || '').split(/[,，\n]/).map(item => item.trim()).filter(Boolean))]
}
async function load() {
  try {
    const [profileData, categoryData, tagData, statsData] = await Promise.all([api.profile(), api.adminCategories(), api.adminTags(), api.siteStats()])
    hydrateProfile(profileData); categories.value = categoryData; tags.value = tagData; siteStats.value = statsData
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}
async function saveProfile() {
  if (savingProfile.value) return
  savingProfile.value = true
  error.value = ''
  const payload = {
    name: profile.name.trim(), initials: profile.initials.trim(), title: profile.title.trim(),
    hero_intro: profile.hero_intro, hero_skills: parseStackItems(profile.heroSkillsText).slice(0, 8),
    writing_since_year: Number(profile.writing_since_year), views_baseline: Number(profile.views_baseline || 0),
    bio: profile.bio, story: profile.story, location: profile.location.trim(),
    email: profile.email.trim(), github: profile.github.trim(),
    principles: profile.principles.map(item => ({ title: item.title.trim(), description: item.description.trim() })).filter(item => item.title || item.description),
    stack: profile.stack.map(group => ({ group: group.group.trim(), items: parseStackItems(group.itemsText) })).filter(group => group.group || group.items.length),
  }
  try {
    const saved = await api.updateProfile(payload)
    hydrateProfile(saved)
    siteStats.value = await api.siteStats()
    flash('关于我资料已保存，前台已同步更新')
  } catch (e) { error.value = e.message }
  finally { savingProfile.value = false }
}
function addPrinciple() { profile.principles.push({ title: '', description: '' }) }
function addStack() { profile.stack.push({ group: '', items: [], itemsText: '' }) }
async function changePassword() {
  if (password.new_password !== password.confirm) { error.value = '两次输入的新密码不一致'; return }
  try { await api.changePassword({ current_password: password.current_password, new_password: password.new_password }); auth.clear(); router.replace('/admin/login') } catch (e) { error.value = e.message }
}
async function saveCategory(category) {
  try {
    if (category.id) await api.updateCategory(category.slug, { name: category.name })
    else if (newCategory.value.trim()) await api.createCategory({ name: newCategory.value.trim() })
    newCategory.value = ''; editingCategory.value = ''; categories.value = (await api.adminCategories())
    flash('分类已保存')
  } catch (e) { error.value = e.message }
}
async function deleteCategory(category) {
  if (category.count) { error.value = `该分类仍有 ${category.count} 篇文章，不能删除`; return }
  try { await api.deleteCategory(category.slug); categories.value = (await api.adminCategories()); flash('空分类已删除') }
  catch (e) { error.value = e.message }
}
async function saveTag(tag) {
  try {
    if (tag.id) await api.updateTag(tag.slug, { name: tag.name })
    else if (newTag.value.trim()) await api.createTag({ name: newTag.value.trim() })
    newTag.value = ''; editingTag.value = ''; tags.value = await api.adminTags()
    flash('标签已保存')
  } catch (e) { error.value = e.message }
}
async function deleteTag(tag) {
  if (tag.count) { error.value = `该标签仍被 ${tag.count} 篇文章使用，不能删除`; return }
  try { await api.deleteTag(tag.slug); tags.value = await api.adminTags(); flash('空标签已删除') }
  catch (e) { error.value = e.message }
}
onMounted(load)
</script>

<template>
  <main class="min-h-[calc(100vh-4rem)] bg-zinc-50 px-4 py-8 dark:bg-zinc-950 sm:px-6 lg:px-8"><div class="mx-auto max-w-6xl"><div class="flex flex-col gap-3 sm:flex-row sm:items-end"><div><p class="eyebrow">Settings</p><h1 class="mt-1 text-3xl font-bold">站点设置</h1><p class="mt-2 text-sm text-zinc-500">维护公开资料、文章分类、标签和管理员密码。</p></div><RouterLink to="/admin" class="secondary-button sm:ml-auto">返回后台</RouterLink></div><div class="mt-8 grid gap-6 lg:grid-cols-[220px_1fr]"><nav class="h-fit rounded-xl border border-zinc-200 bg-white p-2 dark:border-zinc-800 dark:bg-zinc-900"><button class="settings-tab" :class="{active:tab==='profile'}" @click="tab='profile'"><UserRound/>关于我</button><button class="settings-tab" :class="{active:tab==='categories'}" @click="tab='categories'"><FolderCog/>文章分类</button><button class="settings-tab" :class="{active:tab==='tags'}" @click="tab='tags'"><Tag/>文章标签</button><button class="settings-tab" :class="{active:tab==='password'}" @click="tab='password'"><KeyRound/>登录密码</button></nav><section class="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900"><div v-if="loading" class="py-16 text-center text-sm text-zinc-400">正在加载设置...</div><template v-else><p v-if="notice" class="mb-4 flex items-center gap-2 rounded-lg bg-teal-50 px-3 py-2 text-sm text-teal-700 dark:bg-teal-950/40 dark:text-teal-300"><Check/>{{ notice }}</p><p v-if="error" class="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600 dark:bg-rose-950/40">{{ error }}</p>
          <div v-if="tab==='profile'" class="space-y-6"><div><h2 class="text-xl font-bold">关于我</h2><p class="mt-1 text-sm text-zinc-500">这些内容会同步到首页作者卡片、文章作者信息和关于我页面。</p></div><div class="grid gap-4 sm:grid-cols-2"><label><span class="field-label">姓名</span><input v-model="profile.name" class="settings-input" /></label><label><span class="field-label">头像缩写</span><input v-model="profile.initials" class="settings-input" /></label><label class="sm:col-span-2"><span class="field-label">职业标题</span><input v-model="profile.title" class="settings-input" /></label><label><span class="field-label">所在位置</span><input v-model="profile.location" class="settings-input" /></label><label><span class="field-label">联系邮箱</span><input v-model="profile.email" class="settings-input" /></label><label class="sm:col-span-2"><span class="field-label">GitHub 地址</span><input v-model="profile.github" class="settings-input" /></label><label class="sm:col-span-2"><span class="field-label">作者简介（首页侧栏）</span><textarea v-model="profile.bio" rows="3" class="settings-input h-auto py-3" /></label><label class="sm:col-span-2"><span class="field-label">详细介绍（空行分段）</span><textarea v-model="profile.story" rows="6" class="settings-input h-auto py-3" /></label></div><div class="border-t border-zinc-200 pt-5 dark:border-zinc-800"><div><h3 class="font-semibold">首页首屏内容</h3><p class="text-xs text-zinc-400">对应首页顶部的介绍文案、技能标签与真实统计。</p></div><div class="mt-4 grid gap-4"><label><span class="field-label">首屏介绍文案</span><textarea v-model="profile.hero_intro" rows="4" class="settings-input h-auto py-3" placeholder="输入首页顶部介绍文案" /></label><label><span class="field-label">首屏技能标签 <em>最多 8 个，支持中英文逗号或换行</em></span><input v-model="profile.heroSkillsText" class="settings-input" placeholder="React, Next.js, AI" /></label><div class="grid gap-3 sm:grid-cols-3"><div class="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50"><span class="field-label">已发布文章</span><b class="mt-1 block text-xl">{{ siteStats.published_posts }}</b><p class="text-[11px] text-zinc-400">由文章状态自动统计</p></div><div class="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50"><span class="field-label">真实访问量</span><b class="mt-1 block text-xl">{{ siteStats.actual_views }}</b><p class="text-[11px] text-zinc-400">公开文章浏览量合计</p></div><div class="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50"><span class="field-label">当前写作年限</span><b class="mt-1 block text-xl">{{ siteStats.writing_years }} 年</b><p class="text-[11px] text-zinc-400">根据起始年份计算</p></div></div><div class="grid gap-4 sm:grid-cols-2"><label><span class="field-label">历史阅读量基数 <em>用于补录迁移前的真实阅读量</em></span><input v-model.number="profile.views_baseline" type="number" min="0" class="settings-input" /></label><label><span class="field-label">开始写作年份</span><input v-model.number="profile.writing_since_year" type="number" min="1970" :max="new Date().getFullYear()" class="settings-input" /></label></div><p class="text-xs text-zinc-400">首页阅读量 = 历史基数 + 当前文章真实浏览量；文章数随发布、转草稿或删除自动变化。</p></div></div><div class="border-t border-zinc-200 pt-5 dark:border-zinc-800"><div class="flex items-center"><div><h3 class="font-semibold">个人原则</h3><p class="text-xs text-zinc-400">展示在“我在意的事情”区域。</p></div><button class="secondary-button ml-auto h-8" @click="addPrinciple"><Plus/>添加</button></div><div class="mt-4 space-y-3"><div v-for="(item,index) in profile.principles" :key="index" class="grid gap-2 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50 sm:grid-cols-[180px_1fr_auto]"><input v-model="item.title" class="settings-input mt-0" placeholder="原则标题"/><input v-model="item.description" class="settings-input mt-0" placeholder="原则说明"/><button class="icon-button" @click="profile.principles.splice(index,1)"><X/></button></div></div></div><div class="border-t border-zinc-200 pt-5 dark:border-zinc-800"><div class="flex items-center"><div><h3 class="font-semibold">技术栈</h3><p class="text-xs text-zinc-400">支持中文逗号、英文逗号或换行分隔。</p></div><button class="secondary-button ml-auto h-8" @click="addStack"><Plus/>添加</button></div><div class="mt-4 space-y-3"><div v-for="(group,index) in profile.stack" :key="index" class="grid gap-2 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800/50 sm:grid-cols-[180px_1fr_auto]"><input v-model="group.group" class="settings-input mt-0" placeholder="分组名称"/><input v-model="group.itemsText" class="settings-input mt-0" placeholder="Vue, Python, Docker"/><button class="icon-button" @click="profile.stack.splice(index,1)"><X/></button></div></div></div><div class="flex justify-end"><button class="primary-button" :disabled="savingProfile" @click="saveProfile"><Save/>{{ savingProfile ? '保存中...' : '保存关于我' }}</button></div></div>
          <div v-else-if="tab==='categories'"><h2 class="text-xl font-bold">文章分类</h2><p class="mt-1 text-sm text-zinc-500">分类会同步到新建文章编辑器和公开分类页；文章可在文章管理中删除。</p><div class="mt-5 flex gap-2"><input v-model="newCategory" class="settings-input" placeholder="输入新分类名称" @keydown.enter.prevent="saveCategory({})"/><button class="primary-button" @click="saveCategory({})">新增分类</button></div><div class="mt-6 divide-y divide-zinc-100 dark:divide-zinc-800"><div v-for="category in categories" :key="category.id" class="flex items-center gap-3 py-3"><input v-if="editingCategory===category.id" v-model="category.name" class="settings-input h-9" @keydown.enter="saveCategory(category)"/><div v-else class="min-w-0 flex-1"><b>{{ category.name }}</b><p class="text-xs text-zinc-400">{{ category.count }} 篇文章</p></div><button v-if="editingCategory===category.id" class="secondary-button h-9" @click="saveCategory(category)">保存</button><button v-else class="secondary-button h-9" @click="editingCategory=category.id">编辑</button><button class="icon-button text-rose-500" :disabled="category.count>0" :title="category.count ? '有文章的分类不能删除' : '删除空分类'" @click="deleteCategory(category)"><Trash2/></button></div></div></div>
          <div v-else-if="tab==='tags'"><h2 class="text-xl font-bold">文章标签</h2><p class="mt-1 text-sm text-zinc-500">统一维护标签名称，避免出现大小写不同或含义重复的近似标签。</p><div class="mt-5 flex gap-2"><input v-model="newTag" class="settings-input" placeholder="输入新标签名称" @keydown.enter.prevent="saveTag({})"/><button class="primary-button" @click="saveTag({})">新增标签</button></div><div class="mt-6 divide-y divide-zinc-100 dark:divide-zinc-800"><div v-for="item in tags" :key="item.id" class="flex items-center gap-3 py-3"><input v-if="editingTag===item.id" v-model="item.name" class="settings-input h-9" @keydown.enter="saveTag(item)"/><div v-else class="min-w-0 flex-1"><b># {{ item.name }}</b><p class="text-xs text-zinc-400">{{ item.count }} 篇文章使用</p></div><button v-if="editingTag===item.id" class="secondary-button h-9" @click="saveTag(item)">保存</button><button v-else class="secondary-button h-9" @click="editingTag=item.id">编辑</button><button class="icon-button text-rose-500" :disabled="item.count>0" :title="item.count ? '使用中的标签不能删除' : '删除空标签'" @click="deleteTag(item)"><Trash2/></button></div></div></div>
          <div v-else class="max-w-xl"><h2 class="text-xl font-bold">修改登录密码</h2><p class="mt-1 text-sm text-zinc-500">修改成功后当前登录会失效，需要用新密码重新登录。</p><div class="mt-6 space-y-4"><label><span class="field-label">当前密码</span><input v-model="password.current_password" type="password" class="settings-input" autocomplete="current-password" /></label><label><span class="field-label">新密码（至少 8 位）</span><input v-model="password.new_password" type="password" class="settings-input" autocomplete="new-password" /></label><label><span class="field-label">确认新密码</span><input v-model="password.confirm" type="password" class="settings-input" autocomplete="new-password" /></label></div><div class="mt-5 flex justify-end"><button class="primary-button" @click="changePassword"><KeyRound/>更新密码</button></div></div>
        </template></section></div></div></main>
</template>
