<template>
  <section id="art-gallery" class="page-container">

    <div class="header-section">
      <h2 class="page-title">{{ $t('views.artGallery.title') }}</h2>
      <p class="subtitle">{{ $t('views.artGallery.subtitle') }}</p>
    </div>

    <div class="content-wrapper">

    <el-form label-position="top">
      <el-form-item :label="$t('views.artGallery.step1')">
        <el-select
          v-model="filters.departmentId"
          :placeholder="$t('views.artGallery.allDepartments')"
          style="width: 100%; max-width: 400px;"
          filterable
        >
          <el-option value="">{{ $t('views.artGallery.allDepartments') }}</el-option>
          <el-option v-for="dept in departments" :key="dept.departmentId" :label="dept.displayName" :value="dept.departmentId" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-card shadow="never" class="tag-card-container">
      <template #header>
        <div class="card-header">
          <span>{{ $t('views.artGallery.step2') }}</span>
        </div>
      </template>
      <div v-for="group in tagGroups" :key="group.title" class="tag-group">
        <el-text tag="h4" class="tag-group-title">{{ group.title }}：</el-text>
        <el-space wrap>
          <el-check-tag
            v-for="tag in group.tags"
            :key="tag.label"
            :checked="isTagActive(tag)"
            @change="toggleTag(tag)"
          >
            {{ tag.label }}
          </el-check-tag>
        </el-space>
      </div>
    </el-card>

    <el-form label-position="top" class="aux-search-form">
      <el-form-item :label="$t('views.artGallery.step3')">
        <el-input
          v-model="filters.q"
          :placeholder="$t('views.artGallery.searchPlaceholder')"
          clearable
          style="max-width: 400px;"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="search"
          :loading="isLoading"
          :icon="Search"
          style="width: 100%; max-width: 400px;"
        >
          {{ $t('views.artGallery.applyFilters') }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      style="margin-top: 20px;"
    />

    <el-row :gutter="20" id="gallery-result" v-if="results.length > 0">
      <el-col
        v-for="art in results"
        :key="art.id"
        :xs="24" :sm="12" :md="8"
        style="margin-bottom: 20px;"
      >
        <el-card shadow="hover" :body-style="{ padding: '0px' }">
          <el-image
            :src="art.imageUrl"
            :alt="art.title"
            fit="cover"
            lazy
            hide-on-click-modal
            preview-teleported
            style="width: 100%; height: 200px; cursor: pointer;"
            @click="openArtworkDetail(art)"
          />
          <div class="gallery-card-content">
            <h3>{{ art.title }}</h3>
            <p><strong>{{ art.artist || $t('views.artGallery.unknownArtist') }}</strong></p>
            <p>{{ art.date || 'N/A' }}</p>
            <p><em>{{ art.medium || 'N/A' }}</em></p>

            <el-button
              type="primary"
              plain
              size="small"
              @click="openArtworkDetail(art)"
            >
              <i class="icon ph-bold ph-eye"></i>
              {{ $t('views.artGallery.viewDetails') }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    </div>

  </section>

  <el-dialog
    v-model="dialogVisible"
    :title="selectedArtwork?.title"
    width="70%"
    top="5vh"
  >
    <div v-if="selectedArtwork" class="artwork-detail-dialog">
      <div class="artwork-image-wrapper">
        <el-image
          :src="selectedArtwork.imageUrl.replace('small', 'large')"
          :alt="selectedArtwork.title"
          fit="contain"
          lazy
          :preview-src-list="[selectedArtwork.imageUrl.replace('small', 'large')]"
          hide-on-click-modal
          preview-teleported
        />
      </div>
      <div class="artwork-info-wrapper">
        <h3>{{ selectedArtwork.title }}</h3> <p><strong>{{ selectedArtwork.artist }}</strong></p> <p>{{ selectedArtwork.date }} | <em>{{ selectedArtwork.medium }}</em></p> <el-divider />
        <h4><i class="icon ph-bold ph-robot"></i> {{ $t('views.artGallery.aiExplanation') }}</h4>

        <el-skeleton :rows="5" animated v-if="isExplainLoading" />

        <el-alert v-if="explainError" :title="explainError" type="error" show-icon />
        <div v-if="explainResult?.ai_explanation" class="ai-explanation" v-html="formattedAIExplanation"></div>

        <el-divider />
        <h4><i class="icon ph-bold ph-scroll"></i> {{ $t('views.artGallery.officialDescription') }}</h4>
        <el-skeleton :rows="8" animated v-if="isExplainLoading" />
        <el-alert v-if="explainError" :title="explainError" type="error" show-icon />
        <div v-if="explainResult?.original_description_zh" class="original-explanation">
          <p class="original-explanation-text">{{ explainResult.original_description_zh }}</p>
        </div>

        <el-divider />

        <el-link type="info" :href="selectedArtwork.metUrl" target="_blank" rel="noopener">
          {{ $t('views.artGallery.visitMuseum') }} <i class="icon ph-bold ph-arrow-up-right"></i>
        </el-link>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { Search } from '@element-plus/icons-vue';
import { useAIApi } from '../composables/useAIApi.js'; // 导入 useAIApi
import { marked } from 'marked'; // 导入 marked

const { t } = useI18n();

const departments = ref([]);
const filters = reactive({ departmentId: '', q: '', activeTags: {} });
const isLoading = ref(false);
const error = ref('');
const results = ref([]);

// [弹窗状态]
const dialogVisible = ref(false);
const selectedArtwork = ref(null);
// [新增] AI 讲解的状态
const {
  isLoading: isExplainLoading,
  error: explainError,
  result: explainResult,
  execute: fetchExplanation
} = useAIApi('/api/gallery/explain');
const tagGroups = computed(() => [
    { title: t('views.artGallery.tags.popular'), tags: [{ label: t('views.artGallery.tags.museumHighlight'), type: 'isHighlight', value: 'true' }] },
    { title: t('views.artGallery.tags.era'), tags: [
        { label: t('views.artGallery.tags.era19th'), type: 'dateRange', begin: '1800', end: '1900' },
        { label: t('views.artGallery.tags.eraRenaissance'), type: 'dateRange', begin: '1400', end: '1600' },
        { label: t('views.artGallery.tags.eraClassical'), type: 'dateRange', begin: '-1000', end: '400' },
    ]},
    { title: t('views.artGallery.tags.medium'), tags: [
        { label: t('views.artGallery.tags.paintings'), type: 'medium', value: 'Paintings' },
        { label: t('views.artGallery.tags.sculpture'), type: 'medium', value: 'Sculpture' },
        { label: t('views.artGallery.tags.ceramics'), type: 'medium', value: 'Ceramics' },
    ]},
    { title: t('views.artGallery.tags.region'), tags: [
        { label: t('views.artGallery.tags.china'), type: 'geoLocation', value: 'China' },
        { label: t('views.artGallery.tags.japan'), type: 'geoLocation', value: 'Japan' },
        { label: t('views.artGallery.tags.europe'), type: 'geoLocation', value: 'Europe' },
        { label: t('views.artGallery.tags.egypt'), type: 'geoLocation', value: 'Egypt' },
    ]},
]);
const formattedAIExplanation = computed(() => {
  return explainResult.value && explainResult.value.ai_explanation && explainResult.value.ai_explanation.content
    ? marked(explainResult.value.ai_explanation.content)
    : '';
});

async function openArtworkDetail(art) {
  selectedArtwork.value = art;
  dialogVisible.value = true;

  // 重置状态
  explainResult.value = null;
  explainError.value = '';
  isExplainLoading.value = true; // 手动设置为加载中

  const cacheKey = `artExplain_${art.id}`; // 定义缓存键

  try {
    // 1. 尝试从 sessionStorage 读取缓存
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading explanation from cache for key:", cacheKey);
      explainResult.value = JSON.parse(cachedData); // 使用缓存数据
      isExplainLoading.value = false; // 结束加载状态
      return; // 提前结束函数
    }
  } catch (e) {
    console.error("Error reading explanation from sessionStorage:", e);
    // 如果读取缓存出错，则继续执行 API 请求
  }

  // 2. 如果没有缓存，则发起 API 请求
  console.log("Fetching explanation from API for key:", cacheKey);
  try {
    const explanationData = await fetchExplanation({ // 等待 execute 函数
      id: art.id, // 传递 objectID
      title: art.original_title || art.title,
      artist: art.original_artist || art.artist,
      medium: art.original_medium || art.medium,
      date: art.date,
    });

    // 3. 缓存结果 (useAIApi的execute在成功时会返回result.value)
    // 检查 explanationData (即 result.value) 是否有效，并且没有发生错误
    if (explanationData && !explainError.value) {
      try {
        sessionStorage.setItem(cacheKey, JSON.stringify(explanationData));
      } catch (e) {
        console.error("Error writing explanation to sessionStorage:", e);
      }
    }
  } catch (e) {
    console.error("fetchExplanation failed:", e);
  }
}
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
  // ElCheckTag 的 @change 事件会触发，所以我们直接修改状态
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

  // --- 缓存逻辑 ---
  const searchFilters = { // 先构建筛选条件对象
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

  // 1. 生成缓存键 (基于筛选条件)
  const cacheKey = `artGallerySearch_${JSON.stringify(searchFilters)}`;

  try {
    // 2. 尝试从 sessionStorage 读取缓存
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading search results from cache for key:", cacheKey);
      results.value = JSON.parse(cachedData); // 使用缓存数据
      isLoading.value = false; // 加载完成
      return; // 提前结束函数，不发起 API 请求
    }
  } catch (e) {
    console.error("Error reading from sessionStorage:", e);
  }

  results.value = [];
  try {
    const response = await fetch('/api/gallery/search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(searchFilters),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `请求失败: ${response.status}`);
    }
    const resultData = await response.json();
    results.value = resultData.artworks;

    try {
      console.log("Saving search results to cache for key:", cacheKey);
      sessionStorage.setItem(cacheKey, JSON.stringify(results.value));
    } catch (e) {
      console.error("Error writing to sessionStorage:", e);
    }

    if (resultData.artworks.length === 0) {
      error.value = t('views.artGallery.noResults');
    }
  } catch (e) {
    error.value = `${t('views.artGallery.searchFailed')}: ${e.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadDepartments);
</script>

<style scoped>
/* --- 布局容器 --- */
.page-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* --- 头部区域 --- */
.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 10px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 10px;
  border-bottom: none;
  font-family: var(--font-serif);
  color: var(--secondary-color);
}

.subtitle {
  color: var(--dark-text);
  font-size: 1rem;
  margin-top: 0;
  font-weight: 500;
  opacity: 0.8;
}

/* --- 内容区域 --- */
.content-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-color);
  padding: 40px;
}

/* --- 表单样式 --- */
.el-form {
  max-width: 600px;
  margin: 0 auto 30px auto;
}

.el-form-item {
  margin-bottom: 25px;
}

/* --- 标签卡片 --- */
.tag-card-container {
  margin: 20px auto 30px auto;
  background-color: #FDFDFD;
  border-radius: 12px;
  max-width: 800px;
}
.card-header { font-weight: 500; }
.tag-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed var(--border-color);
}
.tag-group:last-child {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}
.tag-group-title {
  margin: 0;
  font-size: 0.95rem;
  color: var(--secondary-color);
  width: 100px;
}

.aux-search-form {
  margin-top: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

#gallery-result {
  text-align: left;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}

.gallery-card-content {
  padding: 15px;
}

.gallery-card-content h3 {
  font-size: 1.1rem;
  color: var(--secondary-color);
  margin: 0 0 10px 0;
  font-family: var(--font-serif);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 2.8em;
}

.gallery-card-content p {
  font-size: 0.85rem;
  color: #555;
  margin: 4px 0;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gallery-card-content p:last-of-type {
  margin-bottom: 10px;
}

/* 弹窗内部样式 */
.artwork-detail-dialog {
  display: flex;
  gap: 20px;
}
.artwork-image-wrapper {
  flex: 3; /* 图片占 3/5 */
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
}
.artwork-image-wrapper .el-image {
  max-height: 75vh;
}
.artwork-info-wrapper {
  flex: 2; /* 信息占 2/5 */
}
.artwork-info-wrapper h3 {
  font-family: var(--font-serif);
  font-size: 1.6rem;
  color: var(--secondary-color);
  margin-top: 0;
}
.artwork-info-wrapper h4 {
  font-family: var(--font-serif);
  color: var(--secondary-color);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
}
.artwork-info-wrapper .icon {
  font-size: 1.2rem;
}
.ai-explanation {
  background-color: #fdfdfd;
  padding: 10px 15px;
  border-radius: 8px;
  line-height: 1.8;
  font-size: 0.95rem;
}

.ai-explanation :deep(p) {
  margin: 0.5em 0;
}

.ai-explanation :deep(ul), .ai-explanation :deep(ol) {
  padding-left: 20px;
}
/* [新增] 官方原文样式 */
.original-explanation {
  background-color: #f8f9fa; /* 用不同的背景色区分 */
  padding: 10px 15px;
  border-radius: 8px;
  line-height: 1.7;
  font-size: 0.9rem;
  color: #495057;
}
.original-explanation p {
  margin: 0.5em 0;
}
.el-link .icon {
  font-size: 0.8rem;
  margin-left: 2px;
}

/* 弹窗响应式 */
@media (max-width: 992px) {
  .artwork-detail-dialog {
    flex-direction: column;
  }
  .artwork-image-wrapper {
    min-height: auto;
    max-height: 50vh;
  }
}
.original-explanation {
  background-color: #f8f9fa; /* 用不同的背景色区分 */
  padding: 10px 15px;
  border-radius: 8px;
  line-height: 1.7;
  font-size: 0.9rem;
  color: #495057;
}

/* [新增] 添加这个规则以处理换行 */
.original-explanation-text {
  white-space: pre-line; /* 保留换行符 */
  margin: 0; /* 移除 p 标签默认的 margin */
}
</style>