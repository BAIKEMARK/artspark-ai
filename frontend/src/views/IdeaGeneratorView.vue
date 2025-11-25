<template>
  <section id="idea-generator" class="page-container">

    <div class="header-section">
      <h2 class="page-title">创意灵感 & 绘画练习</h2>
      <p class="subtitle">输入你想画的主题，AI 为你生成专属线稿教材，并像老师一样点评你的作品。</p>
    </div>

    <el-form class="search-form" @submit.prevent="generate">
      <el-form-item class="search-input-item">
        <el-input
          v-model="theme"
          placeholder="例如：森林里的聚会、未来的汽车..."
          class="huge-input"
          clearable
          @keyup.enter="generate"
        >
          <template #prefix>
            <el-icon class="input-icon" :size="20"><i class="ph-bold ph-paint-brush"></i></el-icon>
          </template>
          <template #suffix>
            <VoiceInputButton @update:text="handleVoiceInput" />
          </template>
          <template #append>
            <el-button type="primary" @click="generate" :loading="isLoading" class="generate-btn">
              <i class="ph-bold ph-magic-wand"></i> 生成教材
            </el-button>
          </template>
        </el-input>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="error-alert"
    />

    <div v-if="result?.length > 0" class="practice-list">
      <transition-group name="el-fade-in-linear">
        <div v-for="(idea, index) in result" :key="index" class="practice-card">

          <div class="card-header">
            <div class="title-group">
              <span class="index-badge">练习 {{ index + 1 }}</span>
              <h3>{{ idea.name }}</h3>
            </div>
            <p class="desc">{{ idea.description }}</p>
          </div>

          <div class="card-body">

            <div class="panel left-panel">
              <div class="panel-header">
                <i class="ph-bold ph-eye"></i>
                <span>第一步：观察参考线稿</span>
              </div>

              <div class="image-wrapper">
                 <ImageResult
                    v-if="idea.exampleImage"
                    :image-url="idea.exampleImage"
                    :alt-text="idea.name"
                    :filename="`${idea.name}-lineart.png`"
                  />
                  <div class="guide-tip">
                    <i class="ph-fill ph-lightbulb"></i>
                    <span>观察重点：{{ idea.elements }}</span>
                  </div>
              </div>
            </div>

            <div class="divider-vertical"></div>

            <div class="panel right-panel">
              <div class="panel-header">
                <i class="ph-bold ph-pencil-simple"></i>
                <span>第二步：交作业求点评</span>
              </div>

              <div v-if="!idea.critique" class="upload-canvas-area">
                 <el-upload
                    class="homework-uploader"
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="(file) => handleFile(file, index)"
                    accept="image/*"
                  >
                    <div v-if="!idea.tempImageUrl" class="uploader-placeholder">
                      <div class="icon-circle">
                        <i class="ph-bold ph-camera"></i>
                      </div>
                      <p>点击拍照 / 上传作品</p>
                    </div>
                    <img v-else :src="idea.tempImageUrl" class="homework-preview" />
                  </el-upload>

                  <div class="action-bar" v-if="idea.tempImageUrl">
                    <el-button
                      type="success"
                      size="large"
                      class="submit-btn"
                      @click="submitHomework(index)"
                      :loading="idea.submitting"
                    >
                      <i class="ph-bold ph-paper-plane-right"></i> 请老师点评
                    </el-button>
                    <el-button text bg size="small" @click.stop="clearFile(index)">重选</el-button>
                  </div>
              </div>

              <div v-else class="critique-report">
                 <div class="report-header">
                    <div class="teacher-info">
                      <el-avatar :size="32" style="background:var(--accent-color); color:white;">艺</el-avatar>
                      <span>小艺老师</span>
                    </div>
                    <el-rate v-model="idea.stars" disabled show-score text-color="#ff9900" />
                 </div>
                 <div class="report-content"><p>{{ idea.critique }}</p></div>

                 <div class="report-actions">
                   <el-button type="primary" plain size="small" @click="submitHomework(index)" :loading="idea.submitting">
                     <i class="ph-bold ph-arrows-clockwise"></i> 重新点评
                   </el-button>
                   <el-button text class="retry-btn" size="small" @click="resetHomework(index)">
                     <i class="ph-bold ph-camera"></i> 重拍 / 练下一个
                   </el-button>
                 </div>
              </div>

            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';
import { ElMessage } from 'element-plus';

const theme = ref('');
const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/generate-ideas', { initialResult: [] });
const { execute: executeCritique } = useAIApi('/api/critique-homework');

const handleVoiceInput = (text) => { theme.value += text; };

async function generate() {
  if (!theme.value) return;
  result.value = []; // 清空以显示加载状态
  try {
    await execute({ theme: theme.value });
  } catch (e) { console.error(e); }
}

function handleFile(uploadFile, index) {
  const idea = result.value[index];
  idea.tempImageUrl = URL.createObjectURL(uploadFile.raw);
  idea.tempFile = uploadFile.raw;
  result.value[index] = { ...idea }; // 触发响应式更新
}

function clearFile(index) {
  const idea = result.value[index];
  idea.tempImageUrl = null;
  idea.tempFile = null;
  result.value[index] = { ...idea };
}

function resetHomework(index) {
   const idea = result.value[index];
   idea.critique = null;
   idea.stars = 0;
   idea.tempImageUrl = null;
   idea.tempFile = null;
   result.value[index] = { ...idea };
}

