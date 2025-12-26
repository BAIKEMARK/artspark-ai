<template>
  <section id="style-workshop" class="page-container">

    <div class="header-section">
      <h2 class="page-title">{{ $t('views.styleWorkshop.title') }}</h2>
      <p class="subtitle">{{ $t('views.styleWorkshop.subtitle') }}</p>
    </div>

    <el-tabs v-model="activeMode" type="border-card" class="mode-tabs">

      <el-tab-pane name="portrait">
        <template #label>
          <span class="custom-tab-label">
            <i class="ph-bold ph-user-focus"></i> {{ $t('views.styleWorkshop.portraitMode') }}
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            :title="$t('views.styleWorkshop.portraitAlert')"
            type="primary"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form label-position="top" @submit.prevent="generatePortrait">
            <el-form-item :label="$t('views.styleWorkshop.step1Portrait')">
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
                  <span>{{ $t('views.styleWorkshop.uploadPortrait') }}</span>
                </div>
              </el-upload>
            </el-form-item>

            <el-tabs v-model="portraitStyleTab" class="inner-tabs">
              <el-tab-pane :label="$t('views.styleWorkshop.presetStyle')" name="preset">
                <el-form-item :label="$t('views.styleWorkshop.step2Style')">
                   <el-select
                      v-model="presetStyleIndex"
                      :placeholder="$t('views.styleWorkshop.selectStyle')"
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
              <el-tab-pane :label="$t('views.styleWorkshop.customReference')" name="custom">
                <el-form-item :label="$t('views.styleWorkshop.step2Reference')">
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
                      <span>{{ $t('views.styleWorkshop.styleReference') }}</span>
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
              <i class="ph-bold ph-magic-wand"></i> {{ $t('views.styleWorkshop.startTransform') }}
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
            :alt-text="$t('views.styleWorkshop.portraitMode')"
            filename="portrait-art.png"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="creative">
        <template #label>
          <span class="custom-tab-label">
            <i class="ph-bold ph-paint-brush-broad"></i> {{ $t('views.styleWorkshop.artisticMode') }}
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            :title="$t('views.styleWorkshop.artisticAlert')"
            type="primary"
            show-icon
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form label-position="top" @submit.prevent="generateCreative">
            <el-form-item :label="$t('views.styleWorkshop.step1Content')">
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
                  <span>{{ $t('views.styleWorkshop.uploadOriginal') }}</span>
                </div>
              </el-upload>
            </el-form-item>

            <el-tabs v-model="creativeStyleTab" class="inner-tabs">
              <el-tab-pane :label="$t('views.styleWorkshop.textInstruction')" name="text">
                <el-form-item :label="$t('views.styleWorkshop.step2Instruction')">
                  <el-input
                    v-model="textPrompt"
                    type="textarea"
                    :rows="3"
                    :placeholder="$t('views.styleWorkshop.instructionPlaceholder')"
                    resize="none"
                  />
                   <div class="voice-btn-wrapper">
                      <VoiceInputButton @update:text="(t) => textPrompt += t" />
                   </div>
                </el-form-item>
              </el-tab-pane>
              <el-tab-pane :label="$t('views.styleWorkshop.imageStyle')" name="image">
                <el-form-item :label="$t('views.styleWorkshop.step2StyleImage')">
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
                      <span>{{ $t('views.styleWorkshop.styleReference') }}</span>
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
              <i class="ph-bold ph-paint-bucket"></i> {{ $t('views.styleWorkshop.startRedraw') }}
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
            :alt-text="$t('views.styleWorkshop.artisticMode')"
            filename="creative-art.png"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAIApi } from '../composables/useAIApi.js';
import { useUploadLimiter } from '../composables/useUploadLimiter.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';

const { t } = useI18n();

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

