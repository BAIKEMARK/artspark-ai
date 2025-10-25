<template>
  <section id="style-workshop" class="feature-panel">
    <h2>创意风格工坊</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="艺术风格:">
        <el-select v-model="style" placeholder="请选择风格" style="width: 100%;">
          <el-option label="梵高 (后印象派)" value="梵高"></el-option>
          <el-option label="毕加索 (立体主义)" value="毕加索"></el-option>
          <el-option label="水墨画 (中国传统)" value="水墨画"></el-option>
          <el-option label="剪纸风格 (中国民间)" value="剪纸风格"></el-option>
          <el-option label="水彩画 (透明)" value="水彩画"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="上传草图/图片 (可选):">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          list-type="picture-card"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传草图</span>
          </div>
        </el-upload>
      </el-form-item>
      <el-form-item label="内容补充描述 (可选):">
        <el-input
          v-model="content"
          placeholder="例如：一只戴帽子的狗"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
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

    <el-card v-if="result?.imageUrl" class="result-card" shadow="never">
       <el-image :src="result.imageUrl" alt="风格画作" fit="contain" />
       <div class="result-content">
          <p class="style-desc">{{ result.styleDescription }}</p>
          <el-button
            type="primary"
            plain
            size="small"
            @click="downloadImage(result.imageUrl, 'style-workshop')"
          >
            <i class="icon ph-bold ph-download-simple"></i> 下载图片
          </el-button>
       </div>
    </el-card>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import { Upload } from '@element-plus/icons-vue'

const style = ref('梵高');
const content = ref('');
const workshopFile = ref(null);

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/generate-style', { initialResult: { imageUrl: null, styleDescription: '' } });

function handleFileChange(file) {
  workshopFile.value = file.raw;
}

function downloadImage(imageUrl, imageName) {
  const link = document.createElement('a');
  link.href = `/api/proxy-download?url=${encodeURIComponent(imageUrl)}`;
  link.download = `${imageName.replace(/\s/g, '_')}.png`;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function generate() {
  if (!content.value && !workshopFile.value) {
    error.value = '请输入绘制内容或上传一张草图';
    return;
  }

  try {
    let base64_image = null;
    if (workshopFile.value) {
      base64_image = await fileToBase64(workshopFile.value);
    }
    await execute({ content: content.value, style: style.value, base64_image });
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.result-card {
  margin-top: 20px;
}
.result-content {
  padding: 14px;
  text-align: center;
}
.style-desc {
  margin-bottom: 15px;
  color: #606266;
}
</style>