async function submitHomework(index) {
  const idea = result.value[index];
  if (!idea.tempFile) return;

  idea.submitting = true;
  result.value[index] = { ...idea };

  try {
    const base64 = await fileToBase64(idea.tempFile);
    const critiqueResult = await executeCritique({
      theme: idea.name,
      student_image: base64
    });

    if (critiqueResult) {
       idea.critique = critiqueResult.critique;
       idea.stars = critiqueResult.stars || 4;
    }
  } catch (e) {
    ElMessage.error(e.message || '点评失败，请重试');
  } finally {
    idea.submitting = false;
    result.value[index] = { ...idea };
  }
}
</script>

<style scoped>
/* --- 布局容器 --- */
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}

/* --- 头部区域 (继承 main.css 的全局 h2，仅做微调) --- */
.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 10px;
}
.page-title {
  font-size: 2rem;
  margin-bottom: 10px;
  border-bottom: none; /* 移除全局 h2 的下划线 */
}
.subtitle {
  color: #666;
}

/* --- 搜索框 (大圆角胶囊风格) --- */
.search-form {
  max-width: 680px;
  margin: 0 auto 50px;
}
/* 输入框：左圆右方 */
.huge-input :deep(.el-input__wrapper) {
  border-radius: 50px 0 0 50px; /* CSS 简写：左上 右上 右下 左下 */
  padding-left: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  height: 55px;
  z-index: 1;
}
/* 清除 Append 容器默认样式 */
.huge-input :deep(.el-input-group__append) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}
/* 按钮：左方右圆 */
.huge-input :deep(.el-input-group__append .el-button) {
  border-radius: 0 50px 50px 0;
  margin: 0;
  height: 100%;
  padding: 0 30px;
  border: none;
  background-color: var(--accent-color) !important;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 4px 4px 15px rgba(0,0,0,0.08);
}
.huge-input :deep(.el-input-group__append .el-button:hover) {
  background-color: var(--accent-hover) !important;
  opacity: 0.95;
}
.input-icon {
  color: var(--accent-color);
  font-size: 1.2rem;
  margin-right: 5px;
}

/* --- 练习卡片 (复用全局变量) --- */
.practice-card {
  background: white;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-color);
  margin-bottom: 40px;
  overflow: hidden;
}

/* 标题栏 */
.card-header {
  background: linear-gradient(to right, #fcfcfc, #fff);
  padding: 15px 25px;
  border-bottom: 1px solid var(--border-color);
}
.title-group {
  display: flex; align-items: center; gap: 10px; margin-bottom: 5px;
}
.index-badge {
  background: var(--accent-color);
  color: white;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}
.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--secondary-color);
}
.desc { margin: 0; color: #888; font-size: 0.9rem; }

/* --- 双栏内容区 --- */
.card-body {
  display: flex;
  min-height: 380px;
}
.panel {
  flex: 1;
  padding: 20px;
  display: flex; flex-direction: column;
}
.panel-header {
  display: flex; align-items: center; gap: 8px;
  font-weight: 600;
  color: var(--secondary-color);
  margin-bottom: 15px;
  border-bottom: 2px solid #f2f2f2;
  padding-bottom: 8px;
}
.panel-header i { color: var(--accent-color); }

/* 左侧：教材 */
.image-wrapper {
  flex-grow: 1;
  background: var(--light-bg);
  border-radius: 8px;
  padding: 15px;
  display: flex; flex-direction: column;
}
.guide-tip {
  margin-top: 10px; background: #fff8e1; color: #b8860b; padding: 8px 12px;
  border-radius: 6px; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;
}
.divider-vertical { width: 1px; background: var(--border-color); margin: 20px 0; }

/* 右侧：互动 */
.upload-canvas-area {
  flex-grow: 1;
  display: flex; flex-direction: column; gap: 15px;
}
.homework-uploader { flex-grow: 1; display: flex; }
.homework-uploader :deep(.el-upload) {
  width: 100%; height: 100%; min-height: 200px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  background-color: #fafafa;
  transition: all 0.3s;
  display: flex; align-items: center; justify-content: center;
}
.homework-uploader :deep(.el-upload:hover) {
  border-color: var(--accent-color);
  background-color: #fffbf0;
}
.uploader-placeholder { text-align: center; color: #909399; }
.icon-circle { font-size: 24px; margin-bottom: 10px; color: var(--secondary-color); }
.homework-preview { width: 100%; height: 100%; object-fit: contain; border-radius: 6px; }
.submit-btn { width: 100%; }

/* 点评报告 */
.critique-report {
  flex-grow: 1;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  display: flex; flex-direction: column;
}
.report-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 15px; padding-bottom: 10px;
  border-bottom: 1px dashed #eee;
}
.teacher-info { display: flex; align-items: center; gap: 8px; font-weight: bold; color: var(--secondary-color); }
.report-content { flex-grow: 1; background: var(--light-bg); padding: 15px; border-radius: 8px; margin-bottom: 10px; line-height: 1.6; }

/* 底部按钮组 */
.report-actions {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: auto; padding-top: 15px; border-top: 1px dashed #eee;
}
.retry-btn { color: #909399; }
.retry-btn:hover { color: var(--secondary-color); }

/* --- 移动端适配 --- */
@media (max-width: 768px) {
  .card-body { flex-direction: column; }
  .divider-vertical { display: none; }
  .left-panel { border-bottom: 1px solid var(--border-color); }
  .homework-uploader :deep(.el-upload) { min-height: 180px; }
}

.error-alert { max-width: 680px; margin: 0 auto 20px auto; }
</style>