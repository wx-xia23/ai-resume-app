// 后端接口地址配置
//
// 线上：网页由后端同一服务托管，走同源相对路径，留空即可（如改用独立域名托管前端，这里填后端完整地址）
// 本地地址：H5 开发调试、App 基座调试使用；真机调试改成电脑局域网 IP，如 http://192.168.1.100:8000
const PROD_BASE_URL = ''
const DEV_BASE_URL = 'http://127.0.0.1:8000'

// 发行（生产）构建走线上地址，开发调试走本地地址
const IS_PROD = process.env.NODE_ENV === 'production'

export const BASE_URL = IS_PROD ? PROD_BASE_URL : DEV_BASE_URL

// 评估请求总超时（毫秒），前端兜底保护
// 线上首次请求可能遇到免费平台冷启动（约 30-60 秒），因此放宽到 150 秒
export const EVALUATE_TIMEOUT = 150000