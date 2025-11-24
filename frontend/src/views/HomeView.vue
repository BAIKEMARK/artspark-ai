<template>
  <header id="home-view" class="view-panel active">
    <div class="hero-gallery">
      <div class="slider-container">
        <div
          v-for="(slide, index) in heroSlides"
          :key="index"
          class="slide"
          :class="{ active: currentHeroSlide === index }"
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
      <h1>艺启智AI：赋能创意美术教育</h1>
      <p>触手可及的AI艺术工具，点燃每个学生的创造火花</p>

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
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  heroSlides: Array,
  featureCards: Array,
});

defineEmits(['navigate']);

const currentHeroSlide = ref(0);
let slideInterval = null;

const showHeroSlide = (index) => {
  currentHeroSlide.value = index;
};

const nextHeroSlide = () => {
  currentHeroSlide.value = (currentHeroSlide.value + 1) % props.heroSlides.length;
};

onMounted(() => {
  showHeroSlide(0);
  slideInterval = setInterval(nextHeroSlide, 5000);
});

onUnmounted(() => {
  clearInterval(slideInterval);
});
</script>