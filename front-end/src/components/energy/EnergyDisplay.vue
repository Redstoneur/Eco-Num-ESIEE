<script setup lang="ts">
import {computed} from "vue";
import SmartNotation from '../Number/SmartNotation.vue';

const props = defineProps<{
  value: number
  unit?: string
  icon?: string
  color?: string
}>()

const displayUnit = computed(() => props.unit ?? 'kWh')
const displayIcon = computed(() => props.icon ?? '⚡')

const displayColor = computed(() => props.color ?? '#4CAF50')
const displayColorBackground = computed(() => {
  const color = props.color ?? '#4CAF50'
  return `${color}60`
})
</script>

<template>
  <div class="energy-display" :style="{ borderColor: displayColor , backgroundColor: displayColorBackground }">
    <span class="icon" :style="{ color: displayColor }">{{ displayIcon }}</span>
    <div class="value">
      <SmartNotation class="number" :value="props.value" />
      <span class="unit">{{ displayUnit }}</span>
    </div>
  </div>
</template>

<style scoped>
.energy-display {
  display: flex;
  justify-content: center;
  align-items: center;

  width: 3em;
  height: 3em;
  border: 0.5em solid;
  border-radius: 50%;
  font-family: 'Segoe UI', sans-serif;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  padding: 2rem;

}

.icon {
  font-size: 1rem;
  margin-right: 0.4rem;
}

.value {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.number {
  font-size: 0.8rem;
  font-weight: bold;
}

.unit {
  font-size: 0.7rem;
  color: #666;
}
</style>