<template>
  <nav id="global-nav">
    <div class="nav-content">
      <a href="#" id="home-logo-btn" class="nav-logo" @click.prevent="$emit('navigate', 'home-view')">🎨 艺启智AI</a>
      <div class="nav-links">
        <button
          v-for="nav in navItems"
          :key="nav.id"
          :data-target="nav.id"
          class="nav-btn"
          :class="{ active: activeView === nav.id }"
          @click="$emit('navigate', nav.id)"
        >
          <i class="icon ph-bold" :class="nav.icon"></i>{{ nav.text }}
        </button>
      </div>
      <button id="settings-btn" class="nav-settings-btn" aria-label="打开设置" @click="$emit('open-settings')">
        <i class="icon ph-bold ph-gear"></i>
      </button>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  navItems: Array,
  activeView: String,
});

defineEmits(['navigate', 'open-settings']);
</script>

