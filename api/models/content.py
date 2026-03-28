from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, Enum
from sqlalchemy.sql import func
from api.db.database import Base
import enum


class JobTitle(str, enum.Enum):
    """职位类型"""
    CEO_FOUNDER = "ceo_founder"
    PRODUCT_MANAGER = "product_manager"
    SALES_DIRECTOR = "sales_director"
    MARKETING_LEADER = "marketing_leader"
    TECH_LEAD = "tech_lead"
    HR_DIRECTOR = "hr_director"
    OPERATIONS_MANAGER = "operations_manager"
    CONSULTANT = "consultant"
    FREELANCER = "freelancer"
    OTHER = "other"


class ContentQuality(str, enum.Enum):
    """内容质量等级"""
    NORMAL = "normal"          # 普通：2-3个字段 × 15-25字
    ADVANCED = "advanced"      # 进阶：3-4个字段 × 25-50字
    PROFESSIONAL = "professional"  # 专业：全部字段 × 50-100字（有图片时可缩短）


class OutputFormat(str, enum.Enum):
    """输出格式"""
    TEXT_ONLY = "text_only"    # 纯文字
    WITH_IMAGE = "with_image"  # 一图


class GenerationStatus(str, enum.Enum):
    """内容生成状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentGeneration(Base):
    """内容生成记录模型"""
    __tablename__ = "content_generations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)

    # 新字段：职位、内容质量、输出格式
    job_title = Column(Enum(JobTitle), nullable=False)
    content_quality = Column(Enum(ContentQuality), nullable=False)
    output_format = Column(Enum(OutputFormat), nullable=False)

    # 基础字段
    linkedin_url = Column(Text, nullable=False)
    company_url = Column(Text)
    selected_topic = Column(Text)  # 用户选择或手动输入的主题
    additional_context = Column(Text)

    # 生成结果
    status = Column(Enum(GenerationStatus), default=GenerationStatus.PENDING)
    generated_content = Column(Text)
    generated_images = Column(JSON)
    content_structure = Column(String)  # 使用的内容结构（分类展示型/流程步骤型等）
    target_audience = Column(String)  # 目标受众
    error_message = Column(Text)  # 错误信息

    # 元数据
    is_favorited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<ContentGeneration {self.id} - {self.job_title} - {self.status}>"
