<template>
  <header id="home-view" class="view-panel active">
    <div class="hero-gallery">
      <div class="slider-container">
        <div
          v-for="(slide, index) in heroSlides"
          :key="index"
          class="slide"
          :class="{ 
            active: currentHeroSlide === index,
            'dual-layer': getCurrentSlideUseDualLayer(index)
          }"
          :style="{ backgroundImage: 'url(' + slide.image + ')' }"
        ></div>
      </div>
      <div class="slider-dots">
        <div
          v-for="(slide, index) in heroSlides"
          :key="index"
          class="dot"
          :class="{ active: currentHeroSlide === index }"
          @click="showHeroSlide(index)"
        ></div>
      </div>
    </div>
    <div class="home-content-overlay">
      <!-- 中文显示图片，英文显示文字 -->
      <img 
        v-if="$i18n.locale === 'zh-CN'" 
        src="/img/ArtSpark-title.png" 
        alt="艺启智AI" 
        class="hero-title-image" 
      />
      <h1 v-else>{{ $t('views.home.heroTitle') }}</h1>
      <p>{{ $t('views.home.heroSubtitle') }}</p>

      <div class="feature-cards-container">
        <div
          v-for="card in featureCards"
          :key="card.id"
          class="feature-card"
          :data-target="card.id"
          @click="$emit('navigate', card.id)"
        >
          <div class="icon"><i class="ph-bold" :class="card.icon"></i></div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.description }}</p>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const props = defineProps({
  heroSlides: Array,
  featureCards: Array,
});

defineEmits(['navigate']);

const currentHeroSlide = ref(0);
let slideInterval = null;

// 使用本地响应式数据存储每张图片的显示模式
const slidesDisplayMode = ref(new Map());

// 检测图片宽高比的函数
const checkImageAspectRatio = (imageSrc) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const imageRatio = img.width / img.height;
      const screenRatio = window.innerWidth / window.innerHeight;
      
      // 计算比例差异，如果相差超过1.5倍则使用双层模式
      const ratioDifference = Math.max(imageRatio / screenRatio, screenRatio / imageRatio);
      const useDualLayer = ratioDifference > 1.8;
      
      // 调试信息
      console.log(`图片: ${imageSrc.split('/').pop()}, 图片比例: ${imageRatio.toFixed(2)}, 屏幕比例: ${screenRatio.toFixed(2)}, 差异倍数: ${ratioDifference.toFixed(2)}, 使用双层: ${useDualLayer}`);
      
      resolve(useDualLayer);
    };
    img.onerror = () => {
      console.warn(`图片加载失败: ${imageSrc}`);
      resolve(false); // 加载失败时默认不使用双层
    };
    img.src = imageSrc;
  });
};

// 初始化所有图片的显示模式
const initializeSlides = async () => {
  if (!props.heroSlides || props.heroSlides.length === 0) return;
  
  const newDisplayMode = new Map();
  
  for (let i = 0; i < props.heroSlides.length; i++) {
    const slide = props.heroSlides[i];
    const useDualLayer = await checkImageAspectRatio(slide.image);
    newDisplayMode.set(i, useDualLayer);
  }
  
  slidesDisplayMode.value = newDisplayMode;
  console.log('轮播图显示模式已更新:', Array.from(newDisplayMode.entries()));
};

// 计算属性：获取当前图片是否使用双层模式
const getCurrentSlideUseDualLayer = (index) => {
  return slidesDisplayMode.value.get(index) || false;
};

const showHeroSlide = (index) => {
  currentHeroSlide.value = index;
};

const nextHeroSlide = () => {
  currentHeroSlide.value = (currentHeroSlide.value + 1) % props.heroSlides.length;
};

// 防抖函数
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// 监听窗口大小变化，重新计算显示模式（防抖处理）
const handleResize = debounce(async () => {
  console.log('窗口大小变化，重新计算轮播图显示模式');
  await initializeSlides();
}, 300);

// 监听props变化
watch(() => props.heroSlides, async () => {
  if (props.heroSlides && props.heroSlides.length > 0) {
    await initializeSlides();
  }
}, { immediate: true });

onMounted(async () => {
  showHeroSlide(0);
  slideInterval = setInterval(nextHeroSlide, 5000);
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  clearInterval(slideInterval);
  window.removeEventListener('resize', handleResize);
});
</script>
