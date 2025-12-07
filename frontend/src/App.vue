<template>
  <el-config-provider :locale="elementPlusLocale">
    <el-container id="vue-app" :class="bodyClass">
      <ApiKeyModal v-if="!isLoggedIn"
                   @save-api-key="saveApiKey"
                   :is-verifying="isVerifyingApiKey"
                   :api-error="apiKeyError"
      />

    <el-header class="app-header">
      <TheNavbar :nav-items="navItems"
                 :active-view="activeView"
                 @navigate="navigateTo"
                 @open-settings="isSettingsSidebarOpen = true"
      />
    </el-header>

    <el-container
      class="main-content-container"
      :direction="isMobile ? 'vertical' : 'horizontal'"
      :class="{ 'centered-layout': activeView !== 'home-view' }"
    >

      <el-main :style="mainStyle">
        <HomeView v-if="activeView === 'home-view'"
                  :hero-slides="heroSlides"
                  :feature-cards="featureCards"
                  @navigate="navigateTo"
        />
        <div id="tool-content" :class="{ 'view-panel': activeView !== 'home-view' }" v-else>
          <KeepAlive>
            <component :is="currentToolComponent" />
          </KeepAlive>
        </div>
      </el-main>

      <el-aside
        :width="isMobile ? '100%' : '300px'"
        class="contextual-sidebar"
        v-if="activeView !== 'home-view'"
        style="padding: 20px 20px 0 0;"
      >
        <div v-if="isMobile" style="margin-bottom: 10px; font-weight: bold; color: var(--secondary-color);">
           <i class="ph-bold ph-lightbulb"></i> {{ t('sidebar.tipsAndInspiration') }}
        </div>
        <div id="dynamic-sidebar-content" v-html="sidebarContentHTML"></div>
      </el-aside>
    </el-container>

    <el-footer v-if="isLoggedIn" class="app-footer">
      <TheFooter :is-home-page="isHomePage" />
    </el-footer>

    <SettingsSidebar :is-open="isSettingsSidebarOpen"
                     @close="isSettingsSidebarOpen = false"
    />
    <FeedbackForm />
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useAuthStore } from './stores/auth';
import { useLocaleStore } from './stores/locale';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

// 导入组件
import ApiKeyModal from './components/ApiKeyModal.vue';
import TheNavbar from './components/TheNavbar.vue';
import HomeView from './views/HomeView.vue';
import TheFooter from './components/TheFooter.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';
import FeedbackForm from './components/FeedbackForm.vue';

const authStore = useAuthStore();
const { isLoggedIn } = storeToRefs(authStore);
const localeStore = useLocaleStore();
const { currentElementPlusLocale } = storeToRefs(localeStore);
const { t } = useI18n();

// Element Plus locale for ConfigProvider
const elementPlusLocale = computed(() => currentElementPlusLocale.value);

const isVerifyingApiKey = ref(false);
const apiKeyError = ref('');

const activeView = ref('home-view');
const isSettingsSidebarOpen = ref(false);
// 新增：检测是否为移动端
const isMobile = ref(window.innerWidth <= 768);

async function saveApiKey(apiKey) {
  if (!apiKey) {
    apiKeyError.value = t('errors.apiKeyMissing');
    return;
  }
  isVerifyingApiKey.value = true;
  apiKeyError.value = '';
  try {
    const response = await fetch('/api/set_key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `${t('errors.validationFailed')}: ${response.status}`);
    }
    if (data.token) {
      authStore.login(data.token);
    } else {
      throw new Error(t('errors.loginFailed'));
    }
  } catch (error) {
    apiKeyError.value = error.message || t('errors.apiKeyValidationFailed');
  } finally {
    isVerifyingApiKey.value = false;
  }
}

// --- 静态数据 ---
const heroSlides = [
  { image: '/img/Starry-Night.jpg' }, { image: '/img/千里江山图.jpg' },
  { image: '/img/Мона-Лиза.jpg' }, { image: '/img/五牛图.jpeg' },
  { image: '/img/Monet-Impression-Sunrise.jpg' }, { image: '/img/步辇图.jpeg' },
];

