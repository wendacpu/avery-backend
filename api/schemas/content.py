from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from api.models.content import JobTitle, ContentQuality, OutputFormat, GenerationStatus


class ContentGenerateRequest(BaseModel):
    """内容生成请求 Schema"""
    linkedin_url: str  # LinkedIn URL（必选）
    company_url: Optional[str] = None  # 公司网站 URL（可选）
    job_title: JobTitle  # 职位（必选）
    content_quality: ContentQuality  # 内容质量（必选）
    output_format: OutputFormat  # 输出格式（必选）
    selected_topic: str  # 用户选择或手动输入的主题
    additional_context: Optional[str] = None  # 额外补充信息
    language: str = "en"  # 语言：en=英文, zh=中文，默认英文
    include_charts: Optional[bool] = True  # 是否生成图表
    style_id: Optional[str] = None  # 视觉风格ID

    @field_validator('company_url', mode='before')
    @classmethod
    def empty_str_to_none(cls, v: Optional[str]) -> Optional[str]:
        """将空字符串转换为 None"""
        if v is None or v.strip() == "":
            return None
        return v


class ContentGenerateResponse(BaseModel):
    """内容生成响应 Schema"""
    id: str
    status: GenerationStatus
    message: str
    execution_id: Optional[str] = None


class ContentResponse(BaseModel):
    """内容响应 Schema"""
    id: str
    user_id: str
    job_title: JobTitle
    content_quality: ContentQuality
    output_format: OutputFormat
    linkedin_url: Optional[str] = None
    company_url: Optional[str] = None
    selected_topic: Optional[str] = None
    status: GenerationStatus
    generated_content: Optional[str] = None
    image_url: Optional[str] = None  # 单个高质量图片
    content_structure: Optional[str] = None  # 使用的内容结构
    target_audience: Optional[str] = None  # 目标受众
    research_summary: Optional[Dict[str, Any]] = None
    image_prompt: Optional[str] = None
    infographic_spec: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    style_id: Optional[str] = None
    include_charts: Optional[bool] = None
    is_favorited: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContentUpdateRequest(BaseModel):
    """内容更新请求 Schema"""
    generated_content: str


class TopicRecommendation(BaseModel):
    """主题推荐 Schema"""
    topic: str
    source: str  # 'hot_topic' | 'historical' | 'industry_trend'
    reason: str
    estimated_engagement: Optional[int] = None  # 预估互动度


class LinkedInValidateRequest(BaseModel):
    """LinkedIn URL 验证请求"""
    url: HttpUrl


class ExtractDataResponse(BaseModel):
    """数据提取响应 Schema"""
    linkedin_profile: Optional[Dict[str, Any]] = None
    company_info: Optional[Dict[str, Any]] = None
    topic_recommendations: List[TopicRecommendation]
