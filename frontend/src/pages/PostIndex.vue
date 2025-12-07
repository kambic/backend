<template>
  <div class="flex flex-wrap gap-6 justify-center content-start">
    <PostCard title="Post 1" :id="1" />
    <PostCard title="Post 2" :id="2" />
    <PostCard title="Post 3" :id="3" />
    <PostCard title="Post 4" :id="4" />
    <PostCard title="Post 5" :id="5" />
    <PostCard title="Post 6" :id="6" />
  </div>
</template>

<script setup>
import PostCard from '@/components/posts/PostCard.vue'
</script>
