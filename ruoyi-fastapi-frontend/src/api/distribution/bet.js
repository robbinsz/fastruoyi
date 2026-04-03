import request from '@/utils/request'

export function createBetLink(data) {
  return request({
    url: '/bet/link/create',
    method: 'post',
    data
  })
}

export function listBetLinks(query) {
  return request({
    url: '/bet/link/list',
    method: 'get',
    params: query
  })
}

export function openBetLink(token) {
  return request({
    url: `/bet/open/${token}`,
    method: 'get'
  })
}

export function confirmBet(token, data) {
  return request({
    url: `/bet/open/${token}/confirm`,
    method: 'post',
    data
  })
}

export function confirmBetResult(linkId, data) {
  return request({
    url: `/bet/link/${linkId}/confirm-result`,
    method: 'put',
    data
  })
}

export function listMyBets() {
  return request({
    url: '/bet/my-bets',
    method: 'get'
  })
}
