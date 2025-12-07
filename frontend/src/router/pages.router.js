import SimpleLayout from '@/layouts/SimpleLayout.vue'

const routes = {
  path: '/simple',
  component: SimpleLayout,
  children: [
    {
      path: '',
      component: () => import('../pages/Home.vue'),
    },
    {
      path: 'about',
      components: {
        default: () => import('../pages/AboutShow.vue'),
        LeftSidebar: () => import('../components/ui/SidebarOne.vue'),
        RightSidebar: () => import('../components/ui/SidebarTwo.vue'),
      },
    },
    {
      path: 'posts',
      components: {
        default: () => import('../pages/PostIndex.vue'),
        RightSidebar: () => import('../components/ui/SidebarOne.vue'),
      },
    },
    {
      path: 'posts/:id',
      components: {
        default: () => import('../pages/PostShow.vue'),
        RightSidebar: () => import('../components/ui/SidebarTwo.vue'),
      },
    },
  ],
}

export { routes as PageRoutes }
