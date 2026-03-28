from sqlalchemy import Column, String, DateTime, Text, JSON, Integer
from sqlalchemy.sql import func
from api.db.database import Base


class InfographicGeneration(Base):
    """Infographic生成记录模型"""
    __tablename__ = "infographic_generations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Associated user

    # 输入参数
    input_content = Column(Text, nullable=False)  # 用户输入的内容
    input_type = Column(String, default="text")  # text, url, file
    job_title = Column(String, nullable=False)  # cto, ceo, hybrid
    perspective = Column(String, nullable=False)  # cto, ceo, hybrid
    framework = Column(String, default="how-to")  # how-to, listicle, comparison

    # 生成结果
    status = Column(String, default="pending")  # pending, completed, failed
    generated_count = Column(Integer, default=0)  # 成功生成的数量
    results = Column(JSON)  # 存储所有生成结果

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<InfographicGeneration {self.id} - {self.status} - {self.generated_count} images>"
