<template>
  <view class="page">
    <!-- 个人信息卡 -->
    <view class="profile-card">
      <view class="avatar">{{ avatarText }}</view>
      <view class="info">
        <view class="name">{{ profile.name }}</view>
        <view class="bio">{{ bioText }}</view>
        <view class="contact">
          <text>📞 {{ profile.phone }}</text>
          <text class="dot">·</text>
          <text>✉️ {{ profile.email }}</text>
        </view>
      </view>
      <view class="edit-btn" @tap="openEdit">编辑</view>
    </view>

    <!-- 统计 -->
    <view class="stats">
      <view class="stat-item">
        <view class="stat-num">{{ history.length }}</view>
        <view class="stat-label">评估次数</view>
      </view>
      <view class="stat-item">
        <view class="stat-num">{{ avgScore }}</view>
        <view class="stat-label">平均分</view>
      </view>
      <view class="stat-item">
        <view class="stat-num">{{ maxScore }}</view>
        <view class="stat-label">最高分</view>
      </view>
    </view>

    <!-- 历史记录 -->
    <view class="history-header">
      <view class="history-title">评估历史</view>
      <view v-if="history.length" class="clear-btn" @tap="clearHistory">清空历史</view>
    </view>

    <view v-if="!history.length" class="empty">
      <view class="empty-icon">🗂️</view>
      <view class="empty-text">暂无评估记录</view>
      <view class="empty-btn" @tap="goEvaluate">去评估简历</view>
    </view>

    <view v-else class="history-list">
      <view v-for="(item, i) in history" :key="i" class="history-card" @tap="openDetail(item)">
        <view class="history-left">
          <view class="history-file">{{ item.filename }}</view>
          <view class="history-time">{{ item.time }}</view>
          <view class="history-industries">
            <text v-for="(name, ni) in item.industries" :key="ni" class="mini-tag">{{ name }}</text>
          </view>
        </view>
        <view class="history-score">{{ item.totalScore }}<text class="unit">分</text></view>
      </view>
    </view>

    <!-- 历史详情弹层 -->
    <view v-if="detail" class="mask" @tap="detail = null">
      <view class="detail-popup" @tap.stop>
        <view class="detail-head">
          <view class="detail-ring" :style="{ '--pct': detail.result.total_score }">
            <view class="detail-ring-inner">{{ detail.result.total_score }}</view>
          </view>
          <view class="detail-meta">
            <view class="detail-file">{{ detail.filename }}</view>
            <view class="detail-time">{{ detail.time }}</view>
            <view class="detail-industries">
              <text v-for="(name, ni) in detail.industries" :key="ni" class="mini-tag">{{ name }}</text>
            </view>
          </view>
        </view>
        <scroll-view scroll-y class="detail-body">
          <view class="detail-section">
            <view class="detail-section-title">通用修改建议</view>
            <view class="detail-text">{{ detail.result.general_advice }}</view>
          </view>
          <view v-for="item in detail.result.industry_scores" :key="item.industry" class="detail-section">
            <view class="detail-section-title">{{ item.industry }} · {{ item.score }}分</view>
            <view class="detail-text">{{ item.advice }}</view>
          </view>
        </scroll-view>
        <view class="detail-close" @tap="detail = null">关闭</view>
      </view>
    </view>

    <!-- 编辑个人介绍弹层 -->
    <view v-if="showEdit" class="mask" @tap="closeEdit">
      <view class="edit-popup" @tap.stop>
        <view class="edit-title">编辑个人介绍</view>
        <view class="form-item">
          <view class="form-label">姓名</view>
          <input class="form-input" v-model="form.name" placeholder="请输入姓名" />
        </view>
        <view class="form-item">
          <view class="form-label">求职目标</view>
          <input class="form-input" v-model="form.target" placeholder="如：互联网 / 大模型方向" />
        </view>
        <view class="form-item">
          <view class="form-label">联系电话</view>
          <input class="form-input" v-model="form.phone" placeholder="请输入联系电话" />
        </view>
        <view class="form-item">
          <view class="form-label">邮箱</view>
          <input class="form-input" v-model="form.email" placeholder="请输入邮箱" />
        </view>
        <view class="edit-actions">
          <view class="edit-cancel" @tap="closeEdit">取消</view>
          <view class="edit-save" @tap="saveProfile">保存</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
const STORAGE_KEY = 'eval_history'
const PROFILE_KEY = 'user_profile'
const DEFAULT_PROFILE = {
  name: '李明',
  target: '互联网 / 大模型方向',
  phone: '138****6666',
  email: 'liming@example.com',
}

