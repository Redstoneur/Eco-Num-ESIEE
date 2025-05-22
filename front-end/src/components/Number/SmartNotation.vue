<script setup lang="ts">
import { computed, defineProps } from 'vue'
import ScientificNotation from './ScientificNotation.vue'

const props = defineProps<{
  value: number
}>()

// Détermine si on doit utiliser la forme scientifique ou non
const useScientific = computed(() => {
  const num = props.value
  if (num === 0) return false

  const exponent = Math.floor(Math.log10(Math.abs(num)))
  return exponent < -2 || exponent > 2
})

// Si pas scientifique, on affiche en notation classique
const plainFormat = computed(() => {
  return props.value.toPrecision(6).replace(/\.?0+$/, '')
})
</script>

<template>
  <span class="smart-notation">
    <ScientificNotation v-if="useScientific" :value="value" />
    <span v-else>{{ plainFormat }}</span>
  </span>
</template>

<style scoped>
.smart-notation {
  font-family: monospace;
  white-space: nowrap;
}
</style>
