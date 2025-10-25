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
        <div id="tool-content" class="view-panel" v-else>
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
      <TheFooter />
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

// 导入组件 (路径将很快更新)
import ApiKeyModal from './components/ApiKeyModal.vue';
import TheNavbar from './components/TheNavbar.vue';
import HomeView from './views/HomeView.vue';
import TheFooter from './components/TheFooter.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';

// 图片存放在 `public/img`，应使用绝对路径 `/img/...`

const authStore = useAuthStore();
const { isLoggedIn } = storeToRefs(authStore);

const settingsStore = useSettingsStore();

const isVerifyingApiKey = ref(false);
const apiKeyError = ref('');

const activeView = ref('home-view');
const isSettingsSidebarOpen = ref(false);

// 移除了 files 和 previews

async function saveApiKey(apiKey) {
  // ... (此函数保持不变)
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
const navItems = [
  { id: 'home-view', text: '首页', icon: 'ph-house' },
  { id: 'art-gallery', text: '艺术画廊', icon: 'ph-palette' },
  { id: 'line-coloring', text: 'AI智能上色', icon: 'ph-paint-brush' },
  { id: 'style-workshop', text: '创意风格工坊', icon: 'ph-sparkle' },
  { id: 'self-portrait', text: 'AI自画像', icon: 'ph-user-square' },
  { id: 'art-fusion', text: '艺术融合', icon: 'ph-paint-roller' },
  { id: 'art-qa', text: '艺术知识问答', icon: 'ph-question' },
  { id: 'idea-generator', text: '创意灵感生成', icon: 'ph-lightbulb' },
];
const featureCards = [
  { id: 'line-coloring', icon: 'ph-paint-brush', title: 'AI智能上色', description: '上传线稿，一键变为专业彩绘' },
  { id: 'style-workshop', icon: 'ph-sparkle', title: '创意风格工坊', description: '用名画风格重绘你的草图' },
  { id: 'self-portrait', icon: 'ph-user-square', title: 'AI自画像', description: '上传照片，生成你的卡通肖像' },
  { id: 'art-fusion', icon: 'ph-paint-roller', title: '艺术融合', description: '将任意风格“刷”到你的照片上' },
];
const sidebarContentData = {
    'default': { tips: `<h3><i class="icon ph-bold ph-lightbulb-filament"></i> 教学小贴士</h3><p>欢迎来到“艺启智AI”！从左侧导航栏选择一个工具，开始您的创意之旅。</p><p>您可以利用这些工具，帮助学生们理解色彩、风格和构图。</p>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="示例1"><img src="/img/千里江山图.jpg" alt="示例2"></div>` },
    'line-coloring': { tips: `<h3><i class="icon ph-bold ph-paint-brush"></i> 上色小贴士</h3><ul><li><strong>风格多样：</strong> 尝试“水彩画”、“油画”、“动漫风格”或“赛博朋克”等关键词。</li><li><strong>色彩词：</strong> 使用“明亮的颜色”、“柔和的色调”或“复古色”来引导AI。</li><li><strong>教学应用：</strong> 让学生上传同一张线稿，但使用不同的风格提示词，比较结果。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 上色示例</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="上色示例1"><img src="/img/Starry-Night.jpg" alt="上色示例2"></div>` },
    'style-workshop': { tips: `<h3><i class="icon ph-bold ph-sparkle"></i> 风格小贴士</h3><ul><li><strong>上传草图：</strong> 上传一张简单的草图（比如一只猫），再选择“梵高”风格，效果惊人。</li><li><strong>内容描述：</strong> 即使不上传草图，也可以只通过描述来创作，例如“一只戴帽子的狗”。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="梵高"><img src="/img/千里江山图.jpg" alt="水墨画"></div>` },
    'self-portrait': { tips: `<h3><i class="icon ph-bold ph-user-square"></i> 自画像小贴士</h3><ul><li><strong>风格探索：</strong> 尝试“迪士尼卡通风格”、“像素风”、“超级英雄漫画”或“黏土动画”。</li><li><strong>清晰照片：</strong> 使用面部清晰、光线明亮的照片，AI更容易识别特征。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="自画像1"><img src="/img/Starry-Night.jpg" alt="自画像2"></div>` },
    'art-fusion': { tips: `<h3><i class="icon ph-bold ph-paint-roller"></i> 融合小贴士</h3><ul><li><strong>内容为王：</strong> “内容图片”决定了画面的主体结构（如人物、建筑）。</li><li><strong>风格至上：</strong> “风格图片”决定了颜色和笔触（如《星空》或一张火焰图片）。</li><li><strong>大胆尝试：</strong> 试试用一张电路板的图片作为“风格”来融合你的宠物照片！</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 融合示例</h3><div class="example-images"><img src="/img/Starry-Night.jpg" alt="融合1"><img src="/img/Starry-Night.jpg" alt="融合2"></div>` },
    'art-qa': { tips: `<h3><i class="icon ph-bold ph-question"></i> 提问小贴士</h3><ul><li><strong>保持好奇：</strong> 你可以问任何关于艺术的问题，比如“什么是印象派？”</li><li><strong>艺术家：</strong> “文森特·梵高是谁？”</li><li><strong>技巧：</strong> “怎么画透视？”</li></ul>`, examples: `` },
    'idea-generator': { tips: `<h3><i class="icon ph-bold ph-lightbulb"></i> 灵感小贴士</h3><ul><li><strong>激发创意：</strong> 当你不知道画什么时，这是最好的起点。</li><li><strong>主题词：</strong> 尝试输入“节日”、“动物”、“太空”或“梦想”等主题。</li><li><strong>再创作：</strong> AI生成的示例图只是参考，鼓励学生在此基础上进行自己的创作！</li></ul>`, examples: `` },
    'art-gallery': { tips: `<h3><i class="icon ph-bold ph-palette"></i> 画廊小贴士</h3><ul><li><strong>探索艺术史：</strong> 这是探索世界顶级博物馆藏品的绝佳方式。</li><li><strong>组合筛选：</strong> 尝试组合不同的筛选条件，例如“19世纪”、“绘画”和“欧洲”，看看印象派大师们的作品。</li><li><strong>关键词搜索：</strong> 使用“辅助搜索”来寻找特定主题，如“cat”、“boat”或“sunflower”。</li></ul>`, examples: `` }
};

// --- 计算属性 (Computed) ---

const mainStyle = computed(() => {
  if (activeView.value === 'home-view') {
    return { padding: 0 };
  }
  return { padding: '20px 40px 0 20px' };
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
  if (content.examples) html += `<div class="sidebar-widget">${content.examples}</div>`;
  return html;
});

const toolComponentMap = {
  'line-coloring': defineAsyncComponent(() => import('./views/LineColoringView.vue')),
  'art-gallery': defineAsyncComponent(() => import('./views/ArtGalleryView.vue')),
  'style-workshop': defineAsyncComponent(() => import('./views/StyleWorkshopView.vue')),
  'self-portrait': defineAsyncComponent(() => import('./views/SelfPortraitView.vue')),
  'art-fusion': defineAsyncComponent(() => import('./views/ArtFusionView.vue')),
  'art-qa': defineAsyncComponent(() => import('./views/ArtQAView.vue')),
  'idea-generator': defineAsyncComponent(() => import('./views/IdeaGeneratorView.vue')),
};

const currentToolComponent = computed(() => {
  const viewName = activeView.value.replace('-view', '');
  if (toolComponentMap[viewName]) {
    return toolComponentMap[viewName];
  }
  return toolComponentMap[activeView.value];
});

// --- 方法 (Methods) ---
function navigateTo(targetId) {
  activeView.value = targetId;
  window.scrollTo(0, 0);
}

// 移除了 handleFileChange

// --- 生命周期钩子 (Lifecycle Hooks) ---
onMounted(() => {
  if (!isLoggedIn.value) {
    // No action needed, modal will show
  } else {
    navigateTo('home-view');
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
  max-width: 1260px;
  margin: 0 auto;
}
.app-footer {
  height: auto;
  padding: 0;
}
#tool-content {
  padding: 0;
}
</style>
