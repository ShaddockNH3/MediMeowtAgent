<template>
  <div class="q-container">
    <el-page-header @back="goBack" content="填写问诊单" class="mb-4" />
    
    <el-form 
      v-if="questions.length > 0" 
      ref="formRef" 
      :model="formData" 
      label-position="top"
    >
      <div v-for="(q, index) in questions" :key="q.question_id" class="question-item">
        
        <div class="q-title">
          <span class="index">{{ index + 1 }}.</span>
          <span class="label">{{ q.label }}</span>
          <span v-if="q.is_required === 'true' || q.is_required === '1' || q.is_required === true" class="required">*</span>
        </div>

        <el-form-item 
          v-if="isType(q.question_type, 'text')"
          :prop="q.question_id"
          :rules="getRules(q)"
        >
          <el-input 
            v-model="formData[q.question_id]" 
            :placeholder="q.placeholder || '请输入'" 
            type="textarea" 
            :rows="3"
          />
        </el-form-item>

        <el-form-item 
          v-if="isType(q.question_type, 'radio')"
          :prop="q.question_id"
          :rules="getRules(q)"
        >
          <el-radio-group v-model="formData[q.question_id]">
            <el-radio 
              v-for="opt in q.options" 
              :key="opt" 
              :label="opt"
            >
              {{ opt }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item 
          v-if="isType(q.question_type, 'checkbox')"
          :prop="q.question_id"
          :rules="getRules(q)"
        >
          <el-checkbox-group v-model="formData[q.question_id]">
            <el-checkbox 
              v-for="opt in q.options" 
              :key="opt" 
              :label="opt"
            >
              {{ opt }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item 
          v-if="isType(q.question_type, 'file')"
          :prop="q.question_id"
          :rules="getRules(q)"
        >
          <el-upload
            action="#"
            list-type="picture-card"
            :auto-upload="true"
            :limit="Number(q.max_files) || 3"
            :http-request="(opts) => customUpload(opts, q.question_id)"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div style="display:none">{{ formData[q.question_id] }}</div>
        </el-form-item>

      </div>

      <div class="footer-btn">
        <el-button type="primary" size="large" @click="submitForm" :loading="submitting">
          提交问卷
        </el-button>
      </div>
    </el-form>

    <el-empty v-else description="问卷数据加载中..." />
    
    <el-dialog v-model="dialogVisible">
      < img w-full :src="dialogImageUrl" alt="Preview Image" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getQuestionnaire, submitQuestionnaire, uploadFile } from '../api/index.js'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const submitting = ref(false)

const questions = ref([])
const formData = reactive({})
const deptId = route.params.deptId

const dialogImageUrl = ref('')
const dialogVisible = ref(false)

// --- 类型判断工具函数 (重点修复区域) ---
const isType = (serverType, localType) => {
  if (!serverType) return false
  const sType = serverType.toLowerCase()
  
  const typeMap = {
    // 扩大文本类型的匹配范围，确保 'string'/'input'/'text_area' 等都能被识别
    'text': ['text', 'string', 'textarea', 'input', 'text_area', 'long_text'],
    'radio': ['radio', 'single', 'choice', 'single_select'],
    'checkbox': ['checkbox', 'multiple', 'multi_select'],
    'file': ['file', 'image', 'upload', 'picture']
  }
  // 使用 .some(t => sType === t) 来进行严格匹配，或者保留 includes() 进行模糊匹配
  // 这里保留 includes() 来保证兼容性
  return typeMap[localType]?.some(t => sType.includes(t))
}

// --- 生成校验规则 ---
const getRules = (q) => {
  const required = q.is_required === true || q.is_required === 'true' || q.is_required === '1'
  if (!required) return []
  
  const label = q.label || '此项'
  
  // 数组类型的校验 (多选、文件)
  if (isType(q.question_type, 'checkbox') || isType(q.question_type, 'file')) {
    return [
      { required: true, message: `请选择 ${label}`, trigger: 'change' },
      { 
        validator: (rule, value, callback) => {
          if (value && value.length > 0) {
            callback()
          } else {
            callback(new Error(`请完成 ${label}`))
          }
        }, 
        trigger: 'change' 
      }
    ]
  }
  
  // 普通文本/单选校验
  return [{ required: true, message: `${label} 不能为空`, trigger: 'blur' }]
}

// --- 页面加载 ---
onMounted(async () => {
  if (!deptId) return
  try {
    const data = await getQuestionnaire(deptId)
    questions.value = data.questions || []
    
    // 初始化 formData
    questions.value.forEach(q => {
      if (isType(q.question_type, 'checkbox')) {
        formData[q.question_id] = []
      } else if (isType(q.question_type, 'file')) {
        formData[q.question_id] = [] 
      } else {
        // 确保所有文本/单选类型初始化为 string，保证 v-model 可用
        formData[q.question_id] = '' 
      }
    })
  } catch (error) {
    console.error('加载问卷失败', error)
  }
})

// --- 文件上传 ---
const customUpload = async (options, qId) => {
  try {
    const res = await uploadFile(options.file)
    const fileUrl = res.url || res.data?.url || 'http://mock-url.com/file.png' 
    
    // 将 URL 存入 formData
    if (Array.isArray(formData[qId])) {
      formData[qId].push(fileUrl)
    } else {
      formData[qId] = [fileUrl]
    }
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
    options.onError()
  }
}

const handlePreview = (uploadFile) => {
  dialogImageUrl.value = uploadFile.url
  dialogVisible.value = true
}

// --- 提交表单 ---
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          department_id: deptId,
          answers: formData 
        }
        
        await submitQuestionnaire(payload)
        ElMessage.success('提交成功！')
        router.push('/') 
      } catch (error) {
        console.error(error)
      } finally {
        submitting.value = false
      }
    } else {
      ElMessage.warning('请检查是否有必填项未完成')
      return false
    }
  })
}

const goBack = () => router.back()
</script>

<style scoped>
.q-container { max-width: 600px; margin: 20px auto; padding: 25px; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.05); border-radius: 8px;}
.question-item { margin-bottom: 30px; border-bottom: 1px dashed #eee; padding-bottom: 20px; }
.question-item:last-child { border-bottom: none; }
.q-title { margin-bottom: 12px; font-weight: 600; font-size: 16px; display: flex; align-items: center; }
.index { margin-right: 8px; color: #409EFF; font-weight: bold; }
.required { color: #F56C6C; margin-left: 4px; font-size: 18px; line-height: 1; }
.footer-btn { margin-top: 40px; text-align: center; }
.footer-btn .el-button { width: 100%; height: 45px; font-size: 16px; border-radius: 25px;}
.mb-4 { margin-bottom: 20px; }
</style>