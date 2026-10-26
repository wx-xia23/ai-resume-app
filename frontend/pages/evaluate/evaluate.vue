<template>
  <view class="page">
    <!-- 上传简历 -->
    <view class="section">
      <view class="section-title">上传简历</view>
      <view v-if="!file" class="upload-area" @tap="chooseFile">
        <view class="upload-icon">📄</view>
        <view class="upload-text">点击选择 PDF 简历</view>
        <view class="upload-tip">仅支持 PDF，内存解析，不保存到服务器</view>
      </view>
      <view v-else class="file-card" @tap="chooseFile">
        <view class="file-icon">📄</view>
        <view class="file-info">
          <view class="file-name">{{ file.name }}</view>
          <view class="file-size">{{ formatSize(file.size) }}</view>
        </view>
        <view class="file-replace">重新选择</view>
      </view>
    </view>

    <!-- 意向行业 -->
    <view class="section">
      <view class="section-title">
        意向行业
        <text class="section-tip">最多选择 3 个（已选 {{ selected.length }}/3）</text>
      </view>
      <view class="industry-grid">
        <view
          v-for="ind in industries"
          :key="ind.name"
          class="industry-chip"
          :class="{ active: selected.includes(ind.name) }"
          @tap="toggleIndustry(ind.name)"
        >
          <text v-if="selected.includes(ind.name)" class="check">✓</text>
          {{ ind.name }}
        </view>
      </view>

      <!-- 行业必备技能 -->
      <view v-if="selected.length" class="skills-block">
        <view class="skills-title">行业必备技能</view>
        <view v-for="ind in selectedIndustries" :key="ind.name" class="skill-group">
          <view class="skill-group-name">{{ ind.name }}</view>
          <view class="skill-chips">
            <text v-for="(s, si) in ind.skills" :key="si" class="skill-chip">{{ s }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-btn" :class="{ disabled: submitting }" @tap="submit">
      {{ submitting ? 'AI 评估中...' : '提交 AI 评估' }}
    </view>

    <!-- 评估结果 -->
    <view v-if="result" class="result">
      <view class="result-card score-card">
        <view class="ring" :style="{ '--pct': result.total_score }">
          <view class="ring-inner">
            <view class="ring-num">{{ result.total_score }}</view>
            <view class="ring-label">总分</view>
          </view>
        </view>
        <view class="score-tip">{{ scoreTip }}</view>
      </view>

      <view class="result-card">
        <view class="result-title">通用修改建议</view>
        <view class="result-text">{{ result.general_advice }}</view>
      </view>

      <view v-for="item in result.industry_scores" :key="item.industry" class="result-card">
        <view class="industry-result-top">
          <view class="result-title">{{ item.industry }}</view>
          <view class="industry-score">{{ item.score }}<text class="unit">分</text></view>
        </view>
        <view class="progress">
          <view class="progress-bar" :style="{ width: item.score + '%' }"></view>
        </view>
        <view class="result-text">{{ item.advice }}</view>
      </view>
    </view>
  </view>
</template>

<script>
import { BASE_URL, EVALUATE_TIMEOUT } from '../../utils/config.js'

const INDUSTRIES = [
  { name: '互联网/IT', skills: ['扎实的编程基础（Java/Python）', '熟悉数据结构与算法', 'SQL 与数据库设计', 'Git 与团队协作', 'Docker / Linux 基础'] },
  { name: '人工智能/大模型', skills: ['Python + NumPy/Pandas', 'PyTorch / TensorFlow', 'NLP 与 Transformer 原理', '机器学习经典算法', 'RAG / 提示工程实践'] },
  { name: '产品经理', skills: ['需求分析与用户调研', '原型设计（Axure/Figma）', '项目管理与跨团队沟通', '数据驱动决策', 'PRD 撰写能力'] },
  { name: 'UI/UX 设计', skills: ['Figma / Sketch 熟练', '设计规范与组件化', '交互设计思维', '用户研究方法', '视觉审美与排版'] },
  { name: '金融/风控', skills: ['财务报表分析能力', '风控模型与策略', 'Excel / SQL 数据处理', '证券/基金从业知识', '合规与风险意识'] },
  { name: '市场营销', skills: ['品牌策略与定位', '内容营销与文案', '数据分析（GA/BI）', '社交媒体运营', '活动策划与执行'] },
  { name: '人力资源', skills: ['招聘全流程管理', '员工关系与绩效管理', '劳动法律法规', '组织发展经验', 'HR 数据化思维'] },
  { name: '教育培训', skills: ['课程设计与教研', '授课与表达能力', '学员运营与服务', '学习效果评估', '学科专业知识'] },
]

export default {
  data() {
    return {
      industries: INDUSTRIES,
      selected: [],
      file: null,
      filePath: '',
      submitting: false,
      result: null,
    }
  },
  onUnload() {
    // 页面离开时清理 App 端临时缓存文件
    this.deleteTempFile()
  },
  computed: {
    selectedIndustries() {
      return this.industries.filter((i) => this.selected.includes(i.name))
    },
    scoreTip() {
      const s = this.result ? this.result.total_score : 0
      if (s >= 90) return '非常优秀，极具竞争力'
      if (s >= 80) return '良好，稍作优化即可冲刺大厂'
      if (s >= 70) return '基础扎实，按建议重点打磨亮点'
      if (s >= 60) return '有提升空间，建议逐条优化'
      return '需大幅优化，建议对照建议逐项修改'
    },
  },
  methods: {
    chooseFile() {
      // #ifdef APP-PLUS
      this.pickPdfInApp()
      // #endif
      // #ifndef APP-PLUS
      uni.chooseFile({
        count: 1,
        extension: ['.pdf'],
        success: (res) => {
          const f = res.tempFiles && res.tempFiles[0]
          if (!f) return
          this.file = { name: f.name || '未命名.pdf', size: f.size || 0 }
          this.filePath = f.path
        },
        fail: () => {
          uni.showToast({ title: '未选择文件', icon: 'none' })
        },
      })
      // #endif
    },
    // #ifdef APP-PLUS
    pickPdfInApp() {
      try {
        const REQ = 1001
        const main = plus.android.runtimeMainActivity()
        const Intent = plus.android.importClass('android.content.Intent')
        const intent = new Intent(Intent.ACTION_GET_CONTENT)
        // 部分模拟器的系统文件选择器会忽略 application/pdf 过滤导致列表为空，
        // 这里放宽为 */*，选中后再校验文件名是否为 .pdf。
        intent.setType('*/*')
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        main.startActivityForResult(intent, REQ)

        main.onActivityResult = (requestCode, resultCode, data) => {
          if (requestCode !== REQ) return
          if (resultCode !== -1 || !data) {
            // 用户取消选择，无需提示
            return
          }
          try {
            const uri = data.getData()
            if (!uri) return
            this.copyPickedPdf(main, uri)
          } catch (e) {
            uni.showToast({ title: '读取 PDF 失败，请重试', icon: 'none' })
          }
        }
      } catch (e) {
        uni.showToast({ title: '无法打开文件选择器', icon: 'none' })
      }
    },
    copyPickedPdf(main, uri) {
      uni.showLoading({ title: '正在读取简历...', mask: true })
      try {
        const resolver = main.getContentResolver()

        // 读取系统返回的显示文件名（android.provider.OpenableColumns.DISPLAY_NAME）
        let displayName = ''
        const OpenableColumns = plus.android.importClass('android.provider.OpenableColumns')
        const cursor = resolver.query(uri, null, null, null, null)
        if (cursor && cursor.moveToFirst()) {
          const nameIdx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
          if (nameIdx >= 0) displayName = cursor.getString(nameIdx)
          cursor.close()
        }
        if (!displayName) displayName = '未命名.pdf'
        if (!displayName.toLowerCase().endsWith('.pdf')) {
          uni.showToast({ title: '请选择 PDF 文件', icon: 'none' })
          return
        }

        // 将 content:// 流转存到 App 私有缓存目录（临时文件，上传成功后删除）
        const File = plus.android.importClass('java.io.File')
        const cacheDir = main.getCacheDir()
        const outFile = new File(cacheDir, 'resume_upload_' + Date.now() + '.pdf')
        const input = resolver.openInputStream(uri)
        const FileOutputStream = plus.android.importClass('java.io.FileOutputStream')
        const output = new FileOutputStream(outFile)
        const ArrayCls = plus.android.importClass('java.lang.reflect.Array')
        const ByteCls = plus.android.importClass('java.lang.Byte')
        const buffer = ArrayCls.newInstance(ByteCls.TYPE, 8192)
        let len
        while ((len = plus.android.invoke(input, 'read', buffer)) > 0) {
          plus.android.invoke(output, 'write', buffer, 0, len)
        }
        input.close()
        output.close()

        this.file = { name: displayName, size: outFile.length() }
        this.filePath = outFile.getAbsolutePath()
      } catch (e) {
        uni.showToast({ title: '读取 PDF 失败，请重试', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    // #endif
    deleteTempFile() {
      if (!this.filePath) return
      // #ifdef APP-PLUS
      try {
        const File = plus.android.importClass('java.io.File')
        const f = new File(this.filePath)
        f.delete()
      } catch (e) {
        // 清理失败可忽略
      }
      // #endif
      this.filePath = ''
    },
    toggleIndustry(name) {
      const idx = this.selected.indexOf(name)
      if (idx > -1) {
        this.selected.splice(idx, 1)
        return
      }
      if (this.selected.length >= 3) {
        uni.showToast({ title: '最多选择 3 个意向行业', icon: 'none' })
        return
      }
      this.selected.push(name)
    },
    formatSize(size) {
      if (!size) return '未知大小'
      return size > 1024 * 1024
        ? (size / 1024 / 1024).toFixed(1) + ' MB'
        : Math.max(1, Math.round(size / 1024)) + ' KB'
    },
    submit() {
      if (this.submitting) return
      if (!this.file || !this.filePath) {
        uni.showToast({ title: '请先上传 PDF 简历', icon: 'none' })
        return
      }
      if (!this.selected.length) {
        uni.showToast({ title: '请至少选择 1 个意向行业', icon: 'none' })
        return
      }
      this.doUpload()
    },
    doUpload() {
      this.submitting = true
      this.result = null
      uni.showLoading({ title: 'AI 评估中...', mask: true })

      let settled = false
      const finish = () => {
        if (settled) return
        settled = true
        uni.hideLoading()
        this.submitting = false
      }

      uni.uploadFile({
        url: `${BASE_URL}/api/evaluate`,
        filePath: this.filePath,
        name: 'file',
        formData: { industries: JSON.stringify(this.selected) },
        success: (res) => {
          if (settled) return
          let data = {}
          try {
            data = JSON.parse(res.data)
          } catch (e) {
            data = {}
          }
          if (res.statusCode >= 200 && res.statusCode < 300 && typeof data.total_score === 'number') {
            this.result = data
            this.saveHistory(data)
            finish()
            this.deleteTempFile()
            uni.showToast({ title: '评估完成', icon: 'success' })
          } else {
            finish()
            this.handleError(res.statusCode, data.detail)
          }
        },
        fail: () => {
          if (settled) return
          finish()
          this.toast('请求失败，请检查网络或后端服务是否启动')
        },
      })

      // 兜底超时保护：网络异常 / 后端 504 时也保证 UI 恢复
      setTimeout(() => {
        if (settled) return
        finish()
        this.toast('请求超时，请稍后重试')
      }, EVALUATE_TIMEOUT)
    },
    handleError(status, detail) {
      let msg = ''
      if (status === 400) msg = detail || '文件格式或内容不正确'
      else if (status === 422) msg = detail || '请选择 1-3 个意向行业'
      else if (status === 504) msg = detail || 'AI 评估超时，请稍后重试'
      else if (status === 502) msg = detail || 'AI 服务异常，请稍后重试'
      else msg = `服务异常（${status}）`
      this.toast(msg)
    },
    toast(title) {
      uni.showToast({ title, icon: 'none', duration: 2500 })
    },
    saveHistory(data) {
      const record = {
        time: this.formatTime(new Date()),
        filename: this.file ? this.file.name : '',
        totalScore: data.total_score,
        industries: (data.industry_scores || []).map((i) => i.industry),
        result: data,
      }
      const history = uni.getStorageSync('eval_history') || []
      history.unshift(record)
      uni.setStorageSync('eval_history', history.slice(0, 20))
    },
    formatTime(date) {
      const p = (n) => (n < 10 ? '0' + n : '' + n)
      return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())} ${p(date.getHours())}:${p(date.getMinutes())}`
    },
  },
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx 24rpx 64rpx;
  box-sizing: border-box;
}

.section {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2329;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-tip {
  font-size: 22rpx;
  color: #8A9099;
  font-weight: 400;
}

.upload-area {
  margin-top: 24rpx;
  border: 3rpx dashed #C9D4E8;
  border-radius: 20rpx;
  background: #F7F9FD;
  padding: 56rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  font-size: 64rpx;
}

.upload-text {
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #3B6EF6;
  font-weight: 500;
}

.upload-tip {
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #9AA3AF;
}

.file-card {
  margin-top: 24rpx;
  display: flex;
  align-items: center;
  background: #F7F9FD;
  border-radius: 20rpx;
  padding: 28rpx;
}

.file-icon {
  font-size: 48rpx;
}

.file-info {
  flex: 1;
  margin-left: 20rpx;
  min-width: 0;
}

.file-name {
  font-size: 28rpx;
  color: #1F2329;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #9AA3AF;
}

.file-replace {
  font-size: 24rpx;
  color: #3B6EF6;
}

.industry-grid {
  margin-top: 24rpx;
  display: flex;
  flex-wrap: wrap;
}

.industry-chip {
  margin: 0 14rpx 14rpx 0;
  padding: 16rpx 28rpx;
  border-radius: 999rpx;
  background: #F2F4F8;
  color: #5B6470;
  font-size: 26rpx;
  border: 2rpx solid transparent;
}

.industry-chip.active {
  background: rgba(59, 110, 246, 0.08);
  color: #3B6EF6;
  border-color: #3B6EF6;
  font-weight: 500;
}

.check {
  margin-right: 6rpx;
  font-weight: 700;
}

.skills-block {
  margin-top: 8rpx;
  border-top: 2rpx solid #F0F2F6;
  padding-top: 24rpx;
}

.skills-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F2329;
}

.skill-group {
  margin-top: 20rpx;
}

.skill-group-name {
  font-size: 24rpx;
  color: #3B6EF6;
  margin-bottom: 12rpx;
}

.skill-chips {
  display: flex;
  flex-wrap: wrap;
}

.skill-chip {
  margin: 0 12rpx 12rpx 0;
  padding: 10rpx 20rpx;
  border-radius: 12rpx;
  background: #EEF3FF;
  color: #4A6FCF;
  font-size: 22rpx;
}

.submit-btn {
  margin-top: 8rpx;
  height: 96rpx;
  line-height: 96rpx;
  text-align: center;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 12rpx 28rpx rgba(59, 110, 246, 0.3);
}

.submit-btn.disabled {
  opacity: 0.6;
}

.result {
  margin-top: 32rpx;
}

.result-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 44rpx 28rpx;
}

.ring {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  background: conic-gradient(#3B6EF6 calc(var(--pct) * 1%), #E9EEF7 0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-inner {
  width: 156rpx;
  height: 156rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-num {
  font-size: 60rpx;
  font-weight: 700;
  color: #3B6EF6;
  line-height: 1;
}

.ring-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8A9099;
}

.score-tip {
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #5B6470;
}

.result-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2329;
}

.result-text {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #5B6470;
  line-height: 1.7;
}

.industry-result-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.industry-score {
  font-size: 34rpx;
  font-weight: 700;
  color: #3B6EF6;
}

.unit {
  font-size: 22rpx;
  font-weight: 400;
  color: #8A9099;
}

.progress {
  margin-top: 16rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: #EEF1F6;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #3B6EF6, #6A8CFF);
}
</style>