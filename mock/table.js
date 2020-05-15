import Mock from 'mockjs'

const data = Mock.mock({
  'items|30': [{
    id: '@id',
    title: '@sentence(10, 20)',
    'status|1': ['published', 'draft', 'deleted'],
    author: 'name',
    display_time: '@datetime',
    pageviews: '@integer(300, 5000)'
  }]
})

export default [
  {
    url: '/table/list',
    type: 'get',
    response: config => {
      const items = data.items
      return {
        code: 20000,
        // data: {
        //   total: items.length,
        //   items: items
        // }
        data: [
          {
            'table_name': 'sh_article',
            'item_type': 'text',
            'sim_algo': 'doc2vec',
          }
        ]
      }
    }
  },
  {
    url: '/admin/api/table/list',
    type: 'get',
    response: config => {
      return {
        code: 20000,
        data: [
          {
            'table_name': 'sh_article',
            'item_type': 'text',
            'sim_algo': 'doc2vec',
          }
        ]
      }
    }
  }
]
