import request from '@/utils/request'

export function getCommissionConfig() {
  return request({
    url: '/commission/config',
    method: 'get'
  })
}

export function saveCommissionConfig(data) {
  return request({
    url: '/commission/config',
    method: 'put',
    data
  })
}

export function resetCommissionConfig() {
  return request({
    url: '/commission/config/reset',
    method: 'delete'
  })
}

export function updateDefaultCommission(data) {
  return request({
    url: '/commission/default',
    method: 'put',
    data
  })
}
