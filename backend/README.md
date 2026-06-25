# 人脸比例与形象建议分析 Backend

这是一个 FastAPI 后端，用于上传单张正脸照片后进行面部关键点、照片质量、比例与上镜表现分析。结果仅用于娱乐、拍照建议、发型建议和形象参考，不代表现实中的绝对颜值。

## 边界

- 不做人脸身份识别
- 不做人脸库
- 不做人脸检索
- 不判断民族、种族、汉族、亚洲人等敏感身份
- 不保存用户原图
- 图片处理完成后会删除临时文件
- 照片不适合分析时不返回低分，而是提示重新上传

## 安装

```powershell
cd D:\ai\html\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 启动

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 接口

`POST /analyze`

请求类型：`multipart/form-data`

字段：

- `image`: JPG、PNG 或 WEBP 图片，最大 8MB

示例：

```powershell
curl.exe -X POST "http://127.0.0.1:8000/analyze" -F "image=@C:\path\photo.jpg"
```

## 评分逻辑

正式评分前先检查照片适配度：

- 是否检测到单人脸
- 人脸区域是否足够大
- 是否接近正脸
- 是否明显模糊
- 是否过暗或过曝
- 关键点是否稳定

不适合分析时返回：

```json
{
  "status": "not_suitable",
  "reason": "当前照片不适合分析",
  "issues": ["图片清晰度不足，关键点可能不稳定"],
  "suggestions": ["请上传正脸照片"]
}
```

适合分析时采用基础分机制：

```text
final_score = 60 + A + B + C + D + E - P
```

- A：面部比例加分，0 到 12
- B：脸型轮廓加分，0 到 10
- C：五官协调加分，0 到 10
- D：皮肤与状态加分，0 到 5
- E：上镜表现加分，0 到 5
- P：照片质量扣分，0 到 12

最终分数限制在 `45` 到 `98`。

所有比例判断使用区间评分，不使用单一理想值硬扣分。

## 测试

```powershell
cd D:\ai\html\backend
pytest
```
