<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
  titleUsage: string;
  usageSteps: Array<{
    title: string;
    content: string;
  }>;
}>();
</script>

<template>
  <div class="project-info">
    <h2 class="project-title">{{ title }}</h2>
    <p class="project-description">{{ description }}</p>

    <h3>{{ titleUsage }}</h3>
    <ol class="usage-steps">
      <li v-for="(step, index) in usageSteps" :key="index">
        <strong>{{ step.title }}</strong>
        <p v-html="step.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')"></p>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.project-info {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f9fafb;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.project-title {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.project-description {
  font-size: 1rem;
  color: #34495e;
  margin-bottom: 1.5rem;
}

.usage-steps {
  list-style: decimal inside;
  margin: 0;
  padding: 0;
}

.usage-steps li {
  margin-bottom: 1rem;
}

.usage-steps strong {
  font-weight: bold;
  color: #2c3e50;
}

/* Responsive */
@media (max-width: 700px) {
  .project-info {
    padding: 0.75rem;
  }
  .project-title {
    font-size: 1.3rem;
  }
  .project-description {
    font-size: 0.95rem;
    margin-bottom: 1rem;
  }
  .usage-steps li {
    margin-bottom: 0.7rem;
    font-size: 0.98rem;
  }
}

@media (max-width: 450px) {
  .project-info {
    padding: 0.4rem;
  }
  .project-title {
    font-size: 1.05rem;
  }
  .project-description {
    font-size: 0.9rem;
  }
  .usage-steps li {
    font-size: 0.93rem;
  }
}
</style>