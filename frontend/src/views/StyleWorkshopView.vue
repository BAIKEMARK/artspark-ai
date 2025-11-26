<template>
  <section id="style-workshop" class="page-container">

    <div class="header-section">
      <h2 class="page-title">风格工坊</h2>
      <p class="subtitle">探索 AI 艺术魔法：让照片瞬间拥有独特的艺术灵魂</p>
    </div>

    <el-tabs v-model="activeMode" type="border-card" class="mode-tabs">

      <el-tab-pane name="portrait">
        <template #label>
          <span class="custom-tab-label">
            <i class="ph-bold ph-user-focus"></i> 人像变身
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            title="该模式专注于人像处理，会尽可能保留人物面部特征。"
            type="primary"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form label-position="top" @submit.prevent="generatePortrait">
            <el-form-item label="第一步：上传人像照片">
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
                  <el-icon :size="28"><i class="ph-bold ph-user"></i></el-icon>
                  <span>上传人像</span>
                </div>
              </el-upload>
            </el-form-item>

            <el-tabs v-model="portraitStyleTab" class="inner-tabs">
              <el-tab-pane label="预设风格" name="preset">
                <el-form-item label="第二步：选择预设风格">
                   <el-select
                      v-model="presetStyleIndex"
                      placeholder="请选择风格"
                      style="width: 100%;"
                   >
                      <el-option
                        v-for="style in presetStyles"
                        :key="style.value"
                        :label="style.label"
                        :value="style.value"
                      />
                   </el-select>
                   <p v-if="selectedPresetDescription" class="description-text">
                     {{ selectedPresetDescription }}
                   </p>
                </el-form-item>
              </el-tab-pane>
              <el-tab-pane label="自定义参考图" name="custom">
                <el-form-item label="第二步：上传风格参考图">
                   <el-upload
                    action="#"
                    :auto-upload="false"
                    :on-change="handlePortraitStyleFileChange"
                    :on-remove="handlePortraitStyleFileRemove"
                    :limit="1"
                    list-type="picture-card"
                    :class="portraitStyleUploadClass"
                    accept="image/*"
                  >
                    <div class="upload-demo-box">
                      <el-icon :size="28"><i class="ph-bold ph-image"></i></el-icon>
                      <span>风格参考图</span>
                    </div>
                  </el-upload>
                </el-form-item>
              </el-tab-pane>
            </el-tabs>

            <el-button
              type="primary"
              @click="generatePortrait"
              :loading="portraitLoading"
              size="large"
              class="action-btn"
            >
              <i class="ph-bold ph-magic-wand"></i> 开始变身
            </el-button>
          </el-form>

          <el-alert
            v-if="portraitError"
            :title="portraitError"
            type="error"
            show-icon
            :closable="false"
            style="margin-top: 20px;"
          />
          <ImageResult
            v-if="portraitResult?.imageUrl"
            :image-url="portraitResult.imageUrl"
            alt-text="人像作品"
            filename="portrait-art.png"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="creative">
        <template #label>
          <span class="custom-tab-label">
            <i class="ph-bold ph-paint-brush-broad"></i> 艺术重绘
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            title="该模式适用于风景、静物或需要大幅改变画风的场景。"
            type="primary"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form label-position="top" @submit.prevent="generateCreative">
            <el-form-item label="第一步：上传内容图片">
              <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleCreativeContentChange"
                :on-remove="handleCreativeContentRemove"
                :limit="1"
                list-type="picture-card"
                :class="creativeContentUploadClass"
                accept="image/*"
              >
                <div class="upload-demo-box">
                  <el-icon :size="28"><i class="ph-bold ph-image-square"></i></el-icon>
                  <span>上传原图</span>
                </div>
              </el-upload>
            </el-form-item>

            <el-tabs v-model="creativeStyleTab" class="inner-tabs">
              <el-tab-pane label="文本指令" name="text">
                <el-form-item label="第二步：输入风格指令">
                  <el-input
                    v-model="textPrompt"
                    type="textarea"
                    :rows="3"
                    placeholder="例如：变成梵高风格，雪景，赛博朋克效果..."
                    resize="none"
                  />
                   <div class="voice-btn-wrapper">
                      <VoiceInputButton @update:text="(t) => textPrompt += t" />
                   </div>
                </el-form-item>
              </el-tab-pane>
              <el-tab-pane label="图像风格" name="image">
                <el-form-item label="第二步：上传风格图片">
                   <el-upload
                    action="#"
                    :auto-upload="false"
                    :on-change="handleCreativeStyleChange"
                    :on-remove="handleCreativeStyleRemove"
                    :limit="1"
                    list-type="picture-card"
                    :class="creativeStyleUploadClass"
                    accept="image/*"
                  >
                    <div class="upload-demo-box">
                      <el-icon :size="28"><i class="ph-bold ph-palette"></i></el-icon>
                      <span>风格参考图</span>
                    </div>
                  </el-upload>
                </el-form-item>
              </el-tab-pane>
            </el-tabs>

            <el-button
              type="primary"
              @click="generateCreative"
              :loading="creativeLoading"
              size="large"
              class="action-btn"
            >
              <i class="ph-bold ph-paint-bucket"></i> 开始重绘
            </el-button>
          </el-form>

          <el-alert
            v-if="creativeError"
            :title="creativeError"
            type="error"
            show-icon
            :closable="false"
            style="margin-top: 20px;"
          />
          <ImageResult
            v-if="creativeResult?.imageUrl"
            :image-url="creativeResult.imageUrl"
            alt-text="重绘作品"
            filename="creative-art.png"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import { useUploadLimiter } from '../composables/useUploadLimiter.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';

