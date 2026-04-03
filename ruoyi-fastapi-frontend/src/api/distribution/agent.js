import request from '@/utils/request'

export function listDirectAgents(query) {
  return request({
    url: '/agent/direct-agents',
    method: 'get',
    params: query
  })
}

export function listDirectCustomers(query) {
  return request({
    url: '/agent/direct-customers',
    method: 'get',
    params: query
  })
}

export function createSubAgent(data) {
  return request({
    url: '/agent/create-sub',
    method: 'post',
    data
  })
}

export function createCustomer(data) {
  return request({
    url: '/agent/create-customer',
    method: 'post',
    data
  })
}
