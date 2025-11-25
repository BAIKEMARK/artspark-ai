<template>
  <section id="idea-generator" class="feature-panel">
    <h2>创意灵感 & 绘画练习</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="灵感主题:">
        <el-input
          v-model="theme"
          placeholder="例如：春天, 节日"
          clearable
          @keyup.enter="generate"
        >
          <template #suffix>
            <VoiceInputButton @update:text="handleVoiceInput" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
        >
          生成灵感
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

    <div v-if="result?.length > 0" class="practice-container">
      <div v-for="(idea, index) in result" :key="index" class="practice-card">
        <div class="card-header">
          <h3>🎨 练习主题：{{ idea.name }}</h3>
          <p class="desc">{{ idea.description }}</p>
        </div>

        <div class="card-body">
          <div class="left-panel">
            <div class="panel-label">第一步：观察并临摹</div>
            <ImageResult :image-url="idea.exampleImage" :alt-text="idea.name" :filename="`${idea.name}.png`" />
          </div>

          <div class="right-panel">
            <div class="panel-label">第二步：拍照交作业</div>

            <div v-if="!idea.critique" class="upload-area">
              <el-upload
                action="#"
                list-type="picture-card"
                :auto-upload="false"
                :on-change="(file) => handleFile(file, index)"
                :limit="1"
              >
                <el-icon><Camera /></el-icon>
                <span>拍作业</span>
              </el-upload>
              <el-button type="primary" @click="submitHomework(index)" :loading="critiqueApi.isLoading.value && currentIndex === index">
                让小艺老师点评
              </el-button>
            </div>

            <div v-else class="critique-result">
              <div class="teacher-avatar">👩‍🏫 小艺老师说：</div>
              <div class="critique-text">{{ idea.critique }}</div>
              <el-rate v-model="idea.stars" disabled />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';
import { Camera } from '@element-plus/icons-vue';

const theme = ref('');
const { isLoading, error, result, execute } = useAIApi('/api/generate-ideas', { initialResult: [] });
const critiqueApi = useAIApi('/api/critique-homework');

const studentWork = ref([]);
const currentIndex = ref(null);

const handleVoiceInput = (text) => {
  theme.value += text;
};

async function generate() {
  if (!theme.value) {
    error.value = '请输入灵感主题';
    return;
  }
  try {
    await execute({ theme: theme.value });
    studentWork.value = result.value.map(() => null); // Reset student work
  } catch (e) {
    console.error(e);
  }
}

const handleFile = (file, index) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    studentWork.value[index] = e.target.result;
  };
  reader.readAsDataURL(file.raw);
};

async function submitHomework(index) {
  if (!studentWork.value[index]) {
    critiqueApi.error.value = '请先上传你的作品图片';
    return;
  }
  currentIndex.value = index;
  try {
    const idea = result.value[index];
    await critiqueApi.execute({
      theme: idea.name,
      student_image: studentWork.value[index],
    });
    if (critiqueApi.result.value) {
      idea.critique = critiqueApi.result.value.critique;
      idea.stars = critiqueApi.result.value.stars;
    }
  } catch (e) {
    console.error(e);
  } finally {
    currentIndex.value = null;
  }
}
</script>

<style scoped>
.practice-card {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.card-header h3 {
  margin-top: 0;
}
.card-header .desc {
  font-size: 0.9em;
  color: #606266;
}
.card-body {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}
.left-panel, .right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.panel-label {
  font-weight: bold;
  font-size: 0.95em;
  color: #303133;
  margin-bottom: 5px;
}
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
.critique-result {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}
.teacher-avatar {
  font-weight: bold;
  margin-bottom: 10px;
}
.critique-text {
  margin-bottom: 10px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .card-body {
    flex-direction: column;
  }
}
</style>
