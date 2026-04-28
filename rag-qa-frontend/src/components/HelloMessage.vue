<script setup>
// 定义父组件可以传入的 props
const props = defineProps({
  name: String,
  age: Number
})

// 定义可以发射给父组件的事件
const emit = defineEmits(['greet'])

function sayHello() {
  emit('greet', `你好，我是 ${props.name}，今年 ${props.age} 岁`)
}
</script>

<template>
  <div class="hello-box">
    <p>姓名：{{ name }}</p>
    <p>年龄：{{ age }}</p>
    <button @click="sayHello">打招呼</button>
  </div>
</template>

<style scoped>
.hello-box {
  border: 1px solid #ccc;
  padding: 10px;
  margin: 10px 0;
}
</style>