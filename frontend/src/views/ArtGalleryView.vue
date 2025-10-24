<template>
  <section id="art-gallery" class="feature-panel">
    <h2>艺术画廊 (Met Museum)</h2>

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
            <p><strong>{{ art.artist || 'Unknown Artist' }}</strong></p>
            <p>{{ art.date || 'N/A' }}</p>
            <p><em>{{ art.medium || 'N/A' }}</em></p>
            <el-link type="primary" :href="art.metUrl" target="_blank" rel="noopener">
              查看详情
            </el-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue'; // 导入图标

const departments = ref([]);
const filters = reactive({ departmentId: '', q: '', activeTags: {} });
const isLoading = ref(false);
const error = ref('');
const results = ref([]);

// ... (tagGroups 数组定义保持不变)
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

// ... (loadDepartments, toggleTag, isTagActive, search 函数保持不变)
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
  } catch (e)
 {
    error.value = `搜索失败: ${e.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadDepartments);
</script>

<style scoped>
/* 我们可以保留一些特定的样式，并移除 main.css 中的旧样式 */
.tag-card-container {
  margin-top: 10px;
  margin-bottom: 25px;
  background-color: #FDFDFD;
}

.card-header {
  font-weight: 500;
}

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

/* 保持 main.css 中 gallery-card-content 的样式 */
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
</style>