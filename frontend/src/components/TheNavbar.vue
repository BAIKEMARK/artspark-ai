<template>
  <el-menu
    :default-active="activeView"
    class="global-nav-menu"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <el-menu-item index="home-view" class="nav-logo">
      🎨 <span>艺启智AI</span>
    </el-menu-item>

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
  border-bottom: 1px solid var(--secondary-color);
  padding: 0 20px;
  background-color: var(--primary-color);
  box-shadow: none;
}

/* 2. Logo 样式：白色文字 */
.nav-logo {
  font-size: 1.4rem;
  font-weight: bold;
  color: white !important;
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
  transition: all 0.2s ease;
}

.el-menu-item .icon {
  font-size: 1.2rem;
}

/* 4. 菜单项 悬停 样式 */
.el-menu-item:hover {
  color: white !important;
  background-color: var(--secondary-color) !important;
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

/* 8. 响应式布局：在小屏幕上隐藏菜单文字 */

/* 屏幕宽度 <= 1200px (对应我们内容区的 1260px 断点) */
@media (max-width: 1200px) {
  .el-menu-item:not(.nav-logo) span {
    display: none;
  }

  /* 调整一下间距，让图标更紧凑 */
  .el-menu-item:not(.nav-logo) {
    padding: 0 15px;
    min-width: auto;
  }
}

/* 屏幕宽度 <= 768px (手机) */
@media (max-width: 768px) {
   /* 在手机上，隐藏所有文字 */
   .el-menu-item span {
     display: none;
   }

   .nav-logo {
     font-size: 1.4rem; /* 保持 Logo 图标大小 */
     padding-left: 10px; /* 手机上左边距小一点 */
   }

   .el-menu-item {
     padding: 0 10px; /* 手机上间距更小 */
   }

   .global-nav-menu {
     padding: 0; /* 移除左右内边距 */
   }
}
</style>