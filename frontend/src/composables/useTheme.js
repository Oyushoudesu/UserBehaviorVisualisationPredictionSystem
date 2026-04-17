import { ref } from 'vue'

const isDark = ref(false)

export function useTheme() {
  const init = () => {
    const stored = localStorage.getItem('theme')
    isDark.value = stored
      ? stored === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  const toggle = () => {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  return { isDark, toggle, init }
}
