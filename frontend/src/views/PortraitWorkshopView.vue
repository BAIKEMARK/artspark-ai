<template>
  <section id="portrait-workshop" class="feature-panel">
    <h2>人像工坊</h2>
    <p class="sub-heading">（将人像照片转化为不同艺术风格）</p>

    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="第一步：上传人像图片">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handlePortraitFileChange"
          :on-remove="handlePortraitFileRemove"
          :limit="1"
          list-type="picture-card"
          :class="portraitUploadClass"
          accept="image/*"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传人像图</span>
          </div>
        </el-upload>
      </el-form-item>

      <el-tabs v-model="activeTab" class="style-tabs">
        <el-tab-pane label="预设风格" name="preset">
          <el-form-item label="第二步：选择预设风格">
             <el-select
                v-model="presetStyleIndex"
                placeholder="请选择风格"
                style="width: 100%; max-width: 400px;"
             >
                <el-option
                  v-for="style in presetStyles"
                  :key="style.value"
                  :label="style.label"
                  :value="style.value"
                />
             </el-select>
             <p v-if="selectedPresetDescription" class="preset-description">
                 风格说明：{{ selectedPresetDescription }}
             </p>
          </el-form-item>
        </el-tab-pane>

        <el-tab-pane label="自定义风格" name="custom">
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
          开始变身
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
      alt-text="人像工坊作品"
      filename="portrait-workshop.png"
    />
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue';
import { useUploadLimiter } from '../composables/useUploadLimiter.js';

const activeTab = ref('preset'); // 默认激活预设风格 Tab
const presetStyleIndex = ref(0); // 默认选择第一个预设

// 人像图片上传
const {
  file: portraitFile,
  handleChange: handlePortraitFileChange,
  handleRemove: handlePortraitFileRemove,
  uploadClass: portraitUploadClass
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
  '/api/portrait-workshop', // 指向新后端 API 端点
  { initialResult: { imageUrl: null } }
);

// 定义完整的预设风格列表
const presetStyles = ref([
  { value: 0, label: '复古漫画', description: '经典的美式或日式复古漫画风格' },
  { value: 1, label: '3D童话', description: '类似于迪士尼或皮克斯动画的3D卡通风格' },
  { value: 2, label: '二次元', description: '现代流行的日系二次元动漫美术风格' },
  { value: 3, label: '小清新', description: '色彩淡雅、简约清新的插画风格' },
  { value: 4, label: '未来科技', description: '带有赛博朋克或科幻元素的未来感风格' },
  { value: 5, label: '国画古风', description: '中国传统水墨画或工笔画的人物风格' },
  { value: 6, label: '将军百战', description: '描绘古代将军戎马生涯的写实风格' },
  { value: 7, label: '炫彩卡通', description: '色彩极其鲜艳饱和的卡通风格' },
  { value: 8, label: '清雅国风', description: '清新淡雅的中国古风插画' },
  { value: 9, label: '喜迎新年', description: '充满中国新年元素的喜庆风格' },
  { value: 14, label: '国风工笔', description: '细腻精致的中国工笔画风格' },
  { value: 15, label: '恭贺新禧', description: '年画或传统节日装饰的风格' },
  { value: 30, label: '童话世界', description: '梦幻般的童话故事插画风格' },
  { value: 31, label: '黏土世界', description: '可爱的黏土或橡皮泥质感' },
  { value: 32, label: '像素世界', description: '复古的8-bit或16-bit像素游戏风格' },
  { value: 33, label: '冒险世界', description: '奇幻冒险题材的游戏或插画风格' },
  { value: 34, label: '日漫世界', description: '典型的日本少年或少女漫画风格' },
  { value: 35, label: '3D世界', description: '通用的写实或半写实3D渲染风格' },
  { value: 36, label: '二次元世界', description: '更强调场景和氛围的二次元风格' },
  { value: 37, label: '手绘世界', description: '带有明显手绘笔触感的插画风格' },
  { value: 38, label: '蜡笔世界', description: '模仿儿童蜡笔画的质感和色彩' },
  { value: 39, label: '冰箱贴世界', description: '扁平、色彩鲜亮的冰箱贴卡通风格' },
  { value: 40, label: '吧唧世界', description: '圆形徽章（吧唧）上的Q版人物风格' },
]);

// 计算属性，用于显示选中预设的描述
const selectedPresetDescription = computed(() => {
    const selected = presetStyles.value.find(s => s.value === presetStyleIndex.value);
    return selected ? selected.description : '';
});

async function generate() {
  error.value = '';
  result.value = { imageUrl: null };

  if (!portraitFile.value) {
    error.value = '请上传人像图片';
    return;
  }

  let body = {};
  let portrait_image = null;

  try {
      portrait_image = await fileToBase64(portraitFile.value);
  } catch(e) {
      error.value = `读取人像图片失败: ${e.message}`;
      return;
  }

  body.portrait_image = portrait_image;

  if (activeTab.value === 'preset') {
    if (presetStyleIndex.value === null || presetStyleIndex.value === undefined) {
      error.value = '请选择一个预设风格';
      return;
    }
    body.preset_style_index = presetStyleIndex.value;
  } else if (activeTab.value === 'custom') {
    if (!styleFile.value) {
      error.value = '请上传风格图片';
      return;
    }
    try {
        const style_image = await fileToBase64(styleFile.value);
        body.style_image = style_image;
        body.preset_style_index = -1;
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
    console.error("人像工坊生成失败:", e);
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

.preset-description {
    font-size: 0.85rem;
    color: var(--el-text-color-secondary);
    margin-top: 8px;
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