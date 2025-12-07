<template>
  <h2 class="text-2xl font-bold mb-4">Register</h2>

  <form class="space-y-4">
    <input type="text" placeholder="Email" class="input input-bordered w-full" />
    <input type="password" placeholder="Password" class="input input-bordered w-full" />
    <button class="btn btn-secondary w-full">Create Account</button>
  </form>

  <div class="flex flex-col gap-4 rounded-box bg-base-200 p-6 max-w-md">
    <h1 class="text-3xl font-bold self-center">Create an account</h1>

    <span class="self-center">
      Already have an account?
      <a class="link link-secondary">Log in</a>
    </span>

    <a class="btn btn-neutral">
      <i class="fa-brands fa-google text-primary"></i>
      Create with Google
    </a>

    <div class="divider my-0">OR</div>

    <label class="form-control">
      <div class="label">
        <span class="label-text">Email</span>
      </div>

      <input class="input input-bordered" />
    </label>

    <label class="form-control">
      <div class="label">
        <span class="label-text">Password</span>
      </div>

      <input type="password" class="input input-bordered" />
    </label>

    <label class="form-control">
      <div class="label">
        <span class="label-text">Confirm password</span>
      </div>

      <input type="password" class="input input-bordered" />
    </label>

    <div class="form-control">
      <label class="cursor-pointer label self-start gap-2">
        <input type="checkbox" class="checkbox" />
        <span class="label-text">
          I accept the
          <a class="link link-accent">Terms and Conditions</a>
        </span>
      </label>
    </div>

    <button class="btn btn-primary">Create</button>
  </div>
</template>

<script setup></script>
