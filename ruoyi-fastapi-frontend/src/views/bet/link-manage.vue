<template>
  <div class="app-container">
    <el-form :model="queryParams" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="链接名称">
        <el-input v-model="queryParams.linkName" placeholder="请输入链接名称" clearable @keyup.enter="getList" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="queryParams.status" clearable style="width: 180px">
          <el-option label="待投注" :value="0" />
          <el-option label="投注中" :value="1" />
          <el-option label="已截止" :value="2" />
          <el-option label="已结算" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="getList">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col v-if="!isAdmin" :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="openDialog = true">创建链接</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="tableData">
      <el-table-column label="链接名称" prop="linkName" min-width="180" />
      <el-table-column label="赔率" prop="odds" width="100" />
      <el-table-column label="参与人数" width="120">
        <template #default="scope">
          <span>{{ scope.row.confirmedUsers }} / {{ scope.row.maxUsers || '不限' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="过期时间" prop="expireAt" width="180">
        <template #default="scope">
          <span>{{ proxy.parseTime(scope.row.expireAt) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="scope">
          <el-tag :type="statusTypeMap[scope.row.status]">{{ statusLabelMap[scope.row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="链接Token" prop="linkToken" min-width="220" show-overflow-tooltip />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="scope">
          <template v-if="!isAdmin">
            <el-button link type="primary" @click="copyLink(scope.row)">复制链接</el-button>
            <el-button link type="success" v-if="scope.row.status !== 3" @click="confirmResult(scope.row, 1)">确认中奖</el-button>
            <el-button link type="danger" v-if="scope.row.status !== 3" @click="confirmResult(scope.row, 0)">确认未中</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <el-dialog v-model="openDialog" title="创建投注链接" width="560px" append-to-body>
      <el-form ref="dialogFormRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="链接名称" prop="linkName">
          <el-input v-model="form.linkName" />
        </el-form-item>
        <el-form-item label="投注说明">
          <el-input v-model="form.betDesc" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="赔率" prop="odds">
          <el-input-number v-model="form.odds" :min="0.01" :step="0.1" :precision="2" />
        </el-form-item>
        <el-form-item label="截止时间" prop="expireAt">
          <el-date-picker
            v-model="form.expireAt"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="人数上限">
          <el-input-number v-model="form.maxUsers" :min="1" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="BetLinkManage">
import { createBetLink, listBetLinks, confirmBetResult } from '@/api/distribution/bet'
import useUserStore from '@/store/modules/user'

const { proxy } = getCurrentInstance()
const userStore = useUserStore()

const showSearch = ref(true)
const loading = ref(false)
const openDialog = ref(false)
const submitting = ref(false)
const total = ref(0)
const tableData = ref([])
const dialogFormRef = ref()
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  linkName: '',
  status: undefined
})
const form = reactive({
  linkName: '',
  betDesc: '',
  odds: 2,
  expireAt: '',
  maxUsers: undefined
})

const rules = {
  linkName: [{ required: true, message: '请输入链接名称', trigger: 'blur' }],
  odds: [{ required: true, message: '请输入赔率', trigger: 'blur' }],
  expireAt: [{ required: true, message: '请选择截止时间', trigger: 'change' }]
}

const statusLabelMap = { 0: '待投注', 1: '投注中', 2: '已截止', 3: '已结算' }
const statusTypeMap = { 0: 'primary', 1: 'success', 2: 'warning', 3: 'info' }
const isAdmin = computed(() => userStore.roles.includes('admin'))

async function getList() {
  loading.value = true
  try {
    const res = await listBetLinks({ ...queryParams })
    tableData.value = res.rows || []
    total.value = res.total || 0
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载投注链接失败')
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  queryParams.pageNum = 1
  queryParams.pageSize = 10
  queryParams.linkName = ''
  queryParams.status = undefined
  getList()
}

function closeDialog() {
  openDialog.value = false
  Object.assign(form, {
    linkName: '',
    betDesc: '',
    odds: 2,
    expireAt: '',
    maxUsers: undefined
  })
  proxy.resetForm('dialogFormRef')
}

function submitForm() {
  dialogFormRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await createBetLink({ ...form })
      proxy.$modal.msgSuccess('创建成功')
      closeDialog()
      getList()
    } catch (error) {
      proxy.$modal.msgError(error?.message || '创建投注链接失败')
    } finally {
      submitting.value = false
    }
  })
}

async function confirmResult(row, isWin) {
  const actionText = isWin === 1 ? '确认中奖' : '确认未中'
  await proxy.$modal.confirm(`一旦确认不可更改，确定要${actionText}吗？`)
  try {
    await confirmBetResult(row.linkId, { isWin })
    proxy.$modal.msgSuccess(`${actionText}成功`)
    getList()
  } catch (error) {
    proxy.$modal.msgError(error?.message || `${actionText}失败`)
  }
}

async function copyLink(row) {
  const url = `${window.location.origin}/bet/link/${row.linkToken}`
  await navigator.clipboard.writeText(url)
  proxy.$modal.msgSuccess('链接已复制')
}

onMounted(getList)
</script>