// 顶层 Tab 状态
const activeMode = ref('portrait');

// ==========================================
// 逻辑块 1: 人像变身 (Portrait)
// ==========================================
const portraitStyleTab = ref('preset');
const presetStyleIndex = ref(0);

// 上传钩子
const {
  file: portraitFile,
  handleChange: handlePortraitFileChange,
  handleRemove: handlePortraitFileRemove,
  uploadClass: portraitUploadClass
} = useUploadLimiter();

const {
  file: portraitStyleFile,
  handleChange: handlePortraitStyleFileChange,
  handleRemove: handlePortraitStyleFileRemove,
  uploadClass: portraitStyleUploadClass
} = useUploadLimiter();

// API 钩子 (独立实例)
const {
  isLoading: portraitLoading,
  error: portraitError,
  result: portraitResult,
  execute: executePortrait,
  fileToBase64
} = useAIApi('/api/portrait-workshop', { initialResult: { imageUrl: null } });

// 预设风格数据 (静态常量，无需 ref)
const presetStyles = [
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
  { value: 14, label: '国风工笔', description: '细腻精致的中国工笔画风格'},
  {value: 15, label: '恭贺新禧', description: '年画或传统节日装饰的风格'},
  {value: 30, label: '童话世界', description: '梦幻般的童话故事插画风格'},
  {value: 31, label: '黏土世界', description: '可爱的黏土或橡皮泥质感'},
  {value: 32, label: '像素世界', description: '复古的8-bit或16-bit像素游戏风格'},
  {value: 33, label: '冒险世界', description: '奇幻冒险题材的游戏或插画风格'},
  {value: 34, label: '日漫世界', description: '典型的日本少年或少女漫画风格'},
  {value: 35, label: '3D世界', description: '通用的写实或半写实3D渲染风格'},
  {value: 36, label: '二次元世界', description: '更强调场景和氛围的二次元风格'},
  {value: 37, label: '手绘世界', description: '带有明显手绘笔触感的插画风格'},
  {value: 38, label: '蜡笔世界', description: '模仿儿童蜡笔画的质感和色彩'},
  {value: 39, label: '冰箱贴世界', description: '扁平、色彩鲜亮的冰箱贴卡通风格'},
  {value: 40, label: '吧唧世界', description: '圆形徽章（吧唧）上的Q版人物风格'},
];

// 计算当前选中的风格描述
// 因为 presetStyles 现在是普通数组，直接 .find 即可，不需要 .value
const selectedPresetDescription = computed(() =>
    presetStyles.find(s => s.value === presetStyleIndex.value)?.description
);

