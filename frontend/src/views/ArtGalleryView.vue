<template>
  <section id="art-gallery" class="feature-panel">
    <h2>艺术画廊 </h2>

    <el-form label-position="top">
      <el-form-item label="第一步：选择一个展厅">
        <el-select
          v-model="filters.departmentId"
          placeholder="所有展厅"
          style="width: 100%; max-width: 400px;"
          filterable
        >
          <el-option value="">所有展厅</el-option>
          <el-option v-for="dept in departments" :key="dept.departmentId" :label="dept.displayName" :value="dept.departmentId" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-card shadow="never" class="tag-card-container">
      <template #header>
        <div class="card-header">
          <span>第二步：快速筛选</span>
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
      <el-form-item label="第三步：辅助搜索 (可选)">
        <el-input
          v-model="filters.q"
          placeholder="在以上筛选结果中搜索，例如：Monet, cat"
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
          应用筛选并查看
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
            :preview-src-list="[art.imageUrl]"
            hide-on-click-modal
            preview-teleported
            style="width: 100%; height: 200px;"
          />
          <div class="gallery-card-content">
            <h3>{{ art.title }}</h3>
            <p><strong>{{ art.artist || '未知艺术家' }}</strong></p>
            <p>{{ art.date || 'N/A' }}</p>
            <p><em>{{ art.medium || 'N/A' }}</em></p>

            <el-button
              type="primary"
              plain
              size="small"
              @click="openArtworkDetail(art)"
            >
              <i class="icon ph-bold ph-eye"></i>
              查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
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
        />
      </div>
      <div class="artwork-info-wrapper">
        <h3>{{ selectedArtwork.title }}</h3> <p><strong>{{ selectedArtwork.artist }}</strong></p> <p>{{ selectedArtwork.date }} | <em>{{ selectedArtwork.medium }}</em></p> <el-divider />
        <h4><i class="icon ph-bold ph-robot"></i> 小艺为你讲解</h4>

        <el-skeleton :rows="5" animated v-if="isExplainLoading" />

        <el-alert v-if="explainError" :title="explainError" type="error" show-icon />
        <div v-if="explainResult?.ai_explanation" class="ai-explanation" v-html="formattedAIExplanation"></div>

        <el-divider />
        <h4><i class="icon ph-bold ph-scroll"></i> 官方介绍 (中文)</h4>
        <el-skeleton :rows="8" animated v-if="isExplainLoading" />
        <el-alert v-if="explainError" :title="explainError" type="error" show-icon />
        <div v-if="explainResult?.original_description_zh" class="original-explanation">
          <p class="original-explanation-text">{{ explainResult.original_description_zh }}</p>
        </div>

        <el-divider />

        <el-link type="info" :href="selectedArtwork.metUrl" target="_blank" rel="noopener">
          访问博物馆官网 <i class="icon ph-bold ph-arrow-up-right"></i>
        </el-link>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { useAIApi } from '../composables/useAIApi.js'; // 导入 useAIApi
import { marked } from 'marked'; // 导入 marked

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
const formattedAIExplanation = computed(() => {
  return explainResult.value && explainResult.value.ai_explanation && explainResult.value.ai_explanation.content
    ? marked(explainResult.value.ai_explanation.content)
    : '';
});

// [新增] 打开弹窗并触发 AI 讲解
function openArtworkDetail(art) {
  selectedArtwork.value = art;
  dialogVisible.value = true;

  // 重置之前的讲解结果
  explainResult.value = null;
  explainError.value = '';


  fetchExplanation({
    id: art.id, // 传递 objectID
    title: art.original_title || art.title,
    artist: art.original_artist || art.artist,
    medium: art.original_medium || art.medium,
    date: art.date,
  });
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
      headers: {'Content-Type': 'application/json'},
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

<style scoped>

.tag-card-container {
  margin-top: 10px;
  margin-bottom: 25px;
  background-color: #FDFDFD;
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
}

#gallery-result {
  text-align: left;
  margin-top: 20px;
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