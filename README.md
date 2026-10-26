# AI 简历评估 App（求职 Demo）

技术栈：**Uni-App（Vue 3，仅 App 端）** + **FastAPI** + **DeepSeek 大模型**。

- 无数据库：评估历史保存在 App 本地存储（`uni.setStorageSync`）。
- 无磁盘持久化：PDF 由后端 `PyPDF2` 从内存（`BytesIO`）解析，解析完成后直接丢弃。
- 三个底部 Tab：首页（优秀简历）、评估（核心）、我的（历史）。

## 目录结构

```text
ai-resume-app/
├── README.md
├── backend/
│   ├── main.py            # FastAPI：POST /api/evaluate、GET /api/health
│   ├── deepseek.py        # DeepSeek 客户端：prompt、请求、JSON 兜底解析
│   ├── industries.py      # 行业名称清单（与前端一致）
│   └── requirements.txt
└── frontend/              # Uni-App 工程（HBuilderX 导入 frontend 目录即可）
    ├── App.vue
    ├── main.js
    ├── manifest.json      # vueVersion=3，App 端配置
    ├── pages.json         # 3 个 Tab（纯文字）+ 简历详情页
    ├── index.html
    ├── uni.scss
    ├── utils/
    │   ├── config.js      # BASE_URL 配置（真机调试改局域网 IP）
    │   └── mockResume.js  # 岗位 1/2/3 各 15 条 mock 优秀简历
    └── pages/
        ├── index/index.vue            # 首页
        ├── evaluate/evaluate.vue      # 评估页（核心）
        ├── profile/profile.vue        # 我的
        └── resume-detail/resume-detail.vue  # 简历详情
```

## 后端运行

```bash
cd backend
pip install -r requirements.txt
```

设置环境变量后再启动：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY = "sk-你的key"
uvicorn main:app --host 0.0.0.0 --port 8000

# macOS / Linux
# export DEEPSEEK_API_KEY="sk-你的key"
# uvicorn main:app --host 0.0.0.0 --port 8000
```

可选环境变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 无（必填） | DeepSeek API Key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API 地址 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 模型名 |

验证服务：浏览器或 curl 访问 `http://127.0.0.1:8000/api/health` 返回 `{"status":"ok"}`。

## 前端运行

- **HBuilderX**：文件 → 导入 → 从本地目录导入 `frontend` 文件夹 → 运行 → 运行到手机或模拟器。
- **Android 模拟器上传 PDF**：评估页在 App 端使用原生文件选择器（Native.js），选中后将 `content://` 流转存到 App 私有缓存临时文件，上传成功后立即删除；H5 端仍使用 `uni.chooseFile`。
- **CLI**：`cd frontend && npm install && npm run dev:app`（需要 Node 环境与 HBuilderX 命令行工具）。

真机调试时修改 `frontend/utils/config.js` 中的 `BASE_URL` 为电脑局域网 IP（例如 `http://192.168.1.100:8000`），并确保手机与电脑同网段、后端监听 `0.0.0.0`。

## 接口约定

`POST /api/evaluate`（multipart/form-data）

| 字段 | 说明 |
| --- | --- |
| `file` | PDF 简历文件（仅 `.pdf`） |
| `industries` | JSON 数组字符串，如 `["互联网/IT","产品经理"]`，1-3 个 |

成功返回：

```json
{
  "filename": "resume.pdf",
  "total_score": 88,
  "general_advice": "通用修改建议",
  "industry_scores": [
    { "industry": "互联网/IT", "score": 90, "advice": "针对性优化建议" }
  ]
}
```

错误码：`400` 非 PDF / 解析失败 / 文本为空；`422` 行业参数非法或超 3 个；`504` DeepSeek 超时；`502` DeepSeek 失败。

## 功能与验收清单

- 首页：岗位标签可切换、可添加（最多 3 个）与删除；每页 7 条，上滑加载更多直到“没有更多了”；点击条目进入详情。
- 评估：上传 PDF、最多勾选 3 个行业并展示必备技能；提交后展示总分、通用建议、各行业分数与建议；异常（非 PDF、解析失败、网络超时、输入为空、未配置 API Key）均有中文提示。
- 我的：个人信息 + 评估统计；历史记录持久化，点击查看完整结果，支持清空。

## 说明

- 行业清单（8 个）与必备技能由前端写死，后端 `industries.py` 仅做合法性校验并注入 prompt，两者名称必须一致。
- 首页 mock 简历为确定性生成数据（同一岗位同一序号内容固定），每岗位 15 条。
- 评分依赖 DeepSeek 返回，未配置 `DEEPSEEK_API_KEY` 时后端返回 `502` 并在页面提示。

## 部署上线（免费 PaaS）

前端 H5 与后端 API 分开部署，最终得到两个公网地址。仓库根目录已内置 Render 蓝图配置 `render.yaml`。

### 1. 后端部署到 Render

1. 把整个项目推到 GitHub 仓库（需要 Git 或 GitHub Desktop）。
2. 打开 [Render](https://render.com) → New → Blueprint → 选择该仓库，Render 会自动读取 `render.yaml` 创建服务。
   - 也可以手动创建：New → Web Service，Root Directory 填 `backend`，Build Command 填 `pip install -r requirements.txt`，Start Command 填 `uvicorn main:app --host 0.0.0.0 --port $PORT`。
3. 在服务 Environment 中填写 `DEEPSEEK_API_KEY`（`render.yaml` 里标记为 `sync: false`，必须在控制台手动填）。
4. 部署完成后访问 `https://<服务名>.onrender.com/api/health`，返回 `{"status":"ok"}` 即成功。

> 免费实例闲置会休眠，首次访问需 30-60 秒冷启动；演示前先访问一次唤醒。

### 2. 前端 H5 部署

1. 修改 `frontend/utils/config.js` 中的 `PROD_BASE_URL` 为上面拿到的后端地址（https）。
2. HBuilderX → 发行 → 网站-H5手机版，产物目录为 `frontend/unpackage/dist/build/h5`。
3. 打开 [Cloudflare Pages](https://pages.cloudflare.com) → Create a project → Direct Upload，把该 `h5` 目录整体拖入上传。
4. 部署完成后得到 `https://<项目名>.pages.dev`，手机或电脑浏览器打开即可使用。

### 3. 上线注意事项

- 前端为 https 时后端也必须是 https，否则浏览器会拦截混合内容请求。
- 不要用 Vercel / Netlify Functions 托管后端：函数超时约 10 秒，DeepSeek 评估会失败，需用常驻服务。
- PDF 上传受平台请求体大小限制，Render 与云服务器无明显压力。
- 评估历史与个人信息保存在浏览器 localStorage，换设备看不到（无数据库设计的正常表现）。
- 部署到子路径（如 GitHub Pages 的 `/repo/`）需在 `manifest.json` 里配置 `h5.router.base`；Cloudflare Pages 根域名部署无需配置。