// 预设风格数据 (使用 computed 以支持 i18n)
const presetStyles = computed(() => [
  { value: 0, label: t('views.styleWorkshop.presetStyles.vintage'), description: 'Classic American or Japanese vintage comic style' },
  { value: 1, label: t('views.styleWorkshop.presetStyles.3dFairy'), description: 'Disney or Pixar-like 3D cartoon style' },
  { value: 2, label: t('views.styleWorkshop.presetStyles.anime'), description: 'Modern popular Japanese anime art style' },
  { value: 3, label: t('views.styleWorkshop.presetStyles.fresh'), description: 'Light, elegant, and fresh illustration style' },
  { value: 4, label: t('views.styleWorkshop.presetStyles.futuristic'), description: 'Futuristic style with cyberpunk or sci-fi elements' },
  { value: 5, label: t('views.styleWorkshop.presetStyles.traditional'), description: 'Traditional Chinese ink or Gongbi painting style' },
  { value: 6, label: t('views.styleWorkshop.presetStyles.general'), description: 'Realistic style depicting ancient generals' },
  { value: 7, label: t('views.styleWorkshop.presetStyles.colorful'), description: 'Highly saturated and vibrant cartoon style' },
  { value: 8, label: t('views.styleWorkshop.presetStyles.elegant'), description: 'Fresh and elegant Chinese style illustration' },
  { value: 9, label: t('views.styleWorkshop.presetStyles.newYear'), description: 'Festive style with Chinese New Year elements' },
  { value: 14, label: t('views.styleWorkshop.presetStyles.gongbi'), description: 'Delicate and refined Chinese Gongbi painting style'},
  {value: 15, label: t('views.styleWorkshop.presetStyles.celebration'), description: 'New Year painting or traditional festival decoration style'},
  {value: 30, label: t('views.styleWorkshop.presetStyles.fairyWorld'), description: 'Dreamy fairy tale illustration style'},
  {value: 31, label: t('views.styleWorkshop.presetStyles.clayWorld'), description: 'Cute clay or plasticine texture'},
  {value: 32, label: t('views.styleWorkshop.presetStyles.pixelWorld'), description: 'Retro 8-bit or 16-bit pixel game style'},
  {value: 33, label: t('views.styleWorkshop.presetStyles.adventureWorld'), description: 'Fantasy adventure game or illustration style'},
  {value: 34, label: t('views.styleWorkshop.presetStyles.mangaWorld'), description: 'Typical Japanese shonen or shojo manga style'},
  {value: 35, label: t('views.styleWorkshop.presetStyles.3dWorld'), description: 'General realistic or semi-realistic 3D rendering style'},
  {value: 36, label: t('views.styleWorkshop.presetStyles.animeWorld'), description: 'Anime style emphasizing scene and atmosphere'},
  {value: 37, label: t('views.styleWorkshop.presetStyles.handDrawn'), description: 'Illustration style with obvious hand-drawn brush strokes'},
  {value: 38, label: t('views.styleWorkshop.presetStyles.crayonWorld'), description: 'Imitating children\'s crayon drawing texture and colors'},
  {value: 39, label: t('views.styleWorkshop.presetStyles.magnetWorld'), description: 'Flat, brightly colored fridge magnet cartoon style'},
  {value: 40, label: t('views.styleWorkshop.presetStyles.badgeWorld'), description: 'Q-version character style on round badges'},
]);

// 计算当前选中的风格描述
// presetStyles 是 computed，需要使用 .value
const selectedPresetDescription = computed(() =>
    presetStyles.value.find(s => s.value === presetStyleIndex.value)?.description
);

async function generatePortrait() {
  portraitError.value = '';
  portraitResult.value = {imageUrl: null};

  if (!portraitFile.value) {
    portraitError.value = t('views.styleWorkshop.uploadPortraitError');
    return;
  }

  try {
    const portrait_image = await fileToBase64(portraitFile.value);
    let body = {portrait_image};

    if (portraitStyleTab.value === 'preset') {
      if (presetStyleIndex.value === null || presetStyleIndex.value === undefined) {
        portraitError.value = t('views.styleWorkshop.selectStyleError');
        return;
      }
      body.preset_style_index = presetStyleIndex.value;
    } else {
      if (!portraitStyleFile.value) {
        portraitError.value = t('views.styleWorkshop.uploadStyleError');
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
    creativeError.value = t('views.styleWorkshop.uploadContentError');
    return;
  }

  try {
    const content_image = await fileToBase64(creativeContentFile.value);
    let body = {content_image};

    if (creativeStyleTab.value === 'text') {
      if (!textPrompt.value) {
        creativeError.value = t('views.styleWorkshop.inputInstructionError');
        return;
      }
      body.prompt = textPrompt.value;
    } else {
      if (!creativeStyleFile.value) {
        creativeError.value = t('views.styleWorkshop.uploadStyleImageError');
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