<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">User Behavior System</div>
      <el-menu
        class="menu"
        mode="horizontal"
        :default-active="route.path"
        router
        ellipsis
      >
        <el-menu-item index="/dashboard">Dashboard</el-menu-item>
        <el-menu-item index="/behavior-flow">Behavior Flow</el-menu-item>
        <el-menu-item index="/user-analysis">User Analysis</el-menu-item>
        <el-menu-item index="/prediction">Prediction</el-menu-item>
        <el-menu-item index="/comparison">Comparison</el-menu-item>
      </el-menu>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
  'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background: #f5f5f5;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #ffffff;
  border-bottom: 1px solid #eaeaea;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand {
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.menu {
  flex: 1;
  border-bottom: none !important;
}

.content {
  flex: 1;
  padding: 16px;
}
</style>