<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>代理树管理</span>
          <el-button type="primary" plain icon="Refresh" @click="loadTree">刷新</el-button>
        </div>
      </template>
      <el-empty v-if="!treeData.length" description="暂无代理数据" />
      <el-tree
        v-else
        :data="treeData"
        node-key="agentId"
        default-expand-all
        :props="{ children: 'children', label: 'agentCode' }"
      >
        <template #default="{ data }">
          <div class="tree-node">
            <div class="node-main">
              <span class="node-code">{{ data.agentCode }}</span>
              <el-tag size="small" type="info">L{{ data.agentLevel }}</el-tag>
              <span class="node-user">{{ data.nickName || data.agentName }} / {{ data.userName }}</span>
              <el-tag size="small" :type="data.canCreateSub ? 'success' : 'warning'">
                {{ data.canCreateSub ? '允许创建次级' : '仅可创建客户' }}
              </el-tag>
            </div>
            <div class="node-actions">
              <el-button size="small" plain @click.stop="handleDetail(data)">
                详情
              </el-button>
              <el-button size="small" plain @click.stop="handleEditRate(data)">
                提成系数
              </el-button>
              <el-button
                size="small"
                type="success"
                plain
                v-if="!data.canCreateSub && data.agentLevel < 4"
                @click.stop="handleGrant(data)"
              >
                授权
              </el-button>
              <el-button
                size="small"
                type="danger"
                plain
                v-if="data.canCreateSub"
                @click.stop="handleRevoke(data)"
              >
                撤销
              </el-button>
              <el-button
                size="small"
                :type="data.status === '0' ? 'danger' : 'primary'"
                plain
                @click.stop="handleToggleStatus(data)"
              >
                {{ data.status === '0' ? '停用' : '启用' }}
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>
  </div>
</template>

<script setup name="AgentTree">
import {
  getAgentDetail,
  getAgentTree,
  grantSubAgent,
  revokeSubAgent,
  updateAgentCommissionRate,
  updateAgentStatus
} from '@/api/distribution/admin'

const { proxy } = getCurrentInstance()

const treeData = ref([])

async function loadTree() {
  try {
    const res = await getAgentTree()
    treeData.value = res.data || []
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载代理树失败')
  }
}

async function handleGrant(row) {
  try {
    await proxy.$modal.confirm(`确认授权代理 ${row.agentCode} 创建次级代理？`)
    await grantSubAgent(row.agentId)
    proxy.$modal.msgSuccess('授权成功')
    loadTree()
  } catch (error) {
    if (error !== 'cancel') {
      proxy.$modal.msgError(error?.message || '授权失败')
    }
  }
}

async function handleRevoke(row) {
  try {
    await proxy.$modal.confirm(`确认撤销代理 ${row.agentCode} 创建次级代理权限？`)
    await revokeSubAgent(row.agentId)
    proxy.$modal.msgSuccess('撤销成功')
    loadTree()
  } catch (error) {
    if (error !== 'cancel') {
      proxy.$modal.msgError(error?.message || '撤销失败')
    }
  }
}

async function handleDetail(row) {
  try {
    const res = await getAgentDetail(row.agentId)
    const detail = res.data || {}
    await proxy.$modal.alert(
      [
        `代理编码：${detail.agentCode || '-'}`,
        `账号：${detail.userName || '-'}`,
        `昵称：${detail.nickName || '-'}`,
        `层级：L${detail.agentLevel || '-'}`,
        `投注提成系数：${detail.betCommissionRate ?? '-'}`,
        `状态：${detail.status === '0' ? '正常' : '停用'}`
      ].join('\n')
    )
  } catch (error) {
    proxy.$modal.msgError(error?.message || '获取代理详情失败')
  }
}

async function handleEditRate(row) {
  try {
    const { value } = await proxy.$modal.prompt(`请输入代理 ${row.agentCode} 的投注提成系数`)
    await updateAgentCommissionRate(row.agentId, { betCommissionRate: Number(value) })
    proxy.$modal.msgSuccess('提成系数更新成功')
    loadTree()
  } catch (error) {
    if (error !== 'cancel') {
      proxy.$modal.msgError(error?.message || '提成系数更新失败')
    }
  }
}

async function handleToggleStatus(row) {
  const nextStatus = row.status === '0' ? '1' : '0'
  const actionText = nextStatus === '1' ? '停用' : '启用'
  try {
    await proxy.$modal.confirm(`确认${actionText}代理 ${row.agentCode}？`)
    await updateAgentStatus(row.agentId, { status: nextStatus })
    proxy.$modal.msgSuccess(`${actionText}成功`)
    loadTree()
  } catch (error) {
    if (error !== 'cancel') {
      proxy.$modal.msgError(error?.message || `${actionText}失败`)
    }
  }
}

onMounted(loadTree)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tree-node {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 0;
}

.node-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.node-code {
  font-weight: 600;
}

.node-user {
  color: var(--el-text-color-secondary);
}
</style>
