<template>
  <view class="page">
    <!-- 顶部标题 -->
    <view class="header">
      <view class="header-title">优秀简历</view>
      <view class="header-sub">参考高分简历，打磨你的求职竞争力</view>
    </view>

    <!-- 岗位标签：用户自己添加，不足 3 个按实际展示，最多 3 个 -->
    <scroll-view class="tabs" scroll-x :show-scrollbar="false">
      <view class="tabs-inner">
        <view
          v-for="(p, i) in positions"
          :key="i"
          class="tab"
          :class="{ active: p === current }"
          @tap="switchTab(p)"
        >
          <text class="tab-text">{{ p }}</text>
          <text v-if="editing" class="tab-del" @tap.stop="removeTab(i)">×</text>
        </view>
        <view v-if="positions.length < 3" class="tab tab-add" @tap="openAdd">＋</view>
        <view class="tab tab-edit" @tap="editing = !editing">{{ editing ? '完成' : '编辑' }}</view>
      </view>
    </scroll-view>

    <!-- 空状态：一个岗位都没有 -->
    <view v-if="!positions.length" class="empty">
      <view class="empty-icon">📋</view>
      <view class="empty-text">还没有意向岗位</view>
      <view class="empty-btn" @tap="openAdd">添加岗位</view>
    </view>

    <!-- 简历列表 -->
    <view v-else class="list">
      <view
        v-for="r in visible"
        :key="r.id"
        class="resume-card"
        @tap="goDetail(r)"
      >
        <view class="avatar" :style="{ backgroundColor: avatarColor(r.name) }">{{ r.name.slice(0, 1) }}</view>
        <view class="card-main">
          <view class="card-top">
            <text class="card-name">{{ r.name }}</text>
            <text class="score-badge">{{ r.score }}分</text>
          </view>
          <view class="card-job">{{ r.jobTitle }} · {{ r.company }}</view>
          <view class="card-meta">{{ r.years }}年经验 · {{ r.education }}</view>
          <view class="card-tags">
            <text v-for="(t, ti) in r.tags" :key="ti" class="tag">{{ t }}</text>
          </view>
        </view>
        <view class="arrow">›</view>
      </view>
      <view class="list-footer">{{ listFooter }}</view>
    </view>

    <!-- 添加岗位弹窗 -->
    <view v-if="showAdd" class="mask" @tap="closeAdd">
      <view class="popup" @tap.stop>
        <view class="popup-title">添加意向岗位</view>
        <view class="popup-tip">最多 3 个岗位，输入名称后回车或点击添加</view>
        <input
          v-model="newPosition"
          class="popup-input"
          placeholder="例如：前端开发、产品经理"
          confirm-type="done"
          @confirm="confirmAdd"
        />
        <view class="popup-btns">
          <view class="popup-btn cancel" @tap="closeAdd">取消</view>
          <view class="popup-btn ok" @tap="confirmAdd">添加</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getResumes } from '../../utils/mockResume.js'

const PAGE_SIZE = 7
const STORAGE_KEY = 'home_positions'
const DEFAULT_POSITIONS = ['岗位1', '岗位2', '岗位3']

export default {
  data() {
    return {
      positions: [],
      current: '',
      all: [],
      visible: [],
      page: 1,
      loadingMore: false,
      noMore: false,
      editing: false,
      showAdd: false,
      newPosition: '',
    }
  },
  computed: {
    listFooter() {
      if (this.loadingMore) return '加载中...'
      if (this.noMore) return '— 没有更多了 —'
      return '上滑加载更多'
    },
  },
  onLoad() {
    this.initPositions()
  },
  onReachBottom() {
    this.loadMore()
  },
  methods: {
    initPositions() {
      const saved = uni.getStorageSync(STORAGE_KEY)
      this.positions = saved && saved.length ? saved.slice(0, 3) : DEFAULT_POSITIONS.slice()
      if (!this.positions.length) {
        this.current = ''
        this.visible = []
        return
      }
      this.current = this.positions[0]
      this.resetList()
    },
    savePositions() {
      uni.setStorageSync(STORAGE_KEY, this.positions)
    },
    switchTab(name) {
      if (this.current === name) return
      this.current = name
      this.resetList()
    },
    resetList() {
      this.all = getResumes(this.current)
      this.page = 1
      this.noMore = false
      this.loadingMore = false
      this.visible = this.all.slice(0, PAGE_SIZE)
    },
    loadMore() {
      if (this.loadingMore || this.noMore || !this.all.length) return
      this.loadingMore = true
      setTimeout(() => {
        this.page += 1
        this.visible = this.all.slice(0, this.page * PAGE_SIZE)
        this.noMore = this.visible.length >= this.all.length
        this.loadingMore = false
      }, 500)
    },
    goDetail(r) {
      uni.navigateTo({
        url: `/pages/resume-detail/resume-detail?id=${encodeURIComponent(r.id)}&position=${encodeURIComponent(this.current)}`,
      })
    },
    openAdd() {
      if (this.positions.length >= 3) {
        uni.showToast({ title: '最多添加 3 个岗位', icon: 'none' })
        return
      }
      this.newPosition = ''
      this.showAdd = true
    },
    closeAdd() {
      this.showAdd = false
    },
    confirmAdd() {
      const name = this.newPosition.trim()
      if (!name) {
        uni.showToast({ title: '请输入岗位名称', icon: 'none' })
        return
      }
      if (this.positions.includes(name)) {
        uni.showToast({ title: '该岗位已存在', icon: 'none' })
        return
      }
      if (this.positions.length >= 3) {
        uni.showToast({ title: '最多添加 3 个岗位', icon: 'none' })
        return
      }
      this.positions.push(name)
      this.savePositions()
      this.showAdd = false
      this.current = name
      this.resetList()
    },
    removeTab(index) {
      const name = this.positions[index]
      uni.showModal({
        title: '删除岗位',
        content: `确定删除「${name}」吗？`,
        success: (res) => {
          if (!res.confirm) return
          this.positions.splice(index, 1)
          this.savePositions()
          if (this.current === name) {
            this.current = this.positions.length ? this.positions[0] : ''
            if (this.current) {
              this.resetList()
            } else {
              this.visible = []
            }
          }
        },
      })
    },
    avatarColor(name) {
      const colors = ['#3B6EF6', '#7C5CFC', '#00B8A9', '#F5A623', '#F5483B', '#2F9E44']
      let hash = 0
      for (let i = 0; i < name.length; i++) {
        hash = (hash * 31 + name.charCodeAt(i)) % 997
      }
      return colors[hash % colors.length]
    },
  },
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx 24rpx 48rpx;
  box-sizing: border-box;
}

