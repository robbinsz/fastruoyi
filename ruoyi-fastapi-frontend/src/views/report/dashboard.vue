<template>
  <div class="app-container">
    <el-form :model="queryParams" :inline="true" label-width="68px">
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
        <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        <el-button type="warning" plain icon="Download" @click="handleExport">导出明细</el-button>
      </el-form-item>
      <el-form-item label="趋势粒度">
        <el-radio-group v-model="queryParams.period" @change="loadTrend">
          <el-radio-button value="day">按日</el-radio-button>
          <el-radio-button value="week">按周</el-radio-button>
          <el-radio-button value="month">按月</el-radio-button>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <el-row :gutter="16" class="summary-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="4.8">
        <el-card shadow="hover"><el-statistic title="总投注额" :value="summary.totalBetAmount || 0" /></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="4.8">
        <el-card shadow="hover"><el-statistic title="总中奖额" :value="summary.totalWinAmount || 0" /></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="4.8">
        <el-card shadow="hover"><el-statistic title="投注提成" :value="summary.totalBetCommission || 0" /></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="4.8">
        <el-card shadow="hover"><el-statistic title="利润提成" :value="summary.totalProfitCommission || 0" /></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="4.8">
        <el-card shadow="hover"><el-statistic title="总收益" :value="summary.totalCommission || 0" /></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="board-row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never">
          <template #header>收益趋势</template>
          <div ref="trendChartRef" style="height: 320px;" />
        </el-card>
      </el-col>
      <el-col v-if="showSubAgentBoard" :xs="24" :lg="8">
        <el-card shadow="never">
          <template #header>直属下级代理汇总</template>
          <el-empty v-if="!subAgentRows.length" description="暂无直属代理数据" />
          <el-table v-else :data="subAgentRows" max-height="320">
            <el-table-column label="代理编码" prop="agentCode" min-width="140" />
            <el-table-column label="账号" prop="userName" min-width="120" />
            <el-table-column label="总收益" prop="totalCommission" min-width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>收益明细</template>
      <el-table v-loading="loading" :data="detailRows">
        <el-table-column label="用户账号" prop="userName" min-width="140" />
        <el-table-column label="用户昵称" prop="nickName" min-width="140" />
        <el-table-column label="链接名称" prop="linkName" min-width="180" />
        <el-table-column label="投注金额" prop="betAmount" width="120" />
        <el-table-column label="中奖金额" prop="winAmount" width="120" />
        <el-table-column label="用户收益" prop="profit" width="120" />
        <el-table-column label="确认时间" width="180">
          <template #default="scope">{{ proxy.parseTime(scope.row.confirmTime) }}</template>
        </el-table-column>
      </el-table>
      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="loadDetail"
      />
    </el-card>
  </div>
</template>

<script setup name="ReportDashboard">
import { getDashboard, listEarnings, getEarningsTrend, listSubAgentsSummary, exportEarnings } from '@/api/distribution/report'
import * as echarts from 'echarts'
import useUserStore from '@/store/modules/user'

const { proxy } = getCurrentInstance()
const userStore = useUserStore()

const loading = ref(false)
const dateRange = ref([])
const total = ref(0)
const trendChartRef = ref(null)
let trendChartInstance
const summary = reactive({})
const trendRows = ref([])
const subAgentRows = ref([])
const detailRows = ref([])
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  period: 'day',
  startDate: undefined,
  endDate: undefined
})
const showSubAgentBoard = computed(() => !userStore.roles.includes('agent_l4') && !userStore.roles.includes('customer'))

function syncDateRange() {
  queryParams.startDate = dateRange.value?.[0]
  queryParams.endDate = dateRange.value?.[1]
}

function renderTrendChart() {
  if (!trendChartRef.value) return
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChartRef.value, 'macarons')
  }
  trendChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总投注额', '总收益'] },
    grid: { left: 36, right: 24, top: 36, bottom: 28, containLabel: true },
    xAxis: {
      type: 'category',
      data: trendRows.value.map((item) => item.statDate)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '总投注额',
        type: 'line',
        smooth: true,
        data: trendRows.value.map((item) => item.totalBetAmount)
      },
      {
        name: '总收益',
        type: 'line',
        smooth: true,
        data: trendRows.value.map((item) => item.totalCommission)
      }
    ]
  })
}

async function loadSummary() {
  const res = await getDashboard({ ...queryParams })
  Object.assign(summary, res.data || {})
}

async function loadTrend() {
  const res = await getEarningsTrend({ ...queryParams })
  trendRows.value = res.data || []
  nextTick(renderTrendChart)
}

async function loadSubAgents() {
  if (!showSubAgentBoard.value) {
    subAgentRows.value = []
    return
  }
  const res = await listSubAgentsSummary({ ...queryParams })
  subAgentRows.value = res.data || []
}

async function loadDetail() {
  loading.value = true
  try {
    const res = await listEarnings({ ...queryParams })
    detailRows.value = res.rows || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

async function handleQuery() {
  syncDateRange()
  queryParams.pageNum = 1
  try {
    await Promise.all([loadSummary(), loadTrend(), loadSubAgents(), loadDetail()])
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载收益看板失败')
  }
}

function resetQuery() {
  dateRange.value = []
  queryParams.pageNum = 1
  queryParams.pageSize = 10
  queryParams.startDate = undefined
  queryParams.endDate = undefined
  handleQuery()
}

function handleExport() {
  syncDateRange()
  exportEarnings({ ...queryParams }).catch((error) => {
    proxy.$modal.msgError(error?.message || '导出失败')
  })
}

onMounted(() => {
  handleQuery()
  window.addEventListener('resize', renderTrendChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderTrendChart)
  trendChartInstance?.dispose()
  trendChartInstance = null
})
</script>

<style scoped>
.summary-row,
.board-row {
  margin-bottom: 16px;
}
</style>
