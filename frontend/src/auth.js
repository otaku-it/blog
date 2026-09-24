import { computed, reactive } from 'vue'

const state = reactive({
  token: localStorage.getItem('admin_token') || '',
  user: JSON.parse(localStorage.getItem('admin_user') || 'null'),
})

export const auth = {
  state,
  isAuthenticated: computed(() => Boolean(state.token)),
  setSession(data) {
    state.token = data.access_token
    state.user = data.user
    localStorage.setItem('admin_token', data.access_token)
    localStorage.setItem('admin_user', JSON.stringify(data.user))
  },
  clear() {
    state.token = ''
    state.user = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  },
}