// 更新导航项
const navItems = computed(() => [
  { id: 'home-view', text: t('nav.home'), icon: 'ph-house' },
  // "学" (Learn)
  { id: 'art-gallery', text: t('nav.artGallery'), icon: 'ph-palette' },
  // "想" (Ideate)
  { id: 'idea-generator', text: t('nav.ideaGenerator'), icon: 'ph-lightbulb' },
  { id: 'mood-painting', text: t('nav.moodPainting'), icon: 'ph-paint-brush-household' },
  // "练" (Create)
  { id: 'line-coloring', text: t('nav.lineColoring'), icon: 'ph-paint-brush' },
  { id: 'style-workshop', text: t('nav.styleWorkshop'), icon: 'ph-magic-wand' },
  { id: 'art-qa', text: t('nav.artQA'), icon: 'ph-question' },
]);

// 更新首页卡片
const featureCards = computed(() => [
  {
    id: 'art-gallery',
    icon: 'ph-palette',
    title: t('views.home.featureCards.artGallery.title'),
    description: t('views.home.featureCards.artGallery.description')
  },
  {
    id: 'mood-painting',
    icon: 'ph-paint-brush-household',
    title: t('views.home.featureCards.moodPainting.title'),
    description: t('views.home.featureCards.moodPainting.description')
  },
  {
    id: 'line-coloring',
    icon: 'ph-paint-brush',
    title: t('views.home.featureCards.lineColoring.title'),
    description: t('views.home.featureCards.lineColoring.description')
  },
  {
    id: 'style-workshop', // 指向新页面
    icon: 'ph-magic-wand',
    title: t('views.home.featureCards.styleWorkshop.title'),
    description: t('views.home.featureCards.styleWorkshop.description')
  },
]);

// 生成侧边栏内容的辅助函数
const generateTipsHTML = (viewKey, iconClass) => {
  try {
    const title = t(`views.${viewKey}.sidebarTitle`);
    
    let html = `<h3><i class="icon ph-bold ${iconClass}"></i> ${title}</h3><ul>`;
    
    // 根据不同视图生成不同的提示项
    const tipKeys = {
      'artGallery': ['explore', 'filter', 'search'],
      'ideaGenerator': ['inspire', 'theme', 'recreate'],
      'moodPainting': ['care', 'guide', 'teaching'],
      'lineColoring': ['style', 'color', 'teaching'],
      'styleWorkshop': ['portrait', 'artistic', 'teaching'],
      'artQA': ['start', 'followup', 'clear']
    };
    
    const keys = tipKeys[viewKey] || [];
    keys.forEach(key => {
      const tipText = t(`views.${viewKey}.sidebarTips.${key}`);
      html += `<li>${tipText}</li>`;
    });
    
    html += '</ul>';
    return html;
  } catch (error) {
    console.error(`Error generating tips HTML for ${viewKey}:`, error);
    return '';
  }
};

// 生成示例图片HTML的辅助函数
const generateExamplesHTML = (viewKey, images) => {
  const title = t(`views.${viewKey}.examplesTitle`);
  let html = `<h3><i class="icon ph-bold ph-image"></i> ${title}</h3><div class="example-images">`;
  
  images.forEach(img => {
    html += `<img src="${img.src}" alt="${img.alt}">`;
  });
  
  html += '</div>';
  return html;
};

// 更新侧边栏内容 - 使用computed动态生成
const sidebarContentData = computed(() => ({
    'art-gallery': { 
      tips: generateTipsHTML('artGallery', 'ph-palette'), 
      examples: '' 
    },
    'idea-generator': { 
      tips: generateTipsHTML('ideaGenerator', 'ph-lightbulb'), 
      examples: '' 
    },
    'mood-painting': {
      tips: generateTipsHTML('moodPainting', 'ph-paint-brush-household'),
      examples: generateExamplesHTML('moodPainting', [
        { src: '/img/moodpainting-a.png', alt: t('views.moodPainting.moods.angry') },
        { src: '/img/moodpainting-b.png', alt: t('views.moodPainting.moods.sad') }
      ])
    },
    'line-coloring': { 
      tips: generateTipsHTML('lineColoring', 'ph-paint-brush'), 
      examples: generateExamplesHTML('lineColoring', [
        { src: '/img/lineart.png', alt: t('views.lineColoring.examplesTitle') + ' 1' },
        { src: '/img/line-color.png', alt: t('views.lineColoring.examplesTitle') + ' 2' }
      ])
    },
    'art-qa': { 
      tips: generateTipsHTML('artQA', 'ph-question'), 
      examples: '' 
    },
    'style-workshop': {
      tips: generateTipsHTML('styleWorkshop', 'ph-magic-wand'),
      examples: generateExamplesHTML('styleWorkshop', [
        { src: '/img/cloud-boy.png', alt: t('common.upload') },
        { src: '/img/cloud-boy-fangao.png', alt: 'Van Gogh Style' },
        { src: '/img/style-pic.png', alt: t('views.styleWorkshop.portraitMode') },
        { src: '/img/style-fussion.png', alt: t('views.styleWorkshop.startTransform') }
      ])
    },
}));

