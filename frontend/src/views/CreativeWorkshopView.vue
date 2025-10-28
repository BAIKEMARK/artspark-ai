<template>
  <section id="creative-workshop" class="feature-panel">
    <h2>创意工坊</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="第一步：上传内容图片">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleContentFileChange"
          :on-remove="handleContentFileRemove"
          :limit="1"
          list-type="picture-card"
          :class="contentUploadClass"
          accept="image/*"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传内容图</span>
          </div>
        </el-upload>
      </el-form-item>

      <el-tabs v-model="activeTab" class="style-tabs">
        <el-tab-pane label="文本指令" name="text">
          <el-form-item label="第二步：输入文本指令">
            <el-input
              v-model="textPrompt"
              type="textarea"
              :rows="3"
              placeholder="例如：变成梵高风格，雪景，水彩画效果"
              clearable
            />
          </el-form-item>
        </el-tab-pane>

        <el-tab-pane label="图像风格" name="image">
          <el-form-item label="第二步：上传风格图片">
             <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleStyleFileChange"
              :on-remove="handleStyleFileRemove"
              :limit="1"
              list-type="picture-card"
              :class="styleUploadClass"
              accept="image/*"
            >
              <div class="upload-demo-box">
                <el-icon :size="28"><Upload /></el-icon>
                <span>点击上传风格图</span>
              </div>
            </el-upload>
          </el-form-item>
        </el-tab-pane>
      </el-tabs>

      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%; margin-top: 10px;"
          size="large"
        >
          开始创作
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

    <ImageResult
      v-if="result?.imageUrl"
      :image-url="result.imageUrl"
      alt-text="创意工坊作品"
      filename="creative-workshop.png"
    />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue';
import { useUploadLimiter } from '../composables/useUploadLimiter.js';

const activeTab = ref('text'); // 默认激活文本指令 Tab
const textPrompt = ref('');

// 内容图片上传
const {
  file: contentFile,
  handleChange: handleContentFileChange,
  handleRemove: handleContentFileRemove,
  uploadClass: contentUploadClass
} = useUploadLimiter();

// 风格图片上传
const {
  file: styleFile,
  handleChange: handleStyleFileChange,
  handleRemove: handleStyleFileRemove,
  uploadClass: styleUploadClass
} = useUploadLimiter();

// API 调用
const { isLoading, error, result, execute, fileToBase64 } = useAIApi(
  '/api/creative-workshop', // 指向新的后端 API 端点
  { initialResult: { imageUrl: null } }
);

async function generate() {
  error.value = ''; // 清除旧错误
  result.value = { imageUrl: null }; // 清除旧结果

  if (!contentFile.value) {
    error.value = '请上传内容图片';
    return;
  }

  let body = {};
  let content_image = null;

  try {
      content_image = await fileToBase64(contentFile.value);
  } catch(e) {
      error.value = `读取内容图片失败: ${e.message}`;
      return;
  }

  body.content_image = content_image;

  if (activeTab.value === 'text') {
    if (!textPrompt.value) {
      error.value = '请输入文本指令';
      return;
    }
    body.prompt = textPrompt.value;
  } else if (activeTab.value === 'image') {
    if (!styleFile.value) {
      error.value = '请上传风格图片';
      return;
    }
    try {
        const style_image = await fileToBase64(styleFile.value);
        body.style_image = style_image;
    } catch(e) {
        error.value = `读取风格图片失败: ${e.message}`;
        return;
    }
  } else {
      error.value = '无效的操作模式';
      return;
  }

  try {
    await execute(body);
  } catch (e) {
    // useAIApi 内部会处理 error.value
    console.error("创意工坊生成失败:", e);
  }
}
</script>

<style scoped>
.sub-heading {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
  margin-top: -20px;
  margin-bottom: 25px;
  text-align: center;
}

.style-tabs {
  margin-top: 15px;
}

/* 确保上传框大小一致 */
:deep(.el-upload--picture-card) {
  width: 148px;
  height: 148px;
}
:deep(.el-upload-list--picture-card .el-upload-list__item) {
    width: 148px;
    height: 148px;
}

.upload-demo-box {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 100%;
  color: var(--el-text-color-secondary);
}
.upload-demo-box span {
  font-size: 13px;
}
/* 隐藏已上传文件的上传框 */
:deep(.upload-limit-reached .el-upload--picture-card) {
  display: none;
}
</style>