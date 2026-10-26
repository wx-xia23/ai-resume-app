// ============================================================
// 首页「优秀简历」mock 数据
// 按「岗位标签 + 序号」确定性生成：同一岗位同一序号永远是同一份简历，
// 保证切换标签、上滑加载更多、跳转详情的行为稳定可复现。
// 每个岗位固定 15 条，首页每页展示 7 条，用于模拟上滑加载更多。
// ============================================================

const SURNAMES = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']
const GIVEN_NAMES = ['伟', '芳', '娜', '敏', '静', '磊', '军', '洋', '勇', '杰', '涛', '明', '超', '鑫', '晨', '悦', '婷', '雪', '宇', '浩']
const COMPANIES = ['字节跳动', '腾讯', '阿里巴巴', '百度', '美团', '京东', '华为', '小米', '网易', '快手', '哔哩哔哩', '滴滴', '携程', '拼多多', '小红书', 'OPPO', 'vivo', '顺丰科技', '平安科技', '商汤科技']
const SCHOOLS = ['北京大学', '清华大学', '浙江大学', '复旦大学', '上海交通大学', '华中科技大学', '武汉大学', '中山大学', '南京大学', '哈尔滨工业大学', '西安电子科技大学', '电子科技大学']
const MAJORS = ['计算机科学与技术', '软件工程', '电子信息工程', '信息管理与信息系统', '数据科学与大数据技术', '自动化', '通信工程', '网络工程', '人工智能', '数学与应用数学']
const DEGREES = ['本科', '硕士']
const CITIES = ['北京', '上海', '深圳', '杭州', '广州', '成都', '南京', '武汉']
const TAGS = ['大厂背景', '名校毕业', '项目经验丰富', '技术栈匹配', '数据驱动', '管理经验', '开源贡献', '竞赛获奖', '连续晋升', '跨团队协作']
const SKILL_POOL = ['Python', 'Java', 'SQL', '数据结构与算法', 'Git', 'Docker', 'Linux', 'Vue/React', 'Node.js', 'Go', '机器学习', '数据分析', '项目管理', '需求分析', 'Figma', 'Axure', 'Excel', 'PPT', '英语读写', '团队管理']
const ROLES = ['资深工程师', '团队负责人', '核心开发', '项目主管']

const EXPERIENCE_TPL = [
  ['主导核心模块的设计与开发，推动性能优化 30%+', '与产品、设计、测试多方协作，保证项目按期上线', '参与技术方案评审，输出高质量设计文档'],
  ['负责业务系统架构升级与重构，支撑千万级日活', '搭建数据监控体系，线上问题定位效率提升 50%', '带领 3-5 人小组完成季度重点项目交付'],
  ['从 0 到 1 搭建核心服务，支撑多条业务线稳定运行', '建立自动化测试与发布流程，发布效率提升 40%', '推动 code review 与工程规范落地'],
  ['负责用户增长相关功能迭代，核心转化率提升 15%', '通过 AB 实验持续优化策略，沉淀可复用方法论', '与算法团队协作落地推荐策略，人均时长提升 12%'],
  ['负责核心业务数据分析与指标体系搭建', '输出经营分析报告，辅助管理层决策', '推动数据产品化，节省人工报表时间 60%'],
]

const PROJECT_TPL = [
  ['智能客服系统', '负责意图识别与多轮对话模块，准确率提升至 92%，接入 10+ 业务线'],
  ['高并发消息推送平台', '设计并实现千万级消息推送架构，延迟降低至秒级，日推送量超 5 亿'],
  ['数据可视化大屏', '基于 ECharts 搭建实时监控大屏，支撑运营与决策场景'],
  ['推荐系统优化项目', '参与召回与排序策略优化，CTR 提升 18%，人均时长提升 12%'],
  ['自动化测试平台', '搭建 UI 自动化测试框架，回归测试耗时从 8 小时降至 40 分钟'],
  ['移动端性能优化', '主导启动速度与流畅度优化，启动耗时降低 45%，卡顿率下降 60%'],
]

const pick = (pool, index) => pool[index % pool.length]

function buildBasic(position, index) {
  const name = pick(SURNAMES, index) + pick(GIVEN_NAMES, index + 5)
  const years = 2 + (index % 7)
  return {
    name,
    jobTitle: position,
    company: pick(COMPANIES, index * 3),
    years,
    education: `${pick(SCHOOLS, index)} · ${pick(MAJORS, index + 2)} · ${pick(DEGREES, index + 4)}`,
    score: 88 + (index % 9), // 88-96 的优秀简历评分
    tags: [pick(TAGS, index), pick(TAGS, index + 3), pick(TAGS, index + 6)],
  }
}

function buildFullResume(position, index, basic) {
  const expCount = 2 + (index % 2)
  const experience = Array.from({ length: expCount }, (_, i) => {
    const tpl = EXPERIENCE_TPL[(index + i) % EXPERIENCE_TPL.length]
    return {
      company: pick(COMPANIES, index * 3 + i + 1),
      title: `${position} · ${pick(ROLES, index + i)}`,
      period: `${2017 + (index % 3) + i * 2}.0${1 + (index % 9)} - 至今`,
      duties: tpl,
    }
  })

  const projectCount = 2 + (index % 2)
  const projects = Array.from({ length: projectCount }, (_, i) => {
    const item = PROJECT_TPL[(index + i) % PROJECT_TPL.length]
    return { name: item[0], desc: item[1] }
  })

  const skillCount = 8 + (index % 4)
  const skills = Array.from({ length: skillCount }, (_, i) => pick(SKILL_POOL, index * 2 + i))

  return {
    basic: [
      { label: '姓名', value: basic.name },
      { label: '意向岗位', value: position },
      { label: '工作年限', value: `${basic.years} 年` },
      { label: '学历', value: basic.education },
      { label: '年龄', value: `${26 + (index % 6)} 岁` },
      { label: '城市', value: pick(CITIES, index) },
      { label: '电话', value: `138****${String(1000 + index * 37).slice(-4)}` },
      { label: '邮箱', value: `candidate${index + 1}@example.com` },
    ],
    education: [
      {
        school: pick(SCHOOLS, index),
        major: pick(MAJORS, index + 2),
        degree: pick(DEGREES, index + 4),
        period: `${2013 + (index % 4)}.09 - ${2017 + (index % 4)}.06`,
        note: '主修课程：数据结构、操作系统、计算机网络、数据库原理；GPA 专业前 15%',
      },
    ],
    experience,
    projects,
    skills,
  }
}

function buildResume(position, index) {
  const basic = buildBasic(position, index)
  return {
    id: `resume-${position}-${index + 1}`,
    ...basic,
    fullResume: buildFullResume(position, index, basic),
  }
}

const cache = {}

export function getResumes(position) {
  if (!cache[position]) {
    cache[position] = Array.from({ length: 15 }, (_, i) => buildResume(position, i))
  }
  return cache[position]
}