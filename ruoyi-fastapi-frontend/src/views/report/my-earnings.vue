<template>
  <div class="app-container">
    <el-form :inline="true">
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="loadData">查询</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="16" class="mb16">
      <el-col :xs="24" :sm="8"><el-card shadow="hover"><el-statistic title="总投注额" :value="summary.totalBetAmount || 0" /></el-card></el-col>
      <el-col :xs="24" :sm="8"><el-card shadow="hover"><el-statistic title="总中奖额" :value="summary.totalWinAmount || 0" /></el-card></el-col>
      <el-col :xs="24" :sm="8"><el-card shadow="hover"><el-statistic title="总收益" :value="summary.totalProfit || 0" /></el-card></el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>收益记录</template>
      <el-table v-loading="loading" :data="rows">
        <el-table-column label="链接名称" prop="linkName" min-width="180" />
        <el-table-column label="投注金额" prop="betAmount" width="120" />
        <el-table-column label="中奖金额" prop="winAmount" width="120" />
        <el-table-column label="本轮收益" prop="profit" width="120" />
        <el-table-column label="确认时间" width="180">
          <template #default="scope">{{ proxy.parseTime(scope.row.confirmTime) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="MyEarnings">
import { getMyEarnings } from '@/api/distribution/report'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const dateRange = ref([])
const rows = ref([])
const summary = reactive({})

async function loadData() {
  loading.value = true
  try {
    const res = await getMyEarnings({
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    })
    Object.assign(summary, res.data?.summary || {})
    rows.value = res.data?.rows || []
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载我的收益失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
