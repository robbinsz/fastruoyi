<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="直属代理" name="agents" />
      <el-tab-pane label="直属客户" name="customers" />
    </el-tabs>

    <el-form :model="queryParams" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="账号">
        <el-input v-model="queryParams.userName" placeholder="请输入账号" clearable @keyup.enter="getList" />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="queryParams.nickName" placeholder="请输入昵称" clearable @keyup.enter="getList" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="queryParams.phonenumber" placeholder="请输入手机号" clearable @keyup.enter="getList" />
      </el-form-item>
      <el-form-item v-if="activeTab === 'agents'" label="代理编码">
        <el-input v-model="queryParams.agentCode" placeholder="请输入代理编码" clearable @keyup.enter="getList" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="getList">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="tableData">
      <el-table-column label="用户编号" prop="userId" width="100" />
      <el-table-column label="账号" prop="userName" min-width="140" />
      <el-table-column label="昵称" prop="nickName" min-width="140" />
      <el-table-column label="手机号" prop="phonenumber" width="140" />
      <el-table-column v-if="activeTab === 'agents'" label="代理编码" prop="agentCode" min-width="160" />
      <el-table-column v-if="activeTab === 'agents'" label="层级" width="90">
        <template #default="scope">
          <el-tag size="small">L{{ scope.row.agentLevel }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="activeTab === 'agents'" label="次级权限" width="120">
        <template #default="scope">
          <el-tag size="small" :type="scope.row.canCreateSubAgent ? 'success' : 'warning'">
            {{ scope.row.canCreateSubAgent ? '已授权' : '未授权' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ proxy.parseTime(scope.row.createTime) }}</span>
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
  </div>
</template>

<script setup name="AgentList">
import { listDirectAgents, listDirectCustomers } from '@/api/distribution/agent'

const { proxy } = getCurrentInstance()

const activeTab = ref('agents')
const showSearch = ref(true)
const loading = ref(false)
const total = ref(0)
const tableData = ref([])
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  userName: '',
  nickName: '',
  phonenumber: '',
  agentCode: ''
})

async function getList() {
  loading.value = true
  try {
    const api = activeTab.value === 'agents' ? listDirectAgents : listDirectCustomers
    const res = await api({ ...queryParams })
    tableData.value = res.rows || []
    total.value = res.total || 0
  } catch (error) {
    proxy.$modal.msgError(error?.message || '加载代理列表失败')
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  queryParams.pageNum = 1
  queryParams.pageSize = 10
  queryParams.userName = ''
  queryParams.nickName = ''
  queryParams.phonenumber = ''
  queryParams.agentCode = ''
  getList()
}

function handleTabChange() {
  queryParams.pageNum = 1
  getList()
}

onMounted(getList)
</script>
