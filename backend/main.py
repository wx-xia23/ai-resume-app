"""AI 简历评估后端：FastAPI + PyPDF2（内存解析，不落盘）+ DeepSeek。"""

import io
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader

from deepseek import DeepSeekError, DeepSeekTimeout, evaluate_resume
from industries import INDUSTRY_NAMES

MAX_INDUSTRIES = 3

app = FastAPI(
    title="AI简历评估 API",
    description="上传 PDF 简历，内存解析后调用 DeepSeek 进行评分与建议",
    version="1.0.0",
)

# App 原生请求不受 CORS 限制，此处仅为本地调试 / 接口测试工具提供便利
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_pdf(content: bytes) -> str:
    """在内存中解析 PDF，返回全部文本；解析失败抛出 HTTPException。"""
    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"PDF 解析失败，请确认文件未损坏（{exc}）")

    if reader.is_encrypted:
        raise HTTPException(status_code=400, detail="PDF 已加密，暂不支持解析")

    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts).strip()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/evaluate")
async def evaluate(file: UploadFile = File(...), industries: str = Form(...)):
    filename = file.filename or "未命名文件"

    # 1. 非 PDF 校验
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式的简历文件")

    # 2. 读取文件内容（全程内存处理，不写入磁盘）
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 3. 意向行业参数校验（1-3 个，且必须在已知清单内）
    try:
        industry_names = json.loads(industries)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=422, detail="意向行业参数格式错误")

    if not isinstance(industry_names, list) or not 1 <= len(industry_names) <= MAX_INDUSTRIES:
        raise HTTPException(status_code=422, detail=f"请选择 1-{MAX_INDUSTRIES} 个意向行业")

    unknown = [name for name in industry_names if name not in INDUSTRY_NAMES]
    if unknown:
        raise HTTPException(status_code=422, detail=f"包含未知行业：{'、'.join(unknown)}")

    # 4. 内存解析 PDF 并提取文本
    text = _parse_pdf(content)
    if len(text) < 20:
        raise HTTPException(status_code=400, detail="未能从 PDF 中提取到有效文本，请检查文件内容")

    # 5. 调用 DeepSeek 评估
    try:
        result = evaluate_resume(text, industry_names)
    except DeepSeekTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc))
    except DeepSeekError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    # 6. 返回结果（PDF 字节流与文件对象随请求结束被回收，不保存到磁盘）
    return {
        "filename": filename,
        "total_score": result["total_score"],
        "general_advice": result["general_advice"],
        "industry_scores": result["industry_scores"],
    }

# 前端 H5 静态资源：网页与 API 同服务托管，访问根路径即是网站
_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
