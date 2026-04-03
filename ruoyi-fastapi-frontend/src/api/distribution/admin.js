import request from '@/utils/request'

export function assignL1Agent(data) {
  return request({
    url: '/admin/assign-l1-agent',
    method: 'post',
    data
  })
}

export function grantSubAgent(agentId) {
  return request({
    url: `/admin/grant-sub-agent/${agentId}`,
    method: 'put'
  })
}

export function revokeSubAgent(agentId) {
  return request({
    url: `/admin/revoke-sub-agent/${agentId}`,
    method: 'put'
  })
}

export function getAgentTree() {
  return request({
    url: '/admin/agent-tree',
    method: 'get'
  })
}

export function getAgentPermission(agentId) {
  return request({
    url: `/admin/agent-permission/${agentId}`,
    method: 'get'
  })
}

export function getAgentDetail(agentId) {
  return request({
    url: `/admin/agent-detail/${agentId}`,
    method: 'get'
  })
}

export function updateAgentStatus(agentId, data) {
  return request({
    url: `/admin/agent/${agentId}/status`,
    method: 'put',
    data
  })
}

export function updateAgentCommissionRate(agentId, data) {
  return request({
    url: `/admin/agent/${agentId}/commission-rate`,
    method: 'put',
    data
  })
}
