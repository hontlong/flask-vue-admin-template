import request from '@/utils/request'

export function find_sim(params) {
  return request({
    url: '/search',
    method: 'get',
    params
  })
}

export function find_sim_by_id(params) {
  return request({
    url: '/search_by_id',
    method: 'get',
    params
  })
}
