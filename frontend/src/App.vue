<template>
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
           <i class="ph-bold ph-lightbulb"></i> 灵感与贴士
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
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useAuthStore } from './stores/auth';
import { storeToRefs } from 'pinia';

// 导入组件
import ApiKeyModal from './components/ApiKeyModal.vue';
import TheNavbar from './components/TheNavbar.vue';
import HomeView from './views/HomeView.vue';
import TheFooter from './components/TheFooter.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';
import FeedbackForm from './components/FeedbackForm.vue';

const authStore = useAuthStore();
const { isLoggedIn } = storeToRefs(authStore);

const isVerifyingApiKey = ref(false);
const apiKeyError = ref('');

const activeView = ref('home-view');
const isSettingsSidebarOpen = ref(false);
// 新增：检测是否为移动端
const isMobile = ref(window.innerWidth <= 768);

async function saveApiKey(apiKey) {
  if (!apiKey) {
    apiKeyError.value = '请输入 API Key。';
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
      throw new Error(data.error || `验证失败: ${response.status}`);
    }
    if (data.token) {
      authStore.login(data.token);
    } else {
      throw new Error('未收到Token，登录失败。');
    }
  } catch (error) {
    apiKeyError.value = error.message || 'API Key 验证失败，请重试。';
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
const navItems = [
  { id: 'home-view', text: '首页', icon: 'ph-house' },
  // “学” (Learn)
  { id: 'art-gallery', text: '名画鉴赏室', icon: 'ph-palette' },
  // “想” (Ideate)
  { id: 'idea-generator', text: '创意绘练', icon: 'ph-lightbulb' },
  { id: 'mood-painting', text: '心情画板', icon: 'ph-paint-brush-household' },
  // “练” (Create)
  { id: 'line-coloring', text: 'AI智能上色', icon: 'ph-paint-brush' },
  { id: 'creative-workshop', text: '创意工坊', icon: 'ph-paint-brush-broad' },
  { id: 'portrait-workshop', text: '人像工坊', icon: 'ph-user-focus' },
  // “支持” (Support)
  { id: 'art-qa', text: '艺术小百科', icon: 'ph-question' },
];

// 更新首页卡片
const featureCards = [
  {
    id: 'art-gallery',
    icon: 'ph-palette',
    title: '名画鉴赏室',
    description: 'AI带你深度解析世界名画'
  },
  {
    id: 'mood-painting',
    icon: 'ph-paint-brush-household',
    title: '心情画板',
    description: '融合心理学，引导情绪表达'
  },
  {
    id: 'line-coloring',
    icon: 'ph-paint-brush',
    title: 'AI智能上色',
    description: '上传线稿，一键变为专业彩绘'
  },
  {
    id: 'creative-workshop',
    icon: 'ph-paint-brush-broad',
    title: '创意工坊',
    description: '用文本或图像改变图片风格'
  },
];

// 更新侧边栏内容
const sidebarContentData = {
    'art-gallery': { tips: `<h3><i class="icon ph-bold ph-palette"></i> 画廊小贴士</h3><ul><li><strong>探索艺术史：</strong> 这是探索世界顶级博物馆藏品的绝佳方式。</li><li><strong>组合筛选：</strong> 尝试组合不同的筛选条件，例如“19世纪”、“绘画”和“欧洲”。</li><li><strong>关键词搜索：</strong> 使用“辅助搜索”来寻找特定主题，如“猫”、“船”或“向日葵”。</li></ul>`, examples: `` },
    'idea-generator': { tips: `<h3><i class="icon ph-bold ph-lightbulb"></i> 灵感小贴士</h3><ul><li><strong>激发创意：</strong> 当你不知道画什么时，这是最好的起点。</li><li><strong>主题词：</strong> 尝试输入“节日”、“动物”、“太空”或“梦想”等主题。</li><li><strong>再创作：</strong> AI生成的示例图只是参考，鼓励学生在此基础上进行自己的创作！</li></ul>`, examples: `` },
    'mood-painting': {
        tips: `<h3><i class="icon ph-bold ph-paint-brush-household"></i> 心情画板小贴士</h3><ul><li><strong>关怀优先：</strong> 这是为学生（尤其是留守儿童）设计的心理关怀工具。</li><li><strong>情绪引导：</strong> 鼓励学生选择真实的心情，AI会提供具有疏导性质的绘画创意。</li><li><strong>教学应用：</strong> 可用于美术课的开始或结束，作为“情绪签到”或“情绪整理”的环节。</li></ul>`,
        examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="/img/moodpainting-a.png" alt="生气"><img src="/img/moodpainting-b.png" alt="难过"></div>`
    },
    'line-coloring': { tips: `<h3><i class="icon ph-bold ph-paint-brush"></i> 上色小贴士</h3><ul><li><strong>风格多样：</strong> 尝试“水彩画”、“油画”、“动漫风格”或“赛博朋克”等关键词。</li><li><strong>色彩词：</strong> 使用“明亮的颜色”、“柔和的色调”或“复古色”来引导AI。</li><li><strong>教学应用：</strong> 让学生上传同一张线稿，但使用不同的风格提示词，比较结果。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 上色示例</h3><div class="example-images"><img src="/img/lineart.png" alt="上色示例1"><img src="/img/line-color.png" alt="上色示例2"></div>` },
    'creative-workshop': { tips: `<h3><i class="icon ph-bold ph-paint-brush-broad"></i> 创意工坊小贴士</h3><ul><li><strong>文本指令：</strong> 上传一张校园照片，在“文本指令”模式下输入“变成梵高风格”或“雪景”。</li><li><strong>图像风格：</strong> 上传校园照片作为“内容图”，再上传一张《星空》作为“风格图”。</li><li><strong>教学应用：</strong> 结合“名画鉴赏室”进行风格模仿练习。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="/img/cloud-boy.png" alt="原图"><img src="/img/cloud-boy-fangao.png" alt="复古漫画"></div>` },
    'portrait-workshop': { tips: `<h3><i class="icon ph-bold ph-user-focus"></i> 人像工坊小贴士</h3><ul><li><strong>预设风格：</strong> 上传人像照片，在“预设风格”中选择“动漫风”、“3D童话”等快速体验。</li><li><strong>自定义风格：</strong> 上传人像照片，在“自定义风格”中上传一张艺术作品图片（如蒙娜丽莎）。</li><li><strong>教学应用：</strong> 探索不同文化和艺术流派的人像表达方式。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="/img/style-pic.png" alt="原图"><img src="/img/style-fussion.png" alt="复古漫画"></div>` },
    'art-qa': { tips: `<h3><i class="icon ph-bold ph-question"></i> 提问小贴士</h3><ul><li><strong>开始对话：</strong> 你可以问任何艺术问题，比如“什么是印象派？”</li><li><strong>深入追问：</strong> “小艺”老师记住了你们的对话。你可以继续追问：“那印象派有哪些著名的画家呢？”</li><li><strong>清空历史：</strong> 如果你想开始一个全新的话题，可以点击“清空对话”按钮。</li></ul>`, examples: `` },
};

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

const sidebarContentHTML = computed(() => {
  const contentKey = sidebarContentData[activeView.value] ? activeView.value : 'default';
  const content = sidebarContentData[contentKey];
  let html = '';
  if (content.tips) html += `<div class="sidebar-widget">${content.tips}</div>`;
  if (content.examples) {
      const exampleHtml = content.examples.replace('<div class="example-images">', '<div class="sidebar-widget example-widget"><h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images">');
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
  'creative-workshop': defineAsyncComponent(() => import('./views/CreativeWorkshopView.vue')),
  'portrait-workshop': defineAsyncComponent(() => import('./views/PortraitWorkshopView.vue')),
  'art-qa': defineAsyncComponent(() => import('./views/ArtQAView.vue')),
};


const currentToolComponent = computed(() => {
  return toolComponentMap[activeView.value];
});

// --- 方法 (Methods) ---
function navigateTo(targetId) {
  if (navItems.some(item => item.id === targetId)) {
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
     if (!activeView.value || !navItems.some(item => item.id === activeView.value)) {
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