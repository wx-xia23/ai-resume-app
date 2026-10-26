<template>
  <view class="page">
    <view v-if="!resume" class="empty">
      <view class="empty-icon">📄</view>
      <view class="empty-text">未找到该简历</view>
    </view>

    <template v-else>
      <!-- 头部 -->
      <view class="head-card">
        <view class="avatar" :style="{ backgroundColor: avatarColor }">{{ resume.name.slice(0, 1) }}</view>
        <view class="head-info">
          <view class="head-name">{{ resume.name }}</view>
          <view class="head-job">{{ resume.jobTitle }} · {{ resume.company }}</view>
        </view>
        <view class="head-score">{{ resume.score }}<text class="unit">分</text></view>
      </view>

      <!-- 基本信息 -->
      <view class="section">
        <view class="section-title">基本信息</view>
        <view class="basic-grid">
          <view v-for="item in resume.fullResume.basic" :key="item.label" class="basic-item">
            <view class="basic-label">{{ item.label }}</view>
            <view class="basic-value">{{ item.value }}</view>
          </view>
        </view>
      </view>

      <!-- 教育经历 -->
      <view class="section">
        <view class="section-title">教育经历</view>
        <view v-for="(edu, i) in resume.fullResume.education" :key="i" class="edu-card">
          <view class="edu-top">
            <view class="edu-school">{{ edu.school }}</view>
            <view class="edu-period">{{ edu.period }}</view>
          </view>
          <view class="edu-meta">{{ edu.degree }} · {{ edu.major }}</view>
          <view class="edu-note">{{ edu.note }}</view>
        </view>
      </view>

      <!-- 工作经历 -->
      <view class="section">
        <view class="section-title">工作经历</view>
        <view v-for="(exp, i) in resume.fullResume.experience" :key="i" class="exp-card">
          <view class="exp-top">
            <view class="exp-company">{{ exp.company }}</view>
            <view class="exp-period">{{ exp.period }}</view>
          </view>
          <view class="exp-title">{{ exp.title }}</view>
          <view v-for="(d, di) in exp.duties" :key="di" class="exp-duty">· {{ d }}</view>
        </view>
      </view>

      <!-- 项目经历 -->
      <view class="section">
        <view class="section-title">项目经历</view>
        <view v-for="(p, i) in resume.fullResume.projects" :key="i" class="proj-card">
          <view class="proj-name">{{ p.name }}</view>
          <view class="proj-desc">{{ p.desc }}</view>
        </view>
      </view>

      <!-- 专业技能 -->
      <view class="section">
        <view class="section-title">专业技能</view>
        <view class="skill-chips">
          <text v-for="(s, i) in resume.fullResume.skills" :key="i" class="skill-chip">{{ s }}</text>
        </view>
      </view>
    </template>
  </view>
</template>

<script>
import { getResumes } from '../../utils/mockResume.js'

export default {
  data() {
    return {
      resume: null,
      avatarColor: '#3B6EF6',
    }
  },
  onLoad(options) {
    // uni-app 会自动解码 query 参数，此处直接使用
    const position = options.position || ''
    const id = options.id || ''
    const list = position ? getResumes(position) : []
    this.resume = list.find((r) => r.id === id) || null
    if (this.resume) {
      const colors = ['#3B6EF6', '#7C5CFC', '#00B8A9', '#F5A623', '#F5483B', '#2F9E44']
      let hash = 0
      const name = this.resume.name
      for (let i = 0; i < name.length; i++) {
        hash = (hash * 31 + name.charCodeAt(i)) % 997
      }
      this.avatarColor = colors[hash % colors.length]
    }
    uni.setNavigationBarTitle({ title: this.resume ? `${this.resume.name}的简历` : '简历详情' })
  },
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx 24rpx 64rpx;
  box-sizing: border-box;
}

.empty {
  padding-top: 200rpx;
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

.head-card {
  background: linear-gradient(135deg, #3B6EF6, #6A8CFF);
  border-radius: 28rpx;
  padding: 40rpx 32rpx;
  display: flex;
  align-items: center;
  color: #FFFFFF;
  box-shadow: 0 12rpx 28rpx rgba(59, 110, 246, 0.3);
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 28rpx;
  color: #FFFFFF;
  font-size: 44rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.head-info {
  flex: 1;
  margin-left: 24rpx;
  min-width: 0;
}

.head-name {
  font-size: 36rpx;
  font-weight: 700;
}

.head-job {
  margin-top: 8rpx;
  font-size: 24rpx;
  opacity: 0.9;
}

.head-score {
  font-size: 48rpx;
  font-weight: 700;
}

.unit {
  font-size: 22rpx;
  font-weight: 400;
  opacity: 0.85;
}

.section {
  margin-top: 24rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(31, 35, 41, 0.04);
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 20rpx;
}

.basic-grid {
  display: flex;
  flex-wrap: wrap;
}

.basic-item {
  width: 50%;
  margin-bottom: 18rpx;
}

.basic-label {
  font-size: 22rpx;
  color: #9AA3AF;
}

.basic-value {
  margin-top: 6rpx;
  font-size: 26rpx;
  color: #1F2329;
}

.edu-card {
  border-left: 6rpx solid #3B6EF6;
  padding-left: 20rpx;
  margin-bottom: 20rpx;
}

.edu-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.edu-school {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2329;
}

.edu-period {
  font-size: 22rpx;
  color: #9AA3AF;
}

.edu-meta {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #5B6470;
}

.edu-note {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #9AA3AF;
}

.exp-card {
  margin-bottom: 24rpx;
}

.exp-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.exp-company {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2329;
}

.exp-period {
  font-size: 22rpx;
  color: #9AA3AF;
}

.exp-title {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #3B6EF6;
}

.exp-duty {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #5B6470;
  line-height: 1.6;
}

.proj-card {
  margin-bottom: 20rpx;
  background: #F7F9FD;
  border-radius: 16rpx;
  padding: 20rpx;
}

.proj-name {
  font-size: 27rpx;
  font-weight: 600;
  color: #1F2329;
}

.proj-desc {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #5B6470;
  line-height: 1.6;
}

.skill-chips {
  display: flex;
  flex-wrap: wrap;
}

.skill-chip {
  margin: 0 12rpx 12rpx 0;
  padding: 12rpx 24rpx;
  border-radius: 12rpx;
  background: #EEF3FF;
  color: #4A6FCF;
  font-size: 24rpx;
}
</style>