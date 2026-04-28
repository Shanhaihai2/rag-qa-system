<script setup>
import { ref } from 'vue'
import HelloMessage from './components/HelloMessage.vue'

const greeting = ref('')

function handleGreet(message) {
  greeting.value = message
}
</script>

<template>
  <!-- 使用子组件，传入 props -->
  <HelloMessage name="张三" :age="20" @greet="handleGreet" />
  <HelloMessage name="李四" :age="22" @greet="handleGreet" />

  <p v-if="greeting" class="greeting-msg">{{ greeting }}</p>
</template>