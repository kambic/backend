<template>
  <div class="card w-96 bg-base-100 card-compact shadow-xl sm:w-1/3 max-w-sm">
    <figure>
      <img width="400" height="225" :src="`https://picsum.photos/400/225?${id}`" alt="Shoes" />
    </figure>
    <div class="card-body">
      <h2 class="card-title">{{ title }}</h2>
      <div class="justify-end card-actions">
        <RouterLink :to="`/simple/posts/${id}`" class="btn btn-primary">Read</RouterLink>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { title: String, id: Number },
}
</script>
