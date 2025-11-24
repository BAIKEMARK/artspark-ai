<template>
  <el-menu
    :default-active="activeView"
    class="global-nav-menu"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <el-menu-item index="home-view" class="nav-logo">
      🎨 <span class="logo-text">艺启智AI</span>
    </el-menu-item>

    <div class="flex-grow" />

    <el-menu-item v-for="nav in navItems" :key="nav.id" :index="nav.id" class="nav-item-responsive">
      <i class="icon ph-bold" :class="nav.icon"></i>
      <span class="nav-text">{{ nav.text }}</span>
    </el-menu-item>

    <div class="flex-grow" />

    <el-menu-item index="settings-trigger" class="settings-trigger">
      <i class="icon ph-bold ph-gear"></i>
      <span class="nav-text">设置</span>
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
  user-select: none;
  /* 允许在手机上水平滚动，防止菜单溢出 */
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
}
/* 隐藏滚动条 */
.global-nav-menu::-webkit-scrollbar {
    display: none;
}

/* 2. Logo 样式：白色文字 */
:deep(.nav-logo) {
  font-size: 1.4rem;
  font-weight: bold;
  color: white !important;
  flex-shrink: 0; /* 防止 Logo 被压缩 */
}

.flex-grow {
  flex-grow: 1;
}

/* 3. 菜单项：浅色文字 */
:deep(.el-menu-item) {
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8) !important; /* 菜单项默认文字颜色 */
  background-color: transparent !important;
  border-bottom-color: transparent !important;
  transition: all 0.2s ease;
  flex-shrink: 0; /* 防止菜单项被压缩 */
}

:deep(.el-menu-item .icon) {
  font-size: 1.2rem;
}

/* 4. 菜单项 悬停 样式 */
:deep(.el-menu-item:hover) {
  color: white !important;
  background-color: var(--secondary-color) !important;
}

/* 5. 菜单项 激活 样式：金色下划线 */
:deep(.el-menu-item.is-active) {
  color: white !important;
  border-bottom: 3px solid var(--accent-color) !important;
}

/* 6. 特殊处理Logo的激活态 */
:deep(.nav-logo.is-active) {
  color: white !important;
  border-bottom-color: transparent !important;
}
/* 7. 特殊处理设置按钮的激活态 */
:deep(.settings-trigger.is-active) {
  border-bottom-color: transparent !important;
}

/* 8. 响应式布局：在小屏幕上隐藏菜单文字 */

/* 屏幕宽度 <= 1200px (对应我们内容区的 1260px 断点) */
@media (max-width: 1200px) {
  .nav-text {
    display: none; /* 隐藏文字 */
  }

  /* 调整一下间距，让图标更紧凑 */
  :deep(.el-menu-item) {
    padding: 0 12px;
  }
}

/* 手机尺寸 (<= 768px) */
@media (max-width: 768px) {
   .global-nav-menu {
     padding: 0 10px; /* 减少两端留白 */
   }

   :deep(.nav-logo) {
     font-size: 1.2rem; /* Logo 稍微变小 */
     padding: 0 10px;
     margin-right: auto; /* 让Logo靠左，菜单靠右或中间 */
   }

   /* 针对手机屏幕，如果菜单项太多，可以让它们稍微紧凑一点 */
   :deep(.el-menu-item) {
     padding: 0 8px;
   }

   /* 在极小屏幕上，隐藏 Logo 文字，只留 Emoji */
   @media (max-width: 360px) {
       .logo-text { display: none; }
   }
}
</style>