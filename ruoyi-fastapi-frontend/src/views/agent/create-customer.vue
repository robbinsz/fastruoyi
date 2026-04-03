<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>创建直属客户</span>
          <span class="card-tip">客户会自动归属到当前代理名下，不允许越权指定其它代理。</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="max-width: 760px">
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
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">创建直属客户</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup name="CreateCustomer">
import { createCustomer } from '@/api/distribution/agent'

const { proxy } = getCurrentInstance()

const formRef = ref()
const submitting = ref(false)
const form = reactive({
  userName: '',
  nickName: '',
  password: '',
  phonenumber: '',
  email: '',
  remark: ''
})

const rules = {
  userName: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  nickName: [{ required: true, message: '请输入用户昵称', trigger: 'blur' }],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }]
}

function resetForm() {
  Object.assign(form, {
    userName: '',
    nickName: '',
    password: '',
    phonenumber: '',
    email: '',
    remark: ''
  })
  proxy.resetForm('formRef')
}

function submitForm() {
  formRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await createCustomer({ ...form })
      proxy.$modal.msgSuccess('创建成功')
      resetForm()
    } catch (error) {
      proxy.$modal.msgError(error?.message || '创建直属客户失败')
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
