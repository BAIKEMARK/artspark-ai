<template>
  <section id="art-gallery" class="feature-panel">
    <h2>艺术画廊 (Met Museum)</h2>

    <div class="form-group">
      <label for="gallery-department-select">第一步：选择一个展厅</label>
      <select id="gallery-department-select" v-model="filters.departmentId">
        <option value="">所有展厅</option>
        <option v-for="dept in departments" :key="dept.departmentId" :value="dept.departmentId">{{ dept.displayName }}</option>
      </select>
    </div>

    <div class="gallery-tag-groups">
      <div class="tag-group" v-for="group in tagGroups" :key="group.title">
        <h4>{{ group.title }}：</h4>
        <button v-for="tag in group.tags" :key="tag.label" class="tag-btn" :class="{ active: isTagActive(tag) }" @click="toggleTag(tag)">
          {{ tag.label }}
        </button>
      </div>
    </div>

    <div class="form-group gallery-aux-search">
      <label for="gallery-search-input">辅助搜索 (可选):</label>
      <input type="text" id="gallery-search-input" placeholder="在以上筛选结果中搜索，例如：Monet, cat" v-model="filters.q" />
    </div>

    <button id="search-gallery-btn" class="cta-btn" @click="search" :disabled="isLoading">
      <i class="icon ph-bold ph-magnifying-glass"></i>
      应用筛选并查看
    </button>

    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <div id="gallery-result" v-if="results.length > 0">
      <div class="gallery-card" v-for="art in results" :key="art.id">
        <img :src="art.imageUrl" :alt="art.title" loading="lazy" />
        <div class="gallery-card-content">
          <h3>{{ art.title }}</h3>
          <p><strong>{{ art.artist || 'Unknown Artist' }}</strong></p>
          <p>{{ art.date || 'N/A' }}</p>
          <p><em>{{ art.medium || 'N/A' }}</em></p>
          <a :href="art.metUrl" target="_blank" rel="noopener">查看详情</a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';

const departments = ref([]);
const filters = reactive({ departmentId: '', q: '', activeTags: {} });
const isLoading = ref(false);
const error = ref('');
const results = ref([]);

const tagGroups = [
    { title: '热门筛选', tags: [{ label: '博物馆精选', type: 'isHighlight', value: 'true' }] },
    { title: '时代', tags: [
        { label: '19世纪 (印象派等)', type: 'dateRange', begin: '1800', end: '1900' },
        { label: '文艺复兴 (1400-1600)', type: 'dateRange', begin: '1400', end: '1600' },
        { label: '古典时期 (希腊/罗马)', type: 'dateRange', begin: '-1000', end: '400' },
    ]},
    { title: '媒介', tags: [
        { label: '绘画', type: 'medium', value: 'Paintings' },
        { label: '雕塑', type: 'medium', value: 'Sculpture' },
        { label: '陶瓷', type: 'medium', value: 'Ceramics' },
    ]},
    { title: '地区', tags: [
        { label: '中国', type: 'geoLocation', value: 'China' },
        { label: '日本', type: 'geoLocation', value: 'Japan' },
        { label: '欧洲', type: 'geoLocation', value: 'Europe' },
        { label: '埃及', type: 'geoLocation', value: 'Egypt' },
    ]},
];

async function loadDepartments() {
  try {
    const response = await fetch('/api/gallery/departments');
    if (!response.ok) throw new Error('Failed to load departments');
    const data = await response.json();
    departments.value = data.departments;
  } catch (e) {
    console.error("Error loading gallery departments:", e);
  }
}

function toggleTag(tag) {
  const currentActiveTag = filters.activeTags[tag.type];
  if (currentActiveTag && currentActiveTag.label === tag.label) {
    delete filters.activeTags[tag.type];
  } else {
    filters.activeTags[tag.type] = tag;
  }
}

function isTagActive(tag) {
  const activeTag = filters.activeTags[tag.type];
  return activeTag && activeTag.label === tag.label;
}

async function search() {
  isLoading.value = true;
  error.value = '';
  results.value = [];
  try {
    const searchFilters = {
      q: filters.q || '*',
      departmentId: filters.departmentId,
    };
    Object.values(filters.activeTags).forEach(tag => {
      if (tag.type === 'dateRange') {
        searchFilters.dateBegin = tag.begin;
        searchFilters.dateEnd = tag.end;
      } else {
        searchFilters[tag.type] = tag.value;
      }
    });

    const response = await fetch('/api/gallery/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(searchFilters),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || `请求失败: ${response.status}`);
    }
    const resultData = await response.json();
    results.value = resultData.artworks;
    if (resultData.artworks.length === 0) {
      error.value = '没有找到符合条件的作品。';
    }
  } catch (e) {
    error.value = `搜索失败: ${e.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadDepartments);
</script>

