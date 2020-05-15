# vue-admin-template

Fork from: [github.com/PanJiaChen/vue-admin-template](https://github.com/PanJiaChen/vue-admin-template)

修改点
1. npm run dev 方式，用 mock 数据开发，调试
1. npm run stage 方式，连接 flask 的api接口数据开发，调试
1. npm run prod  方式，生成静态单页面在 ./dist目录，flask的模板目录和静态目录指向这个./dist目录，flask可以独立运行

为了构建一个可以用在flask下的简单的后台管理界面做了简化。

## Build Setup

```bash
# 克隆项目
git clone https://github.com/PanJiaChen/vue-admin-template.git

# 进入项目目录
cd vue-admin-template

# 安装依赖
npm install

# 建议不要直接使用 cnpm 安装以来，会有各种诡异的 bug。可以通过如下操作解决 npm 下载速度慢的问题
npm install --registry=https://registry.npm.taobao.org

# 启动服务
npm run dev
npm run stage
npm run prod
```
