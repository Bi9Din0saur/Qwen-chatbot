<template>
  <div class="image-upload">
    <div class="upload-tabs">
      <button :class="['tab-button', { active: activeTab === 'file' }]" @click="activeTab = 'file'">
        上传图片
      </button>
      <button :class="['tab-button', { active: activeTab === 'url' }]" @click="activeTab = 'url'">
        图片URL
      </button>
    </div>

    <div v-if="activeTab === 'file'" class="file-upload">
      <div
        class="drop-zone"
        @drop="handleDrop"
        @dragover.prevent
        @dragenter.prevent
        :class="{ 'drag-over': isDragOver }"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          class="file-input"
        />
        <div class="drop-content">
          <div class="upload-icon">📁</div>
          <p>拖拽图片到此处或点击选择</p>
          <p class="file-types">支持 JPG, PNG, GIF, WebP</p>
        </div>
      </div>
    </div>

    <div v-else class="url-input">
      <div class="input-group">
        <input
          v-model="imageUrl"
          type="url"
          placeholder="请输入图片URL"
          class="url-input-field"
          @keyup.enter="handleUrlSubmit"
        />
        <button @click="handleUrlSubmit" class="submit-button">确定</button>
      </div>
    </div>

    <div v-if="previewImage" class="image-preview">
      <img :src="previewImage" alt="预览" class="preview-img" />
      <button @click="removeImage" class="remove-button">✕</button>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: string | File
}

interface Emits {
  (e: 'update:modelValue', value: string | File | undefined): void
  (e: 'image-selected'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const emitImageSelected = () => {
  emit('image-selected')
}

const activeTab = ref<'file' | 'url'>('file')
const imageUrl = ref('')
const selectedFile = ref<File | null>(null)
const isDragOver = ref(false)
const error = ref('')
const fileInput = ref<HTMLInputElement>()

const previewImage = computed(() => {
  if (selectedFile.value) {
    return URL.createObjectURL(selectedFile.value)
  }
  if (imageUrl.value) {
    return imageUrl.value
  }
  return ''
})

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    if (validateFile(file)) {
      selectedFile.value = file
      imageUrl.value = ''
      error.value = ''
      emit('update:modelValue', file)
      emitImageSelected()
    }
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (validateFile(file)) {
      selectedFile.value = file
      imageUrl.value = ''
      error.value = ''
      emit('update:modelValue', file)
      emitImageSelected()
    }
  }
}

const handleUrlSubmit = () => {
  if (!imageUrl.value.trim()) {
    error.value = '请输入图片URL'
    return
  }

  if (!isValidUrl(imageUrl.value)) {
    error.value = '请输入有效的图片URL'
    return
  }

  selectedFile.value = null
  error.value = ''
  emit('update:modelValue', imageUrl.value)
  emitImageSelected()
}

const validateFile = (file: File): boolean => {
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return false
  }

  if (file.size > 10 * 1024 * 1024) {
    // 10MB
    error.value = '图片大小不能超过10MB'
    return false
  }

  return true
}

const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

const removeImage = () => {
  selectedFile.value = null
  imageUrl.value = ''
  error.value = ''
  emit('update:modelValue', undefined)

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 监听外部值变化
const updateFromProps = () => {
  if (props.modelValue instanceof File) {
    selectedFile.value = props.modelValue
    imageUrl.value = ''
    activeTab.value = 'file'
  } else if (typeof props.modelValue === 'string') {
    imageUrl.value = props.modelValue
    selectedFile.value = null
    activeTab.value = 'url'
  }
}

// 初始化时同步外部值
updateFromProps()
</script>

<style scoped>
.image-upload {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.upload-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab-button {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button.active {
  background: #007bff;
  color: white;
}

.tab-button:hover:not(.active) {
  background: #e9ecef;
}

.file-upload {
  padding: 20px;
}

.drop-zone {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: #007bff;
  background: #f8f9ff;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.drop-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.file-types {
  color: #666;
  font-size: 14px;
  margin-top: 8px;
}

.url-input {
  padding: 20px;
}

.input-group {
  display: flex;
  gap: 8px;
}

.url-input-field {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  outline: none;
}

.url-input-field:focus {
  border-color: #007bff;
}

.submit-button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.submit-button:hover {
  background: #0056b3;
}

.image-preview {
  position: relative;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.preview-img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  display: block;
  margin: 0 auto;
}

.remove-button {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.remove-button:hover {
  background: rgba(0, 0, 0, 0.9);
}

.error-message {
  padding: 12px 20px;
  background: #f8d7da;
  color: #721c24;
  border-top: 1px solid #f5c6cb;
  font-size: 14px;
}
</style>
