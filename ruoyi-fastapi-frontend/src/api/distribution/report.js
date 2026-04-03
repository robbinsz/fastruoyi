import request from '@/utils/request'
import { saveAs } from 'file-saver'

export function getDashboard(query) {
  return request({
    url: '/report/dashboard',
    method: 'get',
    params: query
  })
}

export function listEarnings(query) {
  return request({
    url: '/report/earnings/list',
    method: 'get',
    params: query
  })
}

export function getEarningsTrend(query) {
  return request({
    url: '/report/earnings/trend',
    method: 'get',
    params: query
  })
}

export function listSubAgentsSummary(query) {
  return request({
    url: '/report/sub-agents',
    method: 'get',
    params: query
  })
}

export function getMyEarnings(query) {
  return request({
    url: '/report/my-earnings',
    method: 'get',
    params: query
  })
}

export function exportEarnings(query) {
  return request({
    url: '/report/earnings/export',
    method: 'get',
    params: query,
    responseType: 'blob'
  }).then((data) => {
    const blob = new Blob([data])
    const fallbackName = `earnings-${Date.now()}.xlsx`
    saveAs(blob, fallbackName)
  })
}
