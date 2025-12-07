<template>
  <el-drawer
    :model-value="isOpen"
    direction="rtl"
    @update:modelValue="$emit('close')"
    size="360px"
  >
    <template #header>
      <div class="drawer-header">
        <i class="icon ph-bold ph-gear"></i>
        <span>{{ t('settings.title') }}</span>
      </div>
    </template>

    <el-scrollbar>
      <el-form label-position="top" class="settings-form">

        <el-text type="info" class="setting-group-title">
          <i class="icon ph-bold ph-translate"></i>
          <span>{{ t('settings.languageSettings') }}</span>
        </el-text>
        <el-divider />

        <el-form-item :label="t('settings.selectLanguage')">
          <LanguageSwitcher />
        </el-form-item>

        <el-text type="info" class="setting-group-title setting-group-spacer">
          <i class="icon ph-bold ph-plugs"></i>
          <span>{{ t('settings.apiPlatformConfig') }}</span>
        </el-text>
        <el-divider />

        <el-form-item :label="t('settings.defaultApiPlatform')">
          <el-radio-group v-model="aiSettings.api_platform" class="platform-radio-group">
            <el-radio-button label="modelscope">{{ t('settings.modelscope') }}</el-radio-button>
            <el-radio-button label="bailian">{{ t('settings.dashscope') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <div v-if="aiSettings.api_platform === 'bailian'" class="bailian-settings">
          <el-form-item>
            <template #label>
              <span class="label-with-tooltip" @click.prevent>
                {{ t('settings.dashscopeApiKey') }}
                <el-tooltip
                  effect="dark"
                  :content="t('settings.dashscopeApiKeyTooltip')"
                  placement="top"
                >
                  <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
                </el-tooltip>
              </span>
            </template>
            <el-input
              v-model="aiSettings.bailian_api_key"
              :placeholder="t('settings.dashscopeApiKeyPlaceholder')"
              type="password"
              show-password
            />
          </el-form-item>

          </div>

        <el-text type="info" class="setting-group-title setting-group-spacer">
          <i class="icon ph-bold ph-robot"></i>
          <span>{{ t('settings.aiModelConfig') }}</span>
        </el-text>
        <el-divider />

        <div v-if="aiSettings.api_platform === 'modelscope'">
          <el-form-item>
            <template #label>
              <span class="label-with-tooltip" @click.prevent>
                {{ t('settings.chatModelModelscope') }}
                <el-tooltip
                  effect="dark"
                  :content="t('settings.chatModelTooltip')"
                  placement="top"
                >
                  <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
                </el-tooltip>
              </span>
            </template>
            <el-select v-model="aiSettings.chat_model" :placeholder="t('settings.pleaseSelect')" style="width: 100%;">
              <el-option :label="t('settings.qwen30BRecommended')" value="Qwen/Qwen3-30B-A3B-Instruct-2507" />
              <el-option :label="t('settings.qwen235B')" value="Qwen/Qwen3-235B-A22B-Instruct-2507" />
              <el-option :label="t('settings.deepseekV32')" value="deepseek-ai/Deepseek-V3.2-Exp" />
            </el-select>
            </el-form-item>

          <el-form-item>
            <template #label>
              <span class="label-with-tooltip" @click.prevent>
                {{ t('settings.vlModelModelscope') }}
                <el-tooltip
                  effect="dark"
                  :content="t('settings.vlModelTooltip')"
                  placement="top"
                >
                  <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
                </el-tooltip>
              </span>
            </template>
            <el-select v-model="aiSettings.vl_model" :placeholder="t('settings.pleaseSelect')" style="width: 100%;">
              <el-option :label="t('settings.qwenVL8BRecommended')" value="Qwen/Qwen3-VL-8B-Instruct" />
              <el-option :label="t('settings.qwenVL30B')" value="Qwen/Qwen3-VL-30B-A3B-Instruct" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <template #label>
              <span class="label-with-tooltip" @click.prevent>
                {{ t('settings.imageModelModelscope') }}
                <el-tooltip
                  effect="dark"
                  :content="t('settings.imageModelTooltip')"
                  placement="top"
                >
                  <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
                </el-tooltip>
              </span>
            </template>
            <el-select v-model="aiSettings.image_model" :placeholder="t('settings.pleaseSelect')" style="width: 100%;">
              <el-option :label="t('settings.fluxKreaRecommended')" value="black-forest-labs/FLUX.1-Krea-dev" />
              <el-option :label="t('settings.fluxDev')" value="MusePublic/489_ckpt_FLUX_1" />
              <el-option :label="t('settings.qwenImage')" value="Qwen/Qwen-image" />
            </el-select>
          </el-form-item>
        </div>

        <div v-if="aiSettings.api_platform === 'bailian'">
           <el-form-item>
            <template #label>
              <span class="label-with-tooltip" @click.prevent>
                {{ t('settings.chatModelDashscope') }}
                <el-tooltip
                  effect="dark"
                  :content="t('settings.chatModelTooltip')"
                  placement="top"
                >
                  <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
                </el-tooltip>
              </span>
            </template>
            <el-select v-model="aiSettings.ds_llm_id" :placeholder="t('settings.pleaseSelect')" style="width: 100%;">
              <el-option :label="t('settings.qwenPlusRecommended')" value="qwen-plus" />
              <el-option :label="t('settings.qwenMaxStrongest')" value="qwen3-max" />
              <el-option :label="t('settings.qwenFlashFastest')" value="qwen-flash" />
            </el-select>
          </el-form-item>

           <el-alert
            :title="t('settings.imageModelAutoSelect')"
            type="info"
            :description="t('settings.imageModelAutoSelectDesc')"
            show-icon
            :closable="false"
            style="margin-top: 10px;"
          />
        </div>

        <el-text type="info" class="setting-group-title setting-group-spacer">
          <i class="icon ph-bold ph-student"></i>
          <span>{{ t('settings.teachingContext') }}</span>
        </el-text>
        <el-divider />

        <el-form-item>
          <template #label>
            <span class="label-with-tooltip" @click.prevent>
              {{ t('settings.studentAge') }}
              <el-tooltip
                effect="dark"
                :content="t('settings.studentAgeTooltip')"
                placement="top"
              >
                <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-select v-model="aiSettings.age_range" :placeholder="t('settings.pleaseSelect')" style="width: 100%;">
            <el-option :label="t('settings.age6to8')" value="6-8岁" />
            <el-option :label="t('settings.age9to10')" value="9-10岁" />
            <el-option :label="t('settings.age11to12')" value="11-12岁" />
            <el-option :label="t('settings.age13to15')" value="13-15岁" />
            <el-option :label="t('settings.age16to18')" value="16-18岁" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-scrollbar>

  </el-drawer>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

import { useSettingsStore } from '../stores/settings';
import { storeToRefs } from 'pinia';

import { QuestionFilled } from '@element-plus/icons-vue';
import LanguageSwitcher from './LanguageSwitcher.vue';

const props = defineProps({
  isOpen: Boolean,
});

defineEmits(['close']);

const settingsStore = useSettingsStore();
const { aiSettings } = storeToRefs(settingsStore);

</script>

<style scoped>
/* 抽屉标题 */
.drawer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.drawer-header .icon {
  font-size: 1.2rem;
}

:deep(.el-drawer__body) {
  padding: 0;
}
.settings-form {
  padding: 0 20px 20px 20px;
}

/* 分组标题 */
.setting-group-title {
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
}
.setting-group-title .icon {
  font-size: 1.1rem;
}
.setting-group-spacer {
  margin-top: 20px;
}
.el-divider {
  margin: 12px 0 20px 0;
}

.label-with-tooltip {
  display: flex;
  align-items: center;
  gap: 4px; /* 标签文字和图标的间距 */
}

.help-icon {
  color: var(--el-text-color-secondary);
  cursor: help; /* 鼠标悬停时显示帮助光标 */
}

/* 百炼设置的特殊样式 */
.bailian-settings {
  background: #fdfdfd;
  border: 1px dashed var(--border-color);
  padding: 0 15px 10px 15px;
  border-radius: 8px;
  margin-top: -10px;
  margin-bottom: 10px;
}

/* (新增) 平台选择器美化 */
.platform-radio-group {
  display: flex;
  width: 100%;
}

:deep(.platform-radio-group .el-radio-button) {
  flex: 1; /* 平分宽度 */
}

:deep(.platform-radio-group .el-radio-button__inner) {
  width: 100%;
  text-align: center;
}
</style>