<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>创建下级代理</span>
          <span class="card-tip">仅在已获得超管授权时可创建直属下级代理。默认新代理仍然不能继续创建次级。</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" style="max-width: 760px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="登录账号" prop="userName">
              <el-input v-model="form.userName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户昵称" prop="nickName">
              <el-input v-model="form.nickName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="代理编码" prop="agentCode">
              <el-input v-model="form.agentCode" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="登录密码" prop="password">
              <el-input v-model="form.password" type="password" show-password />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phonenumber" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="投注提成率">
              <el-input-number v-model="form.betCommissionRate" :min="0" :max="1" :step="0.001" :precision="4" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">创建下级代理</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup name="CreateSubAgent">
import { createSubAgent } from '@/api/distribution/agent'

const { proxy } = getCurrentInstance()

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  userName: '',
  nickName: '',
  agentCode: '',
  password: '',
  phonenumber: '',
  email: '',
  betCommissionRate: 0.025,
  remark: ''
})

const rules = {
  userName: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  nickName: [{ required: true, message: '请输入用户昵称', trigger: 'blur' }],
  agentCode: [{ required: true, message: '请输入代理编码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }]
}

function resetForm() {
  Object.assign(form, {
    userName: '',
    nickName: '',
    agentCode: '',
    password: '',
    phonenumber: '',
    email: '',
    betCommissionRate: 0.025,
    remark: ''
  })
  proxy.resetForm('formRef')
}

function submitForm() {
  formRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await createSubAgent({ ...form })
      proxy.$modal.msgSuccess('创建成功')
      resetForm()
    } catch (error) {
      proxy.$modal.msgError(error?.message || '创建下级代理失败')
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
