<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>我的投注记录</span>
          <el-button type="primary" plain icon="Refresh" @click="getList">刷新</el-button>
        </div>
      </template>
      <el-table v-loading="loading" :data="tableData">
        <el-table-column label="链接名称" prop="linkName" min-width="180" />
        <el-table-column label="投注金额" prop="betAmount" width="120" />
        <el-table-column label="赔率" prop="odds" width="100" />
        <el-table-column label="中奖金额" prop="winAmount" width="120" />
        <el-table-column label="本轮收益" prop="roundProfit" width="120" />
        <el-table-column label="是否中奖" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.isWin === 1" type="success">已中</el-tag>
            <el-tag v-else-if="scope.row.isWin === 0" type="danger">未中</el-tag>
            <el-tag v-else type="info">待结算</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="确认时间" width="180">
          <template #default="scope">
            <span>{{ proxy.parseTime(scope.row.confirmTime) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="MyBets">
import { listMyBets } from '@/api/distribution/bet'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const tableData = ref([])

async function getList() {
  loading.value = true
  try {
    const res = await listMyBets()
    tableData.value = res.data || []
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载我的投注失败')
  } finally {
    loading.value = false
  }
}

onMounted(getList)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
