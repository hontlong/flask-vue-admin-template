export default [
  {
    url: '/select',
    type: 'get',
    response: config => {
      return {
        code: 20000,
        statue: 1,
        data: [
          {"item_id": "t_1", "sim": 0.9, "item": "abcdeaalkllaakl"},
          {"item_id": "t_2", "sim": 0.8, "item": "abcdeaalkll;akl"},
          {"item_id": "t_3", "sim": 0.7, "item": "abcdeaalkll;akl"},
          {"item_id": "t_4", "sim": 0.6, "item": "abcdeaalkll;akl"}
        ]
      }
    }
  },
  {
    url: '/select_by_id',
    type: 'get',
    response: config => {
      return {
        code: 20000,
        statue: 1,
        data: [
          {"item_id": "t_1", "sim": 0.8, "item": "abcdeaalkllaakl"},
          {"item_id": "t_3", "sim": 0.6, "item": "abcdeaalkll;akl"},
        ]
      }
    }
  }
]
