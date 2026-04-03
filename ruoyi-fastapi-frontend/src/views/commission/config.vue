<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>提成梯度配置</span>
          <span class="card-tip">个性化配置优先于平台默认配置，利润提成按固定提成金额和分成比例结算。</span>
        </div>
      </template>

      <el-alert
        :title="sourceType === 'custom' ? '当前使用个性化提成配置' : '当前使用平台默认提成配置'"
        :type="sourceType === 'custom' ? 'success' : 'info'"
        :closable="false"
        show-icon
        class="mb16"
      />

      <el-table :data="form.items" border>
        <el-table-column label="利润下限">
          <template #default="scope">
            <el-input-number v-model="scope.row.profitMin" :min="0" :precision="2" />
          </template>
        </el-table-column>
        <el-table-column label="利润上限">
          <template #default="scope">
            <el-input-number v-model="scope.row.profitMax" :min="0" :precision="2" />
          </template>
        </el-table-column>
        <el-table-column label="固定提成金额">
          <template #default="scope">
            <el-input-number v-model="scope.row.commissionAmt" :min="0" :precision="2" />
          </template>
        </el-table-column>
        <el-table-column label="分成比例">
          <template #default="scope">
            <el-input-number v-model="scope.row.splitRatio" :min="0" :max="1" :step="0.1" :precision="4" />
          </template>
        </el-table-column>
        <el-table-column label="排序" width="120">
          <template #default="scope">
            <el-input-number v-model="scope.row.sortOrder" :min="1" :step="1" />
          </template>
        </el-table-column>
      </el-table>

      <el-card shadow="never" class="preview-card">
        <template #header>实时预览</template>
        <div class="preview-toolbar">
          <span>利润金额</span>
          <el-input-number v-model="previewProfit" :min="0" :precision="2" />
        </div>
        <el-alert
          v-if="previewResult"
          :title="`命中区间 ${previewResult.profitMin} - ${previewResult.profitMax}，代理提成 ${previewCommission}，上级分成 ${previewParentShare}`"
          type="success"
          :closable="false"
          show-icon
        />
        <el-empty v-else description="当前利润未命中任何提成区间" />
      </el-card>

      <div class="toolbar">
        <el-button type="primary" plain icon="Plus" @click="addRow">新增区间</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSave">保存配置</el-button>
        <el-button icon="Refresh" :loading="loading" @click="loadData">重新加载</el-button>
        <el-button type="warning" plain @click="handleReset">恢复平台默认</el-button>
        <el-button v-if="isAdmin" type="danger" plain @click="handleSaveDefault">保存为平台默认</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup name="CommissionConfig">
import { getCommissionConfig, resetCommissionConfig, saveCommissionConfig, updateDefaultCommission } from '@/api/distribution/commission'
import useUserStore from '@/store/modules/user'

const { proxy } = getCurrentInstance()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const sourceType = ref('default')
const previewProfit = ref(0)
const form = reactive({
  items: []
})

const isAdmin = computed(() => userStore.roles.includes('admin'))
const previewResult = computed(() =>
  [...form.items]
    .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
    .find((item) => previewProfit.value >= Number(item.profitMin || 0) && previewProfit.value <= Number(item.profitMax || 0))
)
const previewCommission = computed(() => {
  if (!previewResult.value) return 0
  return (Number(previewResult.value.commissionAmt || 0) * Number(previewResult.value.splitRatio || 0)).toFixed(2)
})
const previewParentShare = computed(() => {
  if (!previewResult.value) return 0
  return (Number(previewResult.value.commissionAmt || 0) * (1 - Number(previewResult.value.splitRatio || 0))).toFixed(2)
})

function addRow() {
  form.items.push({
    profitMin: 0,
    profitMax: 0,
    commissionAmt: 0,
    splitRatio: 0.5,
    sortOrder: form.items.length + 1
  })
}

async function loadData() {
  loading.value = true
  try {
    const res = await getCommissionConfig()
    sourceType.value = res.data?.sourceType || 'default'
    form.items = (res.data?.items || []).map(item => ({ ...item }))
    if (!form.items.length) {
      addRow()
    }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  submitting.value = true
  try {
    await saveCommissionConfig({ items: form.items })
    proxy.$modal.msgSuccess('保存成功')
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleReset() {
  await proxy.$modal.confirm('确认恢复为平台默认提成配置吗？')
  await resetCommissionConfig()
  proxy.$modal.msgSuccess('已恢复平台默认配置')
  loadData()
}

async function handleSaveDefault() {
  await proxy.$modal.confirm('确认覆盖平台默认提成配置吗？')
  await updateDefaultCommission({ items: form.items })
  proxy.$modal.msgSuccess('平台默认配置已更新')
  loadData()
}

onMounted(loadData)
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

.toolbar {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.preview-card {
  margin-top: 16px;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.mb16 {
  margin-bottom: 16px;
}
</style>