.header {
  padding: 16rpx 8rpx 24rpx;
}

.header-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #1F2329;
}

.header-sub {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #8A9099;
}

.tabs {
  width: 100%;
}

.tabs-inner {
  display: flex;
  align-items: center;
}

.tab {
  flex-shrink: 0;
  margin-right: 16rpx;
  padding: 16rpx 32rpx;
  border-radius: 999rpx;
  background: #FFFFFF;
  color: #5B6470;
  font-size: 28rpx;
  font-weight: 500;
  border: 2rpx solid #E8EDF5;
  position: relative;
}

.tab.active {
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  color: #FFFFFF;
  border-color: transparent;
  box-shadow: 0 8rpx 20rpx rgba(59, 110, 246, 0.25);
}

.tab-text {
  line-height: 1.2;
}

.tab-del {
  position: absolute;
  top: -14rpx;
  right: -14rpx;
  width: 38rpx;
  height: 38rpx;
  line-height: 34rpx;
  text-align: center;
  border-radius: 50%;
  background: #F5483B;
  color: #FFFFFF;
  font-size: 30rpx;
  box-shadow: 0 4rpx 10rpx rgba(245, 72, 59, 0.3);
}

.tab-add {
  border-style: dashed;
  color: #3B6EF6;
  background: rgba(59, 110, 246, 0.06);
  border-color: rgba(59, 110, 246, 0.4);
}

.tab-edit {
  margin-left: 8rpx;
  border: none;
  color: #3B6EF6;
  background: transparent;
  font-size: 26rpx;
  padding-left: 16rpx;
  padding-right: 8rpx;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 180rpx;
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

.resume-card {
  display: flex;
  align-items: flex-start;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-top: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  color: #FFFFFF;
  font-size: 36rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-main {
  flex: 1;
  margin-left: 24rpx;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
}

.score-badge {
  background: rgba(47, 158, 68, 0.1);
  color: #2F9E44;
  font-size: 22rpx;
  font-weight: 600;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
}

.card-job {
  margin-top: 10rpx;
  font-size: 26rpx;
  color: #3B6EF6;
}

.card-meta {
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #8A9099;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-tags {
  margin-top: 14rpx;
  display: flex;
  flex-wrap: wrap;
}

.tag {
  font-size: 20rpx;
  color: #5B6470;
  background: #F2F4F8;
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  margin: 0 10rpx 10rpx 0;
}

.arrow {
  color: #C4CBD4;
  font-size: 44rpx;
  align-self: center;
  margin-left: 12rpx;
  line-height: 1;
}

.list-footer {
  text-align: center;
  color: #B0B7C1;
  font-size: 24rpx;
  padding: 32rpx 0;
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

.popup {
  width: 600rpx;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 40rpx 36rpx;
}

.popup-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #1F2329;
  text-align: center;
}

.popup-tip {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #8A9099;
  text-align: center;
}

.popup-input {
  margin-top: 32rpx;
  height: 88rpx;
  background: #F2F4F8;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
}

.popup-btns {
  margin-top: 40rpx;
  display: flex;
  gap: 20rpx;
}

.popup-btn {
  flex: 1;
  height: 84rpx;
  line-height: 84rpx;
  text-align: center;
  border-radius: 16rpx;
  font-size: 28rpx;
}

.popup-btn.cancel {
  background: #F2F4F8;
  color: #5B6470;
}

.popup-btn.ok {
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  color: #FFFFFF;
}
</style>