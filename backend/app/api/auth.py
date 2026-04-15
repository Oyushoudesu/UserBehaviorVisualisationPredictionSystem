"""
认证模块
文件: backend/app/api/auth.py

提供登录、Token刷新、当前用户信息接口
依赖: pip install python-jose[cryptography] passlib[bcrypt] PyMySQL sqlalchemy
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
import os

router = APIRouter()

# ============================================================================
# 配置（建议迁移到 config.py / .env）
# ============================================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ecommerce-analysis-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8小时

# DB_URL = os.getenv(
#     "DATABASE_URL",
#     "mysql+pymysql://root:your_password@localhost:3306/ecommerce_analysis"
# )
from config import DATABASE_URL, JWT_SECRET_KEY
DB_URL = DATABASE_URL
SECRET_KEY = JWT_SECRET_KEY
# ============================================================================
# 工具初始化
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

try:
    engine = create_engine(DB_URL, pool_pre_ping=True)
except Exception as e:
    print(f"数据库连接失败，认证功能不可用: {e}")
    engine = None

# ============================================================================
# Pydantic 模型
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int      # 秒
    username: str
    nickname: str
    role: str

class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    role: str
    last_login: Optional[str]

class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    new_username: Optional[str] = None
    current_password: Optional[str] = None  # 修改用户名时需要验证当前密码

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ============================================================================
# 工具函数
# ============================================================================

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_db(username: str) -> Optional[dict]:
    if engine is None:
        return None
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT id, username, password, role, nickname, is_active, last_login "
                     "FROM sys_user WHERE username = :username"),
                {"username": username}
            ).fetchone()
            if row:
                return dict(row._mapping)
    except Exception as e:
        print(f"查询用户失败: {e}")
    return None

def update_last_login(user_id: int, ip: str = None):
    if engine is None:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE sys_user SET last_login = NOW() WHERE id = :id"),
                {"id": user_id}
            )
            conn.execute(
                text("INSERT INTO login_log (user_id, username, ip_address, success) "
                     "SELECT id, username, :ip, 1 FROM sys_user WHERE id = :id"),
                {"id": user_id, "ip": ip}
            )
    except Exception as e:
        print(f"更新登录时间失败: {e}")

# ============================================================================
# 依赖：获取当前登录用户（用于其他接口鉴权）
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_from_db(username)
    if user is None or not user["is_active"]:
        raise credentials_exception
    return user

# ============================================================================
# 接口1: 登录 → 返回 JWT Token
# ============================================================================

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    表单参数: username, password
    返回: JWT access_token
    """
    user = get_user_from_db(form_data.username)

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 生成 Token
    expire_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=expire_delta
    )

    # 更新登录时间
    update_last_login(user["id"])

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        username=user["username"],
        nickname=user["nickname"] or user["username"],
        role=user["role"]
    )

# ============================================================================
# 接口2: 获取当前用户信息
# ============================================================================

@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserInfo(
        id=current_user["id"],
        username=current_user["username"],
        nickname=current_user["nickname"] or current_user["username"],
        role=current_user["role"],
        last_login=str(current_user["last_login"]) if current_user["last_login"] else None
    )

# ============================================================================
# 接口3: 登出（前端清除Token即可，此接口可用于记录日志）
# ============================================================================

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """登出（前端负责清除本地Token）"""
    return {"message": f"用户 {current_user['username']} 已登出"}

# ============================================================================
# 接口4: 用户注册
# ============================================================================

