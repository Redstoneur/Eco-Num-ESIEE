<script setup lang="ts">
import { computed, defineProps } from 'vue'

// Props
const props = defineProps<{
  value: number
}>()

// Formater en notation scientifique
const formatted = computed(() => {
  const num = props.value
  if (num === 0) return '0'

  const exponent = Math.floor(Math.log10(Math.abs(num)))
  const mantissa = num / Math.pow(10, exponent)

  // Limite la mantisse à 3 chiffres significatifs
  const mantissaStr = mantissa.toPrecision(3).replace(/\.?0+$/, '')

  // Exposant avec l'exposant en exposant Unicode
  const superscriptMap: Record<string, string> = {
    '-': '⁻',
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
  }

  const exponentStr = exponent
      .toString()
      .split('')
      .map((char) => superscriptMap[char] || '')
      .join('')

  return `${mantissaStr} × 10${exponentStr}`
})
</script>

<template>
  <span class="scientific">{{ formatted }}</span>
</template>

<style scoped>
.scientific {
  font-family: monospace;
  white-space: nowrap;
}
</style>
