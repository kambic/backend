// src/composables/useVueFinder.js
import { ref, computed, watch } from 'vue'
import { RemoteDriver } from 'vuefinder'
import { defineStore } from 'pinia'

const useFinderStore = defineStore('vuefinder', {
  state: () => ({
    currentPath: 'local://public/',
    history: [],
    historyIndex: -1,
  }),
  actions: {
    goTo(path) {
      if (this.currentPath === path) return
      if (this.historyIndex < this.history.length - 1) {
        this.history = this.history.slice(0, this.historyIndex + 1)
      }
      this.history.push(path)
      this.historyIndex = this.history.length - 1
      this.currentPath = path
    },
    goBack() { if (this.historyIndex > 0) { this.historyIndex--; this.currentPath = this.history[this.historyIndex] } },
    goForward() { if (this.historyIndex < this.history.length - 1) { this.historyIndex++; this.currentPath = this.history[this.historyIndex] } },
    canGoBack() { return this.historyIndex > 0 },
    canGoForward() { return this.historyIndex < this.history.length - 1 },
  },
  persist: true,
})

let driverInstance = null

export function useVueFinder(config = {}) {
  const store = useFinderStore()
  const baseURL = config.baseURL || '/api'
  const initialPath = config.initialPath || 'local://public/'

  if (!driverInstance) {
    driverInstance = new RemoteDriver({
      baseURL,
      url: {
        list: '/files/',
        upload: '/files/upload/',
        delete: '/files/delete/',
        rename: '/files/patch/',
        createFile: '/files/put/',
        createFolder: '/files/put/',
        move: '/files/patch/',
        copy: '/files/patch/',
        save: '/files/put/',
        download: '/files/',
        preview: '/files/',
        search: '/files/',
      },
    })
  }

  const driver = driverInstance

  watch(() => store.currentPath, newPath => {
    if (driver.currentPath !== newPath) driver.goTo(newPath)
  })

  if (store.currentPath === 'local://public/' && initialPath !== store.currentPath) {
    store.goTo(initialPath)
  } else {
    driver.goTo(store.currentPath)
  }

  const currentPath = computed(() => store.currentPath)
  const canGoBack = computed(() => store.canGoBack())
  const canGoForward = computed(() => store.canGoForward())

  return {
    driver,
    currentPath,
    canGoBack,
    canGoForward,
    goBack: () => store.goBack(),
    goForward: () => store.goForward(),
    goTo: (p) => store.goTo(p),
    refresh: () => driver.refresh(),
  }
}
