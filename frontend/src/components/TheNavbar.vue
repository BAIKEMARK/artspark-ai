<template>
  <el-menu
    :default-active="activeView"
    class="global-nav-menu"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <el-menu-item index="home-view" class="nav-logo">🎨 艺启智AI</el-menu-item>

    <div class="flex-grow" />

    <el-menu-item v-for="nav in navItems" :key="nav.id" :index="nav.id">
      <i class="icon ph-bold" :class="nav.icon"></i>
      <span>{{ nav.text }}</span>
    </el-menu-item>

    <div class="flex-grow" />

    <el-menu-item index="settings-trigger" class="settings-trigger">
      <i class="icon ph-bold ph-gear"></i>
      <span>设置</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
const props = defineProps({
  navItems: Array,
  activeView: String,
});

const emit = defineEmits(['navigate', 'open-settings']);

function handleSelect(index) {
  if (index === 'settings-trigger') {
    emit('open-settings');
  } else {
    emit('navigate', index);
  }
}
</script>

<style scoped>
/* 1. 导航栏主体：深蓝色背景 */
.global-nav-menu {
  height: var(--nav-height);
  border-bottom: 1px solid var(--secondary-color); /* 颜色加深一点 */
  padding: 0 20px;
  background-color: var(--primary-color); /* 深蓝色背景 */
  box-shadow: none; /* 移除阴影 */
}

/* 2. Logo 样式：白色文字 */
.nav-logo {
  font-size: 1.4rem;
  font-weight: bold;
  color: white !important;
}
.nav-logo.is-active {
  border-bottom-color: transparent !important; /* 首页激活时无下划线 */
}

.flex-grow {
  flex-grow: 1;
}

/* 3. 菜单项：浅色文字 */
.el-menu-item {
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8) !important; /* 菜单项默认文字颜色 */
  background-color: transparent !important;
  border-bottom-color: transparent !important;
}

.el-menu-item .icon {
  font-size: 1.2rem;
}

/* 4. 菜单项 悬停 样式 */
.el-menu-item:hover {
  color: white !important;
  background-color: var(--secondary-color) !important; /* 悬停时颜色加深 */
}

/* 5. 菜单项 激活 样式：金色下划线 */
.el-menu-item.is-active {
  color: white !important;
  border-bottom: 3px solid var(--accent-color) !important;
}

/* 6. 特殊处理Logo的激活态 */
.nav-logo.is-active {
  color: white !important;
  border-bottom-color: transparent !important;
}
/* 7. 特殊处理设置按钮的激活态 */
.settings-trigger.is-active {
  border-bottom-color: transparent !important;
}
</style>