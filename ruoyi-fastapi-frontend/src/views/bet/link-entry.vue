<template>
  <div class="bet-entry-page">
    <div class="entry-panel" v-loading="loading">
      <template v-if="detail">
        <div class="entry-head">
          <div>
            <h1>{{ detail.linkName }}</h1>
            <p>{{ detail.betDesc || '请确认本次投注信息，确认后不可更改。' }}</p>
          </div>
          <el-tag size="large" :type="statusType">{{ statusLabel }}</el-tag>
        </div>

        <div class="meta-grid">
          <div class="meta-item">
            <span>赔率</span>
            <strong>{{ detail.odds }}</strong>
          </div>
          <div class="meta-item">
            <span>截止时间</span>
            <strong>{{ proxy.parseTime(detail.expireAt) }}</strong>
          </div>
          <div class="meta-item">
            <span>参与人数</span>
            <strong>{{ detail.confirmedUsers }} / {{ detail.maxUsers || '不限' }}</strong>
          </div>
        </div>

        <el-alert
          v-if="detail.alreadyConfirmed"
          title="您已完成投注确认，请等待开奖结果。"
          type="success"
          :closable="false"
          show-icon
        />

        <el-alert
          v-else-if="[2,3].includes(detail.status)"
          title="此投注链接已截止或已结算，当前不可再参与。"
          type="warning"
          :closable="false"
          show-icon
        />

        <el-form v-else ref="formRef" :model="form" :rules="rules" label-width="100px" class="confirm-form">
          <el-form-item label="投注金额" prop="betAmount">
            <el-input-number v-model="form.betAmount" :min="1" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item>
            <el-button type="warning" :loading="submitting" @click="submitForm">确认投注</el-button>
          </el-form-item>
        </el-form>

        <div class="result-card" v-if="detail.alreadyConfirmed">
          <div class="result-item"><span>已投注金额</span><strong>{{ detail.betAmount }}</strong></div>
          <div class="result-item"><span>中奖金额</span><strong>{{ detail.winAmount ?? '--' }}</strong></div>
          <div class="result-item"><span>本轮收益</span><strong>{{ detail.roundProfit ?? '--' }}</strong></div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup name="BetLinkEntry">
import { openBetLink, confirmBet } from '@/api/distribution/bet'

const route = useRoute()
const { proxy } = getCurrentInstance()

const loading = ref(false)
const submitting = ref(false)
const detail = ref(null)
const formRef = ref()
const form = reactive({
  betAmount: 1
})
const rules = {
  betAmount: [{ required: true, message: '请输入投注金额', trigger: 'blur' }]
}

const statusLabel = computed(() => {
  const value = detail.value?.status
  return { 0: '待投注', 1: '投注中', 2: '已截止', 3: '已结算' }[value] || '未知状态'
})

const statusType = computed(() => {
  const value = detail.value?.status
  return { 0: 'primary', 1: 'success', 2: 'warning', 3: 'info' }[value] || 'info'
})

async function loadDetail() {
  loading.value = true
  try {
    const res = await openBetLink(route.params.token)
    detail.value = res.data
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载投注链接失败')
  } finally {
    loading.value = false
  }
}

function submitForm() {
  formRef.value.validate(async valid => {
    if (!valid) return
    await proxy.$modal.confirm(`投注金额 ¥${form.betAmount}，一旦确认不可更改，是否继续？`)
    submitting.value = true
    try {
      await confirmBet(route.params.token, { betAmount: form.betAmount })
      proxy.$modal.msgSuccess('投注确认成功')
      loadDetail()
    } catch (error) {
      proxy.$modal.msgError(error?.message || '投注确认失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(loadDetail)
</script>

<style scoped>
.bet-entry-page {
  min-height: 100vh;
  padding: 40px 16px;
  background: linear-gradient(180deg, #f7f5ef 0%, #eef4ff 100%);
}

.entry-panel {
  max-width: 860px;
  margin: 0 auto;
  background: #fff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.08);
}

.entry-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.entry-head h1 {
  margin: 0 0 8px;
  font-size: 28px;
}

.entry-head p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.meta-item,
.result-item {
  padding: 16px;
  border-radius: 16px;
  background: #f6f8fb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item span,
.result-item span {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.confirm-form {
  margin-top: 24px;
}

.result-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
  margin-top: 24px;
}
</style>
