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

    <el-container class="main-content-container" :class="{ 'centered-layout': activeView !== 'home-view' }">

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

      <el-aside width="300px" class="contextual-sidebar" v-if="activeView !== 'home-view'" style="padding: 20px 20px 0 0;">
        <div id="dynamic-sidebar-content" v-html="sidebarContentHTML"></div>
      </el-aside>
    </el-container>

    <el-footer v-if="isLoggedIn" class="app-footer">
      <TheFooter :is-home-page="isHomePage" />
    </el-footer>

    <SettingsSidebar :is-open="isSettingsSidebarOpen"
                     @close="isSettingsSidebarOpen = false"
    />
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';
import { useAuthStore } from './stores/auth';
import { useSettingsStore } from './stores/settings';
import { storeToRefs } from 'pinia';

// 导入组件
import ApiKeyModal from './components/ApiKeyModal.vue';
import TheNavbar from './components/TheNavbar.vue';
import HomeView from './views/HomeView.vue';
import TheFooter from './components/TheFooter.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';

const authStore = useAuthStore();
const { isLoggedIn } = storeToRefs(authStore);

const settingsStore = useSettingsStore(); // 未使用，但保留

const isVerifyingApiKey = ref(false);
const apiKeyError = ref('');

const activeView = ref('home-view');
const isSettingsSidebarOpen = ref(false);

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

// --- (已修改) 静态数据 ---
const heroSlides = [
  { image: '/img/Starry-Night.jpg' }, { image: '/img/千里江山图.jpg' },
  { image: '/img/Мона-Лиза.jpg' }, { image: '/img/五牛图.jpeg' },
  { image: '/img/Monet-Impression-Sunrise.jpg' }, { image: '/img/步辇图.jpeg' },
];

// (已修改) 更新导航项
const navItems = [
  { id: 'home-view', text: '首页', icon: 'ph-house' },
  { id: 'art-gallery', text: '名画鉴赏室', icon: 'ph-palette' },
  { id: 'line-coloring', text: 'AI智能上色', icon: 'ph-paint-brush' },
  { id: 'creative-workshop', text: '创意工坊', icon: 'ph-paint-brush-broad' }, // 新增
  { id: 'portrait-workshop', text: '人像工坊', icon: 'ph-user-focus' },     // 新增
  { id: 'art-qa', text: '艺术小百科', icon: 'ph-question' },
  { id: 'idea-generator', text: '创意灵感生成', icon: 'ph-lightbulb' },
  // 移除 style-workshop, self-portrait, art-fusion
];

// (已修改) 更新首页卡片
const featureCards = [
  { id: 'line-coloring', icon: 'ph-paint-brush', title: 'AI智能上色', description: '上传线稿，一键变为专业彩绘' },
  { id: 'creative-workshop', icon: 'ph-paint-brush-broad', title: '创意工坊', description: '用文本或图像改变图片风格' }, // 新增
  { id: 'portrait-workshop', icon: 'ph-user-focus', title: '人像工坊', description: '生成不同风格的艺术人像' },     // 新增
  { id: 'idea-generator', icon: 'ph-lightbulb', title: '创意灵感生成', description: '输入主题，获取绘画新点子' }, // 调整顺序
  // 移除 style-workshop, self-portrait, art-fusion
];

