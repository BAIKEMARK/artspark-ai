import { ref, computed } from 'vue';

/**
 * 一个用于处理 Element Plus 'limit=1' 上传组件的 Composable。
 * 它会管理文件状态，并提供必要的事件处理器和 CSS 类。
 */
export function useUploadLimiter() {
  // 1. 内部持有的文件状态 (存储 file.raw)
  const file = ref(null);

  // 2. on-change 事件处理器
  // elFile 是 Element Plus 传递的原始文件对象
  const handleChange = (elFile) => {
    file.value = elFile.raw;
  };

  // 3. on-remove 事件处理器
  const handleRemove = () => {
    file.value = null;
  };

  // 4. 动态绑定的 CSS 类
  const uploadClass = computed(() => {
    return file.value ? 'upload-limit-reached' : '';
  });

  // 5. 导出所有需要的功能
  return {
    file,
    handleChange,
    handleRemove,
    uploadClass,
  };
}