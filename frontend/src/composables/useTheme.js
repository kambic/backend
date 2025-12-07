import { ref, onMounted, onUnmounted } from 'vue'
const storageKey = 'theme'
const defaultTheme = 'system'
const availableThemes = [
  { name: 'system' },
  { name: 'light' },
  { name: 'dark' },
  { name: 'cupcake' },
  { name: 'retro' },
  { name: 'valentine' },
  { name: 'business' },
  { name: 'coffee' },
  { name: 'nord' },
]

// by convention, composable function names start with "use"
export function useTheme() {
  // state encapsulated and managed by the composable
  const x = ref(0)
  const currentTheme = ref(0)

  // a composable can update its managed state over time.
  // Zistí, akú tému by mal použiť systém
  function detect() {
    const saved = localStorage.getItem(storageKey) || this.defaultTheme
    if (saved && this.availableThemes.map((theme) => theme.name).includes(saved)) {
      return saved
    }
    return this.prefersDark() ? 'dark' : 'light'
  }

  // Aplikuje danú tému a uloží ju do localStorage
  function apply(newTheme) {
    if (newTheme === this.defaultTheme) {
      // Uloží "system", ale vzhled na stránce nastaví podle preferencí
      localStorage.setItem(storageKey, 'system')
      document.documentElement.setAttribute('data-theme', this.prefersDark() ? 'dark' : 'light')
    } else {
      // Uloží zvolenou čitelnou hodnotu, např. "dark" nebo "light"
      document.documentElement.setAttribute('data-theme', newTheme)
      localStorage.setItem(storageKey, newTheme)
    }
    this.currentTheme.value = newTheme
  }
  function prefersDark() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  // a composable can also hook into its owner component's
  // lifecycle to setup and teardown side effects.
  onMounted(() => window.addEventListener('mousemove', update))
  onUnmounted(() => window.removeEventListener('mousemove', update))

  // expose managed state as return value
  return { currentTheme }
}