export default {
  data() {
    return {
      history: [],
      detail: null,
      showEdit: false,
      profile: { ...DEFAULT_PROFILE },
      form: { name: '', target: '', phone: '', email: '' },
    }
  },
  computed: {
    avatarText() {
      return (this.profile.name || '求').trim().charAt(0) || '求'
    },
    bioText() {
      return this.profile.target ? '求职者 · 目标：' + this.profile.target : '求职者'
    },
    avgScore() {
      if (!this.history.length) return '-'
      const sum = this.history.reduce((acc, h) => acc + Number(h.totalScore || 0), 0)
      return Math.round(sum / this.history.length)
    },
    maxScore() {
      if (!this.history.length) return '-'
      return Math.max(...this.history.map((h) => Number(h.totalScore || 0)))
    },
  },
  onShow() {
    this.history = uni.getStorageSync(STORAGE_KEY) || []
    const saved = uni.getStorageSync(PROFILE_KEY)
    if (saved && typeof saved === 'object') {
      this.profile = { ...DEFAULT_PROFILE, ...saved }
    }
  },
  methods: {
    openEdit() {
      this.form = {
        name: this.profile.name,
        target: this.profile.target,
        phone: this.profile.phone,
        email: this.profile.email,
      }
      this.showEdit = true
    },
    closeEdit() {
      this.showEdit = false
    },
    saveProfile() {
      const name = (this.form.name || '').trim()
      if (!name) {
        uni.showToast({ title: '请输入姓名', icon: 'none' })
        return
      }
      this.profile = {
        name,
        target: (this.form.target || '').trim(),
        phone: (this.form.phone || '').trim(),
        email: (this.form.email || '').trim(),
      }
      uni.setStorageSync(PROFILE_KEY, this.profile)
      this.showEdit = false
      uni.showToast({ title: '个人介绍已保存', icon: 'success' })
    },
    openDetail(item) {
      this.detail = item
    },
    clearHistory() {
      uni.showModal({
        title: '清空历史',
        content: '确定清空全部评估历史吗？此操作不可恢复。',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync(STORAGE_KEY)
            this.history = []
            this.detail = null
          }
        },
      })
    },
    goEvaluate() {
      uni.switchTab({ url: '/pages/evaluate/evaluate' })
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

.profile-card {
  position: relative;
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  border-radius: 28rpx;
  padding: 40rpx 32rpx;
  display: flex;
  align-items: center;
  color: #FFFFFF;
  box-shadow: 0 12rpx 28rpx rgba(59, 110, 246, 0.3);
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
  font-size: 52rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info {
  margin-left: 28rpx;
  min-width: 0;
}

.name {
  font-size: 36rpx;
  font-weight: 700;
}

.bio {
  margin-top: 8rpx;
  font-size: 24rpx;
  opacity: 0.9;
}

.contact {
  margin-top: 14rpx;
  font-size: 22rpx;
  opacity: 0.85;
}

.dot {
  margin: 0 8rpx;
}

.edit-btn {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  font-size: 24rpx;
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.25);
  padding: 10rpx 26rpx;
  border-radius: 999rpx;
}

.stats {
  margin-top: 24rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx 0;
  display: flex;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-num {
  font-size: 44rpx;
  font-weight: 700;
  color: #3B6EF6;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8A9099;
}

.history-header {
  margin: 40rpx 8rpx 8rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
}

.clear-btn {
  font-size: 24rpx;
  color: #F5483B;
}

.history-list {
  margin-top: 8rpx;
}

.history-card {
  margin-top: 20rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.history-left {
  flex: 1;
  min-width: 0;
}

.history-file {
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2329;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #9AA3AF;
}

.history-industries {
  margin-top: 12rpx;
  display: flex;
  flex-wrap: wrap;
}

.mini-tag {
  font-size: 20rpx;
  color: #4A6FCF;
  background: #EEF3FF;
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  margin: 0 10rpx 8rpx 0;
}

.history-score {
  font-size: 40rpx;
  font-weight: 700;
  color: #2F9E44;
  margin-left: 20rpx;
}

.unit {
  font-size: 22rpx;
  font-weight: 400;
  color: #8A9099;
}

.empty {
  margin-top: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  font-size: 96rpx;
}

.empty-text {
  margin-top: 24rpx;
  color: #8A9099;
  font-size: 28rpx;
}

.empty-btn {
  margin-top: 40rpx;
  padding: 20rpx 64rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  color: #FFFFFF;
  font-size: 28rpx;
  box-shadow: 0 8rpx 20rpx rgba(59, 110, 246, 0.25);
}

.mask {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-popup {
  width: 640rpx;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 36rpx 32rpx;
  display: flex;
  flex-direction: column;
}

.edit-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
  text-align: center;
}

.form-item {
  margin-top: 24rpx;
}

.form-label {
  font-size: 24rpx;
  color: #5B6470;
  margin-bottom: 10rpx;
}

.form-input {
  background: #F2F4F8;
  border-radius: 16rpx;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1F2329;
}

.edit-actions {
  margin-top: 40rpx;
  display: flex;
}

.edit-cancel {
  flex: 1;
  height: 84rpx;
  line-height: 84rpx;
  text-align: center;
  border-radius: 16rpx;
  background: #F2F4F8;
  color: #5B6470;
  font-size: 28rpx;
  margin-right: 16rpx;
}

.edit-save {
  flex: 1;
  height: 84rpx;
  line-height: 84rpx;
  text-align: center;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  color: #FFFFFF;
  font-size: 28rpx;
  font-weight: 600;
  margin-left: 16rpx;
}

.detail-popup {
  width: 640rpx;
  max-height: 78vh;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 36rpx 32rpx;
  display: flex;
  flex-direction: column;
}

.detail-head {
  display: flex;
  align-items: center;
  padding-bottom: 24rpx;
  border-bottom: 2rpx solid #F0F2F6;
}

.detail-ring {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background: conic-gradient(#3B6EF6 calc(var(--pct) * 1%), #E9EEF7 0);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-ring-inner {
  width: 108rpx;
  height: 108rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  font-weight: 700;
  color: #3B6EF6;
}

.detail-meta {
  flex: 1;
  margin-left: 24rpx;
  min-width: 0;
}

.detail-file {
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2329;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-time {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #9AA3AF;
}

.detail-industries {
  margin-top: 10rpx;
  display: flex;
  flex-wrap: wrap;
}

.detail-body {
  flex: 1;
  max-height: 46vh;
  margin-top: 8rpx;
}

.detail-section {
  margin-top: 24rpx;
}

.detail-section-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #3B6EF6;
}

.detail-text {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #5B6470;
  line-height: 1.7;
}

.detail-close {
  margin-top: 24rpx;
  height: 84rpx;
  line-height: 84rpx;
  text-align: center;
  border-radius: 16rpx;
  background: #F2F4F8;
  color: #5B6470;
  font-size: 28rpx;
}
</style>