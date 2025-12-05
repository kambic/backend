// src/router/auth.router.js
import AuthLayout from "../layouts/AuthLayout.vue";
import LoginPage from "../views/auth/LoginPage.vue";
import RegisterPage from "../views/auth/RegisterPage.vue";

export default {
  path: "/auth",
  component: AuthLayout,
  children: [
    {
      path: "login",
      name: "login",
      component: LoginPage,
    },
    {
      path: "register",
      name: "register",
      component: RegisterPage,
    },
  ],
};