// (已修改) 更新侧边栏内容
const sidebarContentData = {
    'default': { tips: `<h3><i class="icon ph-bold ph-lightbulb-filament"></i> 教学小贴士</h3><p>欢迎来到“艺启智AI”！从顶部导航栏选择一个工具开始。</p><p>您可以利用这些工具，辅助学生理解色彩、风格和构图。</p>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="示例1"><img src="/img/千里江山图.jpg" alt="示例2"></div>` },
    'line-coloring': { tips: `<h3><i class="icon ph-bold ph-paint-brush"></i> 上色小贴士</h3><ul><li><strong>风格多样：</strong> 尝试“水彩画”、“油画”、“动漫风格”或“赛博朋克”等关键词。</li><li><strong>色彩词：</strong> 使用“明亮的颜色”、“柔和的色调”或“复古色”来引导AI。</li><li><strong>教学应用：</strong> 让学生上传同一张线稿，但使用不同的风格提示词，比较结果。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 上色示例</h3><div class="example-images"><img src="/img/lineart_example1.png" alt="上色示例1"><img src="/img/lineart_example2.png" alt="上色示例2"></div>` },
    'creative-workshop': { tips: `<h3><i class="icon ph-bold ph-paint-brush-broad"></i> 创意工坊小贴士</h3><ul><li><strong>文本指令：</strong> 上传一张校园照片，在“文本指令”模式下输入“变成梵高风格”或“雪景”。</li><li><strong>图像风格：</strong> 上传校园照片作为“内容图”，再上传一张《星空》作为“风格图”。</li><li><strong>教学应用：</strong> 结合“名画鉴赏室”进行风格模仿练习。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="梵高"><img src="/img/千里江山图.jpg" alt="水墨画"></div>` },
    'portrait-workshop': { tips: `<h3><i class="icon ph-bold ph-user-focus"></i> 人像工坊小贴士</h3><ul><li><strong>预设风格：</strong> 上传人像照片，在“预设风格”中选择“动漫风”、“3D童话”等快速体验。</li><li><strong>自定义风格：</strong> 上传人像照片，在“自定义风格”中上传一张艺术作品图片（如蒙娜丽莎）。</li><li><strong>教学应用：</strong> 探索不同文化和艺术流派的人像表达方式。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="/img/portrait_example1.png" alt="人像示例1"><img src="/img/portrait_example2.png" alt="人像示例2"></div>` },
    'art-qa': { tips: `<h3><i class="icon ph-bold ph-question"></i> 提问小贴士</h3><ul><li><strong>开始对话：</strong> 你可以问任何艺术问题，比如“什么是印象派？”</li><li><strong>深入追问：</strong> “小艺”老师记住了你们的对话。你可以继续追问：“那印象派有哪些著名的画家呢？”</li><li><strong>清空历史：</strong> 如果你想开始一个全新的话题，可以点击“清空对话”按钮。</li></ul>`, examples: `` },
    'idea-generator': { tips: `<h3><i class="icon ph-bold ph-lightbulb"></i> 灵感小贴士</h3><ul><li><strong>激发创意：</strong> 当你不知道画什么时，这是最好的起点。</li><li><strong>主题词：</strong> 尝试输入“节日”、“动物”、“太空”或“梦想”等主题。</li><li><strong>再创作：</strong> AI生成的示例图只是参考，鼓励学生在此基础上进行自己的创作！</li></ul>`, examples: `` },
    'art-gallery': { tips: `<h3><i class="icon ph-bold ph-palette"></i> 画廊小贴士</h3><ul><li><strong>探索艺术史：</strong> 这是探索世界顶级博物馆藏品的绝佳方式。</li><li><strong>组合筛选：</strong> 尝试组合不同的筛选条件，例如“19世纪”、“绘画”和“欧洲”。</li><li><strong>关键词搜索：</strong> 使用“辅助搜索”来寻找特定主题，如“猫”、“船”或“向日葵”。</li></ul>`, examples: `` }
    // 移除 style-workshop, self-portrait, art-fusion 的条目
};

// --- 计算属性 (Computed) ---

const isHomePage = computed(() => activeView.value === 'home-view');
const mainStyle = computed(() => {
  if (activeView.value === 'home-view') {
    return { padding: 0 };
  }
  // (修改) 调整工具页面的内边距
  return { padding: '20px 20px 0 20px' };
});

const bodyClass = computed(() => ({
  'showing-home': activeView.value === 'home-view',
  'showing-tools': activeView.value !== 'home-view'
}));

const sidebarContentHTML = computed(() => {
  const contentKey = sidebarContentData[activeView.value] ? activeView.value : 'default';
  const content = sidebarContentData[contentKey];
  let html = '';
  if (content.tips) html += `<div class="sidebar-widget">${content.tips}</div>`;
  if (content.examples) {
      // 修正：确保 example-images 类应用正确
      const exampleHtml = content.examples.replace('<div class="example-images">', '<div class="sidebar-widget example-widget"><h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images">');
      html += exampleHtml.includes('sidebar-widget example-widget') ? exampleHtml : `<div class="sidebar-widget example-widget">${content.examples}</div>`;
  }
  return html;
});


// (已修改) 更新组件映射
const toolComponentMap = {
  'line-coloring': defineAsyncComponent(() => import('./views/LineColoringView.vue')),
  'art-gallery': defineAsyncComponent(() => import('./views/ArtGalleryView.vue')),
  'creative-workshop': defineAsyncComponent(() => import('./views/CreativeWorkshopView.vue')), // 新增
  'portrait-workshop': defineAsyncComponent(() => import('./views/PortraitWorkshopView.vue')), // 新增
  'art-qa': defineAsyncComponent(() => import('./views/ArtQAView.vue')),
  'idea-generator': defineAsyncComponent(() => import('./views/IdeaGeneratorView.vue')),
  // 移除 style-workshop, self-portrait, art-fusion
};


const currentToolComponent = computed(() => {
  // 简化逻辑，直接使用 activeView 作为 key
  return toolComponentMap[activeView.value];
});

// --- 方法 (Methods) ---
function navigateTo(targetId) {
  if (navItems.some(item => item.id === targetId)) { // 确保 targetId 是有效的视图 ID
      activeView.value = targetId;
      window.scrollTo(0, 0);
  } else {
      console.warn("Invalid navigation target:", targetId);
  }
}

// --- 生命周期钩子 (Lifecycle Hooks) ---
onMounted(() => {
  if (!isLoggedIn.value) {
    // Modal 会自动显示
  } else {
    // 如果已登录，默认导航到首页
     if (!activeView.value || !navItems.some(item => item.id === activeView.value)) {
        navigateTo('home-view');
     }
  }
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
/* 移除这个规则，让 KeepAlive 内的组件自然高度 */
/* #tool-content:not(.view-panel) {
  height: 100%;
} */

/* 侧边栏样式微调 */
.contextual-sidebar {
  background-color: transparent; /* 使其透明以看到背景 */
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