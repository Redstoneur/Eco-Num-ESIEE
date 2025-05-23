<script setup lang="ts">
import DisplayValue from './DisplayValue.vue';
import { defineProps } from 'vue';

defineProps<{
  x: number;
  y: number;
  u1?: string;
  u2?: string;
  separator?: string;
}>();
</script>

<template>
  <div class="display-difference">
    <DisplayValue :value="x" :unit="u1" />
    <span>&nbsp;{{ separator || '-' }}&nbsp;</span>
    <DisplayValue :value="y" :unit="u2" />
  </div>
</template>

<style scoped>
.display-difference {
  display: flex;
  align-items: baseline;
  font-family: Arial, sans-serif;
}
</style>