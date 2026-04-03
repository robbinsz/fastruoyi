<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>分配总代理</span>
          <span class="card-tip">输入已有用户编号并绑定代理编码，分配后该用户下次登录即可获得总代理菜单。</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 720px">
        <el-form-item label="用户编号" prop="userId">
          <el-input-number v-model="form.userId" :min="1" controls-position="right" />
        </el-form-item>
        <el-form-item label="代理商编码" prop="agentCode">
          <el-input v-model="form.agentCode" placeholder="例如 L1-20260403-001" />
        </el-form-item>
        <el-form-item label="投注提成率" prop="betCommissionRate">
          <el-input-number v-model="form.betCommissionRate" :min="0" :max="1" :step="0.001" :precision="4" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="4" placeholder="可选备注" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">分配为总代理</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup name="AssignAgent">
import { assignL1Agent } from '@/api/distribution/admin'

const { proxy } = getCurrentInstance()

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  userId: undefined,
  agentCode: '',
  betCommissionRate: 0.025,
  remark: ''
})

const rules = {
  userId: [{ required: true, message: '请输入用户编号', trigger: 'blur' }],
  agentCode: [{ required: true, message: '请输入代理商编码', trigger: 'blur' }]
}

function resetForm() {
  form.userId = undefined
  form.agentCode = ''
  form.betCommissionRate = 0.025
  form.remark = ''
  proxy.resetForm('formRef')
}

function submitForm() {
  formRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await assignL1Agent({ ...form })
      proxy.$modal.msgSuccess('分配成功')
      resetForm()
    } catch (error) {
      proxy.$modal.msgError(error?.message || '分配总代理失败')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.card-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