// --- 计算属性 (Computed) ---

const isHomePage = computed(() => activeView.value === 'home-view');
const mainStyle = computed(() => {
  if (activeView.value === 'home-view') {
    return { padding: 0 };
  }
  // 移动端减少内边距
  const padding = isMobile.value ? '10px' : '20px 20px 0 20px';
  return { padding };
});

const bodyClass = computed(() => ({
  'showing-home': activeView.value === 'home-view',
  'showing-tools': activeView.value !== 'home-view',
  'is-mobile': isMobile.value // 方便全局 CSS 使用
}));

// 将 kebab-case 转换为 camelCase 的辅助函数
const kebabToCamel = (str) => {
  return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
};

const sidebarContentHTML = computed(() => {
  const contentKey = sidebarContentData.value[activeView.value] ? activeView.value : 'default';
  const content = sidebarContentData.value[contentKey];
  let html = '';
  if (content && content.tips) html += `<div class="sidebar-widget">${content.tips}</div>`;
  if (content && content.examples) {
      const viewKey = kebabToCamel(contentKey);
      const exampleHtml = content.examples.replace('<div class="example-images">', '<div class="sidebar-widget example-widget"><h3><i class="icon ph-bold ph-image"></i> ' + t(`views.${viewKey}.examplesTitle`) + '</h3><div class="example-images">');
      html += exampleHtml.includes('sidebar-widget example-widget') ? exampleHtml : `<div class="sidebar-widget example-widget">${content.examples}</div>`;
  }
  return html;
});

// 组件映射
const toolComponentMap = {
  'art-gallery': defineAsyncComponent(() => import('./views/ArtGalleryView.vue')),
  'idea-generator': defineAsyncComponent(() => import('./views/IdeaGeneratorView.vue')),
  'mood-painting': defineAsyncComponent(() => import('./views/MoodPaintingView.vue')),
  'line-coloring': defineAsyncComponent(() => import('./views/LineColoringView.vue')),
  'style-workshop': defineAsyncComponent(() => import('./views/StyleWorkshopView.vue')),

  'art-qa': defineAsyncComponent(() => import('./views/ArtQAView.vue')),
};


const currentToolComponent = computed(() => {
  return toolComponentMap[activeView.value];
});

// --- 方法 (Methods) ---
function navigateTo(targetId) {
  if (navItems.value.some(item => item.id === targetId)) {
      activeView.value = targetId;
      window.scrollTo(0, 0);
  } else {
      console.warn("Invalid navigation target:", targetId);
  }
}

// 窗口大小监听
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768;
};

// --- 生命周期钩子 (Lifecycle Hooks) ---
onMounted(() => {
  window.addEventListener('resize', handleResize); // 监听窗口变化
  if (!isLoggedIn.value) {
  } else {
     if (!activeView.value || !navItems.value.some(item => item.id === activeView.value)) {
        navigateTo('home-view');
     }
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.app-header {
  padding: 0;
  height: var(--nav-height);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 100;
}
.main-content-container {
  width: 100%;
  flex-grow: 1;
}
.main-content-container.centered-layout {
  max-width: 1260px; /* 保持内容最大宽度 */
  margin: 0 auto;
}
.app-footer {
  height: auto;
  padding: 0;
}
#tool-content {
  padding: 0;
}

/* 侧边栏样式微调 */
.contextual-sidebar {
  background-color: transparent; /* 使其透明以看到背景 */
}
/* 移动端侧边栏样式覆盖 */
.main-content-container[direction="vertical"] .contextual-sidebar {
    padding-left: 20px !important; /* 修正移动端 padding */
    padding-bottom: 20px !important;
}


/* 侧边栏示例图片样式 */
:deep(.example-widget h3) { /* 确保标题选择器正确 */
    font-family: var(--font-serif);
    color: var(--secondary-color);
    margin-top: 0;
    font-size: 1.1rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
}
:deep(.example-widget h3 .icon) { /* 确保图标选择器正确 */
    font-size: 1.2rem;
    margin-right: 8px;
    color: var(--accent-color);
}
:deep(.example-images) { /* 确保图片容器选择器正确 */
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
:deep(.example-images img) { /* 确保图片选择器正确 */
    width: 100%;
    height: 80px;
    object-fit: cover;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}
</style>
