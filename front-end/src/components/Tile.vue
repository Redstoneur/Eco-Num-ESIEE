<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<template>
  <div class="tile">
    <h1 class="tile-title">{{ title }}</h1>
  </div>
</template>

<style scoped>
.tile {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(to left top, #38b2f3, #2575fc);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: #fff;
}

.tile-title {
  font-size: 2.4rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}
</style>