# utils/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

# 硬编码一个开发阶段用的 token（这是演示用，生产会用数据库+JWT）
VALID_TOKEN = "rag-qa-secret-token-2024"

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证请求头中的 Bearer Token"""
    token = credentials.credentials
    if token != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="无效的访问令牌")
    return token