@router.post("/register", status_code=201)
async def register(req: RegisterRequest):
    """
    用户注册

    Body: { username, password, nickname? }
    - 用户名长度 3-20 个字符
    - 密码长度不少于 6 个字符
    - 用户名不可重复
    - 注册成功后角色默认为 viewer，需管理员手动提升
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="数据库不可用，无法注册")

    username = req.username.strip()
    password = req.password

    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=422, detail="用户名长度须在 3-20 个字符之间")
    if len(password) < 6:
        raise HTTPException(status_code=422, detail="密码长度不能少于 6 个字符")

    try:
        with engine.begin() as conn:
            # 查重
            existing = conn.execute(
                text("SELECT id FROM sys_user WHERE username = :username"),
                {"username": username}
            ).fetchone()
            if existing:
                raise HTTPException(status_code=409, detail="该用户名已被注册，请更换")

            # 写入
            hashed = pwd_context.hash(password)
            nickname = (req.nickname or "").strip() or username
            conn.execute(
                text("""INSERT INTO sys_user
                        (username, password, nickname, role, is_active, created_at)
                        VALUES (:username, :password, :nickname, 'viewer', 1, NOW())"""),
                {"username": username, "password": hashed, "nickname": nickname}
            )
        print(f"新用户注册成功: {username}")
        return {"message": "注册成功，请返回登录页面"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")

# ============================================================================
# 接口5: 修改个人资料（昵称 / 用户名）
# ============================================================================

@router.put("/profile")
async def update_profile(
    req: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    修改个人资料
    - 修改昵称：直接修改，无需验证密码
    - 修改用户名：需提供 current_password 验证身份，且新用户名不能重复
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="数据库不可用")

    nickname = (req.nickname or "").strip() or None
    new_username = (req.new_username or "").strip() or None

    if not nickname and not new_username:
        raise HTTPException(status_code=422, detail="昵称和用户名不能同时为空")

    # 修改用户名时需要验证当前密码
    if new_username:
        if not req.current_password:
            raise HTTPException(status_code=422, detail="修改用户名需要提供当前密码")
        if not verify_password(req.current_password, current_user["password"]):
            raise HTTPException(status_code=401, detail="当前密码不正确")
        if len(new_username) < 3 or len(new_username) > 20:
            raise HTTPException(status_code=422, detail="用户名长度须在 3-20 个字符之间")

    try:
        with engine.begin() as conn:
            if new_username and new_username != current_user["username"]:
                existing = conn.execute(
                    text("SELECT id FROM sys_user WHERE username = :username"),
                    {"username": new_username}
                ).fetchone()
                if existing:
                    raise HTTPException(status_code=409, detail="该用户名已被占用，请更换")

            updates = []
            params = {"id": current_user["id"]}
            if new_username:
                updates.append("username = :username")
                params["username"] = new_username
            if nickname:
                updates.append("nickname = :nickname")
                params["nickname"] = nickname

            conn.execute(
                text(f"UPDATE sys_user SET {', '.join(updates)} WHERE id = :id"),
                params
            )

        return {
            "message": "资料更新成功",
            "username": new_username or current_user["username"],
            "nickname": nickname or current_user["nickname"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"修改资料失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ============================================================================
# 接口6: 修改密码
# ============================================================================

@router.put("/password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """修改密码：验证旧密码后更新为新密码"""
    if engine is None:
        raise HTTPException(status_code=503, detail="数据库不可用")

    if not verify_password(req.old_password, current_user["password"]):
        raise HTTPException(status_code=401, detail="原密码不正确")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=422, detail="新密码长度不能少于 6 个字符")

    if req.old_password == req.new_password:
        raise HTTPException(status_code=422, detail="新密码不能与原密码相同")

    try:
        hashed = pwd_context.hash(req.new_password)
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE sys_user SET password = :password WHERE id = :id"),
                {"password": hashed, "id": current_user["id"]}
            )
        return {"message": "密码修改成功，请重新登录"}
    except Exception as e:
        print(f"修改密码失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ============================================================================
# 用户初始化函数
# ============================================================================

def init_test_users():
    """
    应用启动时初始化测试用户（如果不存在）
    """
    # 需要检查的测试用户列表
    test_users = [
        {
            'username': 'admin',
            'password': 'Admin@123',
            'nickname': '管理员',
            'role': 'admin',
            'is_active': 1
        },
        {
            'username': 'demo',
            'password': 'Demo@123',
            'nickname': '演示用户',
            'role': 'viewer',
            'is_active': 1
        },
        {
            'username': 'viewer',
            'password': 'View@123',
            'nickname': '只读用户',
            'role': 'viewer',
            'is_active': 1
        }
    ]
    
    if engine is None:
        return
    
    try:
        with engine.begin() as conn:
            for user_data in test_users:
                # 检查用户是否存在
                existing = conn.execute(
                    text("SELECT id FROM sys_user WHERE username = :username"),
                    {"username": user_data['username']}
                ).fetchone()
                
                if not existing:
                    # 不存在则插入
                    hashed_password = pwd_context.hash(user_data['password'])
                    conn.execute(
                        text("""INSERT INTO sys_user 
                                (username, password, nickname, role, is_active, created_at) 
                                VALUES (:username, :password, :nickname, :role, :is_active, NOW())"""),
                        {
                            'username': user_data['username'],
                            'password': hashed_password,
                            'nickname': user_data['nickname'],
                            'role': user_data['role'],
                            'is_active': user_data['is_active']
                        }
                    )
                    print(f"✓ 已创建测试用户: {user_data['username']}")
                else:
                    print(f"✓ 测试用户已存在: {user_data['username']}")
    except Exception as e:
        print(f"初始化测试用户失败: {e}")