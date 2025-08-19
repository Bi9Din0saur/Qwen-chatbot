from sqlalchemy.orm import Session
from .database import engine
from ..models import Base
from ..services.auth import get_password_hash
from ..models.user import User

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库表创建完成")

def create_initial_data(db: Session):
    """创建初始数据"""
    # 检查是否已有用户
    existing_user = db.query(User).filter(User.username == "admin").first()
    if not existing_user:
        # 创建默认管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("123456")
        )
        db.add(admin_user)
        db.commit()
        print("默认用户创建完成: admin/123456")
    else:
        print("默认用户已存在")

if __name__ == "__main__":
    init_db()
    from .database import SessionLocal
    db = SessionLocal()
    try:
        create_initial_data(db)
    finally:
        db.close()
