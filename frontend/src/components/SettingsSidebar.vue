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
        <span>设置</span>
      </div>
    </template>

    <el-scrollbar>
      <el-form label-position="top" class="settings-form">

        <el-text type="info" class="setting-group-title">
          <i class="icon ph-bold ph-robot"></i>
          <span>AI 模型配置</span>
        </el-text>
        <el-divider />

        <el-form-item>
          <template #label>
            <span class="label-with-tooltip" @click.prevent>
              对话模型:
              <el-tooltip
                effect="dark"
                content="用于“艺术知识问答”和“创意灵感生成”。"
                placement="top"
              >
                <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-select v-model="aiSettings.chat_model" placeholder="请选择" style="width: 100%;">
            <el-option label="Qwen3-30B (推荐)" value="Qwen/Qwen3-30B-A3B-Instruct-2507" />
            <el-option label="Qwen/Qwen3-32B" value="Qwen/Qwen3-32B" />
            <el-option label="Qwen3-235B" value="Qwen/Qwen3-235B-A22B-Instruct-2507" />
            <el-option label="Deepseek-V3.2" value="deepseek-ai/DeepSeek-V3.2-Exp" />
          </el-select>
          </el-form-item>

        <el-form-item>
          <template #label>
            <span class="label-with-tooltip" @click.prevent>
              识图模型:
              <el-tooltip
                effect="dark"
                content="用于所有需要“上传图片”进行分析的工具，如“AI智能上色”。"
                placement="top"
              >
                <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-select v-model="aiSettings.vl_model" placeholder="请选择" style="width: 100%;">
            <el-option label="Qwen-VL-8B (推荐)" value="Qwen/Qwen3-VL-8B-Instruct" />
            <el-option label="Qwen3-VL-30B" value="Qwen/Qwen3-VL-30B-A3B-Instruct" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <template #label>
            <span class="label-with-tooltip" @click.prevent>
              绘图模型:
              <el-tooltip
                effect="dark"
                content="用于所有“生成图片”的工具，如“创意风格工坊”。"
                placement="top"
              >
                <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-select v-model="aiSettings.image_model" placeholder="请选择" style="width: 100%;">
            <el-option label="FLUX.1-Krea (推荐)" value="black-forest-labs/FLUX.1-Krea-dev" />
            <el-option label="FLUX.1-dev" value="MusePublic/489_ckpt_FLUX_1" />
            <el-option label="Qwen-image" value="Qwen/Qwen-Image" />
          </el-select>
        </el-form-item>

        <el-text type="info" class="setting-group-title setting-group-spacer">
          <i class="icon ph-bold ph-student"></i>
          <span>教学情景</span>
        </el-text>
        <el-divider />

        <el-form-item>
          <template #label>
            <span class="label-with-tooltip" @click.prevent>
              学生年龄:
              <el-tooltip
                effect="dark"
                content="AI将根据所选年龄调整其回答的复杂度和语气。"
                placement="top"
              >
                <el-icon :size="14" class="help-icon" ><QuestionFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-select v-model="aiSettings.age_range" placeholder="请选择" style="width: 100%;">
            <el-option label="6-8岁 (低年级)" value="6-8岁" />
            <el-option label="9-10岁 (中年级)" value="9-10岁" />
            <el-option label="11-12岁 (高年级)" value="11-12岁" />
            <el-option label="13-16岁 (初中)" value="13-16岁" />
            <el-option label="17-18岁 (高中)" value="17-18岁" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-scrollbar>

  </el-drawer>
</template>

<script setup>
import { useSettingsStore } from '../stores/settings';
import { storeToRefs } from 'pinia';

import { QuestionFilled } from '@element-plus/icons-vue';

const props = defineProps({
  isOpen: Boolean,
});

defineEmits(['close']);

const settingsStore = useSettingsStore();
const { aiSettings } = storeToRefs(settingsStore);

</script>

<style scoped>
/* 抽屉标题 (保持不变) */
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

/* 分组标题 (保持不变) */
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

/* 关键修改：添加 label 样式，移除旧的 description 样式 */
.label-with-tooltip {
  display: flex;
  align-items: center;
  gap: 4px; /* 标签文字和图标的间距 */
}

.help-icon {
  color: var(--el-text-color-secondary); /* 柔和的图标颜色 */
  cursor: help; /* 鼠标悬停时显示帮助光标 */
}
</style>