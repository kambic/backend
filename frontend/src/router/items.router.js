import { MainLayout } from '@/layouts/index.js'
import { ItemView, LogoutView, HelloView } from '@/views/item/index.js'

const routes = {
  path: '/items',
  component: MainLayout,
  children: [
    {
      path: '',
      redirect: 'item',
    },
    {
      path: 'item',
      name: 'item',
      component: ItemView,
    },
    {
      path: 'hello',
      name: 'hello',
      component: HelloView,
    },
    {
      path: 'logout',
      name: 'logout',
      component: LogoutView,
    },
  ],
}

export { routes as ItemsRoutes }
