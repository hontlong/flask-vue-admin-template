<!--eslint-disable-->
<template>
  <div class="app-container">
    <el-alert title="仅仅用于展示和验证，数据的导入还是要通过接口" type="info" show-icon></el-alert>
    <el-form ref="form" :model="form" label-width="120px">
      <el-row>
        <el-col :span="7">
          <el-form-item label="Table">
            <el-select v-model="form.table" placeholder="please select">
              <el-option v-for="item in tables" :key="item.table_name" :label="item.table_name"
                         :value="item">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :gutter="1" :span="3">
          <el-tag type="warning">{{form.table.sim_algo}}</el-tag>
          <el-tag type="warning">{{form.table.item_type}}</el-tag>
        </el-col>
        <el-col :gutter="1" :span="6">
          <el-form-item label="By">
            <el-select v-model="form.type" placeholder="please select">
              <el-option label="by item" value="item"/>
              <el-option label="by item_id" value="item_id"/>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Text" v-if="form.type==='item'">
        <el-input type="textarea" v-model="form.item" placeholder="please input">
        </el-input>
      </el-form-item>
      <el-form-item label="Item Id" v-else>
        <el-input v-model="form.item_id" placeholder="please input">
        </el-input>
      </el-form-item>
      <el-form-item>
        <!--<el-button @click="onCancel">Cancel</el-button>-->
        <el-button type="primary" @click="onSubmit">Submit</el-button>
      </el-form-item>
    </el-form>

    <hr/>

    <div>
      <el-table v-loading="rs.listLoading" :data="rs.list" element-loading-text="Loading" border fit
                highlight-current-row>
        <el-table-column align="center" label="Idx" width="60">
          <template slot-scope="scope">
            {{ scope.$index }}
          </template>
        </el-table-column>
        <el-table-column label="Item Id" width="200">
          <template slot-scope="scope">
            {{ scope.row.item_id }}
          </template>
        </el-table-column>
        <el-table-column label="Similar" width="80">
          <template slot-scope="scope">
            {{ scope.row.sim }}
          </template>
        </el-table-column>
        <el-table-column label="Item" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.item }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script>
  /* eslint-disable */
  import {find_sim, find_sim_by_id} from '@/api/find'
  import {getTables} from '@/api/table'

  export default {
    data() {
      return {
        tables: null,
        form: {
          table: '',
          item_id: '',
          item: '',
          type: 'item'
        },
        rs: {
          list: null,
          listLoading: false
        }
      }
    },
    created() {
      this.fetchData()
    },
    methods: {
      onSubmit() {
        this.$message('submit!')
        this.to_find()
      },
      onCancel() {
        this.$message({
          message: 'cancel!',
          type: 'warning'
        })
      },
      fetchData() {
        console.log('fetch tables')
        getTables().then(response => {
          this.tables = response.data
          console.log(this.tables)
          for (const idx in this.tables) {
            this.form.table = this.tables[idx]
            break
          }
        })
      },
      to_find() {
        this.rs.listLoading = true
        const ss = this.form.table.table_name.split('_', 2)
        const params = {
          anm: ss[0],
          need_item: true,
          ctype: ss[1]
        }
        console.log(this.form.type)
        if (this.form.type === 'item') {
          console.log('find_sim')
          params.item = Base64.encode(this.form.item)
          find_sim(params).then(response => {
            const len = response.data.length
            for (let i = 0; i < len; i++) {
              let o = response.data[i]
              if ('item' in o) {
                const text = Base64.decode(o.item)
                o.item = text
              }
            }
            this.rs.list = response.data
            this.rs.listLoading = false
          })
        } else {
          console.log('find_sim_by_id')
          params.item_id = this.form.item_id
          find_sim_by_id(params).then(response => {
            console.log(response.data)
            const len = response.data.length
            for (let i = 0; i < len; i++) {
              let o = response.data[i]
              if ('item' in o) {
                const text = Base64.decode(o.item)
                o.item = text
              }
            }
            this.rs.list = response.data
            this.rs.listLoading = false
          })
        }
      }
    }
  }
</script>

<style scoped>
  .line {
    text-align: center;
  }

  .el-alert {
    margin-bottom: 10px;
  }
</style>

