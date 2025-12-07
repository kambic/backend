import AuthLayout from '../layouts/AuthLayout.vue'
import { LoginPage, LogoutPage, ProfilePage, RegisterPage } from '@/views/auth'

const routes = {
  path: '/auth',
  component: AuthLayout,
  children: [
    {
      path: '',
      redirect: 'login',
    },
    {
      path: 'login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: 'register',
      name: 'register',
      component: RegisterPage,
    },
    {
      path: 'profile',
      name: 'profile',
      component: ProfilePage,
    },
    {
      path: 'logout',
      name: 'logout',
      component: LogoutPage,
    },
  ],
}

export { routes as AuthRoutes }
