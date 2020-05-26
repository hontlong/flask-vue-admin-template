# vue-admin-template

Fork from: [github.com/PanJiaChen/vue-admin-template](https://github.com/PanJiaChen/vue-admin-template)

flask + vue-admin-template

修改点
1. npm run dev 方式，用 mock 数据开发，调试，可以单独调试, 需要自己在mock中构建测试数据. 不依赖flask。 这个主要用于界面开发.
1. npm run stage 方式，连接 flask 的api接口数据开发，调试。这个主要用于测试和服务的连通性。
1. npm run prod  方式，生成静态单页面在 ./dist目录，flask的模板目录和静态目录指向这个./dist目录，flask可以独立运行，不再需要node,npm。这个主要用于发布

为了构建一个可以用在flask下的简单的后台管理界面做了简化。

## Build Setup

```bash
# 进入项目目录
cd web/vue-admin-template

# 安装依赖
npm install

# 建议不要直接使用 cnpm 安装以来，会有各种诡异的 bug。可以通过如下操作解决 npm 下载速度慢的问题
npm install --registry=https://registry.npm.taobao.org

# 启动flask
sh run.sh

# 启动服务
cd web/vue-admin-template
npm run dev
npm run stage
npm run prod  
```
