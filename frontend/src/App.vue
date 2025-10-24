<template>
  <div id="vue-app" :class="bodyClass">
    <ApiKeyModal v-if="!isLoggedIn"
                 :api-key-modal="apiKeyModal"
                 :is-verifying-api-key="isVerifyingApiKey"
                 :api-key-error="apiKeyError"
                 v-model:apiKeyInput="apiKeyInput"
                 @save-api-key="saveApiKey"
    />

    <TheNavbar :nav-items="navItems"
               :active-view="activeView"
               @navigate="navigateTo"
               @open-settings="isSettingsSidebarOpen = true"
    />

    <div id="main-content-wrapper">
      <HomeView v-if="activeView === 'home-view'"
                :hero-slides="heroSlides"
                :feature-cards="featureCards"
                @navigate="navigateTo"
      />

      <main id="tool-content" class="view-panel" v-else>
        <div id="tool-panels-wrapper">
          <div id="feature-panels">
            <!-- 动态组件来显示不同的工具 -->
            <component :is="currentToolComponent"
                       :ai-settings="aiSettings"
                       :files="files"
                       :previews="previews"
                       @file-change="handleFileChange"
                       @show-api-key-modal="showApiKeyModal"
            />
          </div>
        </div>
        <aside id="contextual-sidebar" v-if="activeView !== 'home-view'">
          <div id="dynamic-sidebar-content" v-html="sidebarContentHTML"></div>
        </aside>
      </main>
    </div>

    <TheFooter v-if="isLoggedIn" />

    <SettingsSidebar :is-open="isSettingsSidebarOpen"
                     v-model:aiSettings="aiSettings"
                     @close="isSettingsSidebarOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, defineAsyncComponent } from 'vue';

// 导入组件
import ApiKeyModal from './components/ApiKeyModal.vue';
import TheNavbar from './components/TheNavbar.vue';
import HomeView from './components/HomeView.vue';
import TheFooter from './components/TheFooter.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';

const AUTH_TOKEN_KEY = 'art_spark_auth_token';

// --- 状态 (State) ---
const isLoggedIn = ref(false);
const isVerifyingApiKey = ref(false);
const apiKeyInput = ref('');
const apiKeyError = ref('');
const apiKeyModal = reactive({
  title: '欢迎来到 艺启智AI',
  description: '请输入您的ModelScope API KEY以激活助教功能。'
});
const activeView = ref('home-view');
const isSettingsSidebarOpen = ref(false);

const aiSettings = reactive({
  chat_model: 'Qwen/Qwen3-30B-A3B-Instruct-2507',
  vl_model: 'Qwen/Qwen3-VL-8B-Instruct',
  image_model: 'black-forest-labs/FLUX.1-Krea-dev',
  age_range: '6-8岁',
});

const previews = reactive({
  coloring: null, styleWorkshop: null, selfPortrait: null,
  artFusionContent: null, artFusionStyle: null,
});
const files = reactive({
  coloring: null, styleWorkshop: null, selfPortrait: null,
  artFusionContent: null, artFusionStyle: null,
});

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
  'line-coloring': defineAsyncComponent(() => import('./components/tools/LineColoring.vue')),
  'art-gallery': defineAsyncComponent(() => import('./components/tools/ArtGallery.vue')),
  'style-workshop': defineAsyncComponent(() => import('./components/tools/StyleWorkshop.vue')),
  'self-portrait': defineAsyncComponent(() => import('./components/tools/SelfPortrait.vue')),
  'art-fusion': defineAsyncComponent(() => import('./components/tools/ArtFusion.vue')),
  'art-qa': defineAsyncComponent(() => import('./components/tools/ArtQA.vue')),
  'idea-generator': defineAsyncComponent(() => import('./components/tools/IdeaGenerator.vue')),
};

const currentToolComponent = computed(() => toolComponentMap[activeView.value] || null);


// --- 方法 (Methods) ---
async function checkTokenValidity() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) return false;
  try {
    const response = await fetch(`/api/check_key?token=${encodeURIComponent(token)}`);
    if (response.ok) return true;
    localStorage.removeItem(AUTH_TOKEN_KEY);
    return false;
  } catch (error) {
    console.error("Error during token validity check:", error);
    return false;
  }
}

async function saveApiKey() {
  if (!apiKeyInput.value.trim()) {
    apiKeyError.value = 'API KEY 不能为空';
    return;
  }
  isVerifyingApiKey.value = true;
  apiKeyError.value = '';
  try {
    const response = await fetch(`/api/set_key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKeyInput.value.trim() }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || '设置Key失败');
    if (result.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, result.token);
      isLoggedIn.value = true;
      apiKeyError.value = '';
      navigateTo('home-view');
    } else {
      throw new Error('未能从服务器获取 Token');
    }
  } catch (error) {
    apiKeyError.value = `错误: ${error.message}`;
  } finally {
    isVerifyingApiKey.value = false;
  }
}

function showApiKeyModal(reason = 'initial') {
  if (reason === 'expired' || reason === 'invalid') {
    apiKeyModal.title = 'API Key 已失效';
    apiKeyModal.description = '您的API Key已过期或无效。请重新输入以继续使用。';
  } else {
    apiKeyModal.title = '欢迎来到 艺启智AI';
    apiKeyModal.description = '请输入您的ModelScope API KEY以激活助教功能。';
  }
  isLoggedIn.value = false;
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

function navigateTo(targetId) {
  activeView.value = targetId;
  window.scrollTo(0, 0);
}

function handleFileChange(event, key) {
  const file = event.target.files[0];
  if (!file) {
    files[key] = null;
    previews[key] = null;
    return;
  }
  files[key] = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previews[key] = e.target.result;
  };
  reader.readAsDataURL(file);
}

// --- 生命周期钩子 (Lifecycle Hooks) ---
onMounted(async () => {
  const hasValidToken = await checkTokenValidity();
  if (hasValidToken) {
    isLoggedIn.value = true;
    navigateTo('home-view');
  } else {
    showApiKeyModal('initial');
  }
});
</script>

<style>
</style>