async function generatePortrait() {
  portraitError.value = '';
  portraitResult.value = {imageUrl: null};

  if (!portraitFile.value) {
    portraitError.value = '请上传人像图片';
    return;
  }

  try {
    const portrait_image = await fileToBase64(portraitFile.value);
    let body = {portrait_image};

    if (portraitStyleTab.value === 'preset') {
      if (presetStyleIndex.value === null || presetStyleIndex.value === undefined) {
        portraitError.value = '请选择预设风格';
        return;
      }
      body.preset_style_index = presetStyleIndex.value;
    } else {
      if (!portraitStyleFile.value) {
        portraitError.value = '请上传风格参考图';
        return;
      }
      body.style_image = await fileToBase64(portraitStyleFile.value);
      body.preset_style_index = -1;
    }
    await executePortrait(body);
  } catch (e) {
    console.error(e);
  }
}

// ==========================================
// 逻辑块 2: 艺术重绘 (Creative)
// ==========================================
const creativeStyleTab = ref('text');
const textPrompt = ref('');

// 上传钩子
const {
  file: creativeContentFile,
  handleChange: handleCreativeContentChange,
  handleRemove: handleCreativeContentRemove,
  uploadClass: creativeContentUploadClass
} = useUploadLimiter();

const {
  file: creativeStyleFile,
  handleChange: handleCreativeStyleChange,
  handleRemove: handleCreativeStyleRemove,
  uploadClass: creativeStyleUploadClass
} = useUploadLimiter();

// API 钩子 (独立实例)
const {
  isLoading: creativeLoading,
  error: creativeError,
  result: creativeResult,
  execute: executeCreative
} = useAIApi('/api/creative-workshop', {initialResult: {imageUrl: null}});

async function generateCreative() {
  creativeError.value = '';
  creativeResult.value = {imageUrl: null};

  if (!creativeContentFile.value) {
    creativeError.value = '请上传内容图片';
    return;
  }

  try {
    const content_image = await fileToBase64(creativeContentFile.value);
    let body = {content_image};

    if (creativeStyleTab.value === 'text') {
      if (!textPrompt.value) {
        creativeError.value = '请输入文本指令';
        return;
      }
      body.prompt = textPrompt.value;
    } else {
      if (!creativeStyleFile.value) {
        creativeError.value = '请上传风格图片';
        return;
      }
      body.style_image = await fileToBase64(creativeStyleFile.value);
    }
    await executeCreative(body);
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 5px;
  border-bottom: none;
}

.subtitle {
  color: #666;
  font-size: 1rem;
  margin-top: 0;
}

/* Tabs 样式优化 */
.mode-tabs {
  box-shadow: var(--card-shadow);
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border-color);
}

:deep(.el-tabs__content) {
  padding: 30px;
}

:deep(.el-tabs__header) {
  background: #f9fafc;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 1.05rem;
  font-family: var(--font-serif);
}

:deep(.el-tabs__item.is-active) {
  color: var(--secondary-color);
  font-weight: bold;
  background: #fff;
}

.custom-tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-content {
  max-width: 600px;
  margin: 0 auto;
}

.inner-tabs {
  margin-top: 10px;
  margin-bottom: 20px;
}

.action-btn {
  width: 100%;
  font-size: 1.1rem;
  padding: 22px 0;
  border-radius: 8px;
}

.description-text {
  font-size: 0.85rem;
  color: #888;
  margin-top: 5px;
  line-height: 1.4;
}

.voice-btn-wrapper {
  position: absolute;
  right: 8px;
  bottom: 8px;
  z-index: 5;
}

/* 上传框样式复用 */
:deep(.el-upload--picture-card), :deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 120px;
  height: 120px;
  border-radius: 8px;
}

.upload-demo-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  gap: 5px;
}

.upload-demo-box span {
  font-size: 12px;
}

/* 隐藏已上传文件的上传框 - 必须保留以配合 useUploadLimiter */
:deep(.upload-limit-reached .el-upload--picture-card) {
  display: none;
}
</style>