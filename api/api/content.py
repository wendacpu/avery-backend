"""
内容生成 API - 完整的 AI 内容生成系统
工作流：输入主题 → 类型判断 → 资料检索 → 内容生成 → 图片输出
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime
import logging
import asyncio

from api.db.database import get_db
from api.core.config import settings
from api.schemas.content import (
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentResponse,
    ContentUpdateRequest,
    ExtractDataResponse,
)
from api.models.content import ContentGeneration, GenerationStatus

# 导入服务
from api.services import (
    image_generator,
    linkedin_scraper,
    company_scraper
)
from api.services.deep_search import deep_search_service
from api.services.advanced_content_generator import advanced_content_generator
from api.services.topic_recommender import topic_recommender
from api.services.audience_mapper import get_target_audience

logger = logging.getLogger(__name__)
router = APIRouter()

def _extract_image_meta(generated_images):
    if not generated_images or len(generated_images) == 0:
        return {}
    first = generated_images[0]
    if not isinstance(first, dict):
        return {}
    return {
        "image_prompt": first.get("prompt"),
        "research_summary": first.get("research_summary"),
        "infographic_spec": first.get("infographic_spec"),
        "sources": first.get("sources"),
        "style_id": first.get("style_id"),
        "include_charts": first.get("include_charts"),
    }


@router.post("/extract-and-recommend", response_model=ExtractDataResponse)
async def extract_and_recommend(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    提取数据并推荐主题

    用于前端 Step 1 → Step 2 时调用：
    1. 爬取 LinkedIn 资料（含最近3个月帖子）
    2. 爬取公司信息（如有）
    3. 生成3-5个主题推荐
    4. 返回提取的资料和推荐主题
    """
    try:
        logger.info(f"开始提取数据和推荐主题 - LinkedIn: {request.linkedin_url}")

        # 步骤 1: 爬取 LinkedIn 资料（含最近3个月帖子）
        linkedin_profile = None
        if request.linkedin_url:
            try:
                logger.info("爬取 LinkedIn 资料...")
                linkedin_profile = linkedin_scraper.scrape_profile_with_posts(
                    str(request.linkedin_url),
                    months=3  # 获取最近3个月的帖子
                )
            except Exception as e:
                logger.warning(f"LinkedIn 爬取失败: {str(e)}")
                # 即使失败也继续，使用空数据

        # 步骤 2: 爬取公司信息
        company_info = None
        if request.company_url:
            try:
                logger.info("提取公司信息...")
                company_info = company_scraper.scrape_company_info(str(request.company_url))
            except Exception as e:
                logger.warning(f"公司信息提取失败: {str(e)}")

        # 步骤 3: 生成主题推荐
        logger.info("生成主题推荐...")
        recommendations = topic_recommender.generate_recommendations(
            job_title=request.job_title.value,
            linkedin_profile=linkedin_profile or {},
            company_info=company_info or {},
            count=5,
        )

        logger.info(f"生成了 {len(recommendations)} 个主题推荐")

        return ExtractDataResponse(
            linkedin_profile=linkedin_profile,
            company_info=company_info,
            topic_recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"数据提取和推荐失败: {str(e)}")
        # 即使失败也返回空响应，让前端可以继续
        return ExtractDataResponse(
            linkedin_profile=None,
            company_info=None,
            topic_recommendations=[],
        )


async def generate_content_task(
    generation_id: str,
    request: ContentGenerateRequest,
    db: Session
):
    """
    后台任务：完整的内容生成流程

    1. 爬取 LinkedIn 资料（如果提供了 URL）
    2. 爬取公司信息（如果提供了 URL）
    3. 智能判断内容类型
    4. 生成文字内容（使用质量等级提示词）
    5. 生成配图（仅当 output_format == "with_image"）
    6. 更新数据库
    """

    try:
        logger.info(f"开始生成内容: {generation_id}")

        # 获取生成记录
        generation = db.query(ContentGeneration).filter(
            ContentGeneration.id == generation_id
        ).first()

        if not generation:
            logger.error(f"找不到生成记录: {generation_id}")
            return

        # 更新状态为处理中
        generation.status = GenerationStatus.PROCESSING
        db.commit()

        # 步骤 1: 爬取 LinkedIn 资料
        linkedin_profile = None
        if request.linkedin_url:
            try:
                logger.info("爬取 LinkedIn 资料...")
                linkedin_profile = linkedin_scraper.scrape_profile_with_posts(
                    str(request.linkedin_url),
                    months=3  # 获取最近3个月的帖子
                )
                await asyncio.sleep(1)  # 模拟进度
            except Exception as e:
                logger.warning(f"LinkedIn 爬取失败: {str(e)}")

        # 步骤 2: 爬取公司信息
        company_info = None
        if request.company_url:
            try:
                logger.info("提取公司信息...")
                company_info = company_scraper.scrape_company_info(str(request.company_url))
                await asyncio.sleep(1)  # 模拟进度
            except Exception as e:
                logger.warning(f"公司信息提取失败: {str(e)}")

        # 步骤 3: Deep Search（Tavily）
        logger.info("Running deep search...")

        # 使用V2升级版：职位定制的深度查询
        from api.prompts.deep_search_prompts_v2 import get_deep_search_queries

        # 生成专业的深度查询
        queries = get_deep_search_queries(
            job_title=request.job_title.value if request.job_title else None,
            topic=request.selected_topic,
            company_info=company_info
        )

        logger.info(f"使用 {len(queries)} 个专业深度查询")

        deep_search_results = deep_search_service.search(
            topic=request.selected_topic,
            queries=queries,  # 使用定制查询
            max_results_per_query=5
        )

        # 步骤 4: 研究摘要（NotebookLM 风格）- 使用V2升级版
        target_audience = get_target_audience(request.job_title.value) if request.job_title else ""
        include_charts = True if request.include_charts is None else bool(request.include_charts)
        include_charts = include_charts and request.output_format.value == "with_image"

        logger.info("使用V2升级版Research Synthesis（Executive级别）")
        research_summary = advanced_content_generator.synthesize_research_v2(
            topic=request.selected_topic,
            sources=deep_search_results,
            target_audience=target_audience,
            include_charts=include_charts,
            language=request.language,
        )

        # 步骤 5: 生成文字内容（使用V2升级版高级生成器，Executive级别）
        logger.info(f"使用V2升级版生成文字内容（Executive级别）... (language={request.language})")

        # 使用V2版本生成更高密度、更专业的内容
        result = advanced_content_generator.generate_content_v2(
            topic=request.selected_topic,
            job_title=request.job_title.value,
            research_summary=research_summary,
            target_audience=target_audience,
            content_quality=request.content_quality.value,
            language=request.language,
        )

        generated_content = result.get("content", "")
        content_type_cn = result.get("content_type", "清单要点型")
        target_audience = result.get("target_audience", "")
        await asyncio.sleep(2)  # 模拟进度

        # 步骤 6: 生成配图（仅当 output_format == "with_image"）
        image_url = None
        image_prompt = None
        infographic_spec = None
        if request.output_format.value == "with_image":
            logger.info("生成配图（使用V2升级版高密度信息图）...")

            # 生成高密度信息图规范 - 使用V2版本
            infographic_spec = advanced_content_generator.generate_infographic_spec_v2(
                topic=request.selected_topic,
                research_summary=research_summary,
                content_quality=request.content_quality.value,
                include_charts=include_charts,
                style_id=request.style_id,
                language=request.language,
            )

            # 生成图片提示词（反向工程）
            image_prompt = advanced_content_generator.build_infographic_image_prompt(
                spec=infographic_spec,
                style_id=request.style_id,
                include_charts=include_charts,
            )

            # 获取视觉设计文案（从结果中）
            visual_design_specs = result.get("metadata", {}).get("visual_design_specs")

            # 优先使用高密度信息图 prompt
            if image_prompt:
                logger.info("使用高密度信息图 prompt 生成图片")
                image_url = image_generator.generate_image(
                    content=generated_content,
                    topic=request.selected_topic,
                    content_type=content_type_cn,
                    detailed_prompt=image_prompt,
                    content_quality=request.content_quality.value
                )
            elif visual_design_specs:
                # 使用视觉设计文案生成图片
                logger.info("使用视觉设计文案生成图片")
                image_url = image_generator.generate_image(
                    content=generated_content,
                    topic=request.selected_topic,
                    content_type=content_type_cn,
                    visual_design_specs=visual_design_specs,  # 传递视觉设计文案
                    content_quality=request.content_quality.value  # 传递质量等级
                )
            else:
                # 回退到使用图片提示词
                logger.info("使用图片提示词生成图片")
                image_url = image_generator.generate_image(
                    content=generated_content,
                    topic=request.selected_topic,
                    content_type=content_type_cn,
                    detailed_prompt=image_prompt or advanced_content_generator.generate_image_prompt(
                        topic=request.selected_topic,
                        content_type_cn=content_type_cn,
                        content_summary=generated_content[:200] if generated_content else ""
                    ),
                    content_quality=request.content_quality.value  # 传递质量等级
                )
            await asyncio.sleep(1)  # 模拟进度
        else:
            logger.info("纯文字模式，跳过图片生成")

        # 更新生成记录
        generation.generated_content = generated_content
        generation.content_structure = content_type_cn
        generation.target_audience = target_audience

        if image_url:
            generation.generated_images = [{
                "url": image_url,
                "prompt": image_prompt,
                "research_summary": research_summary,
                "infographic_spec": infographic_spec,
                "sources": [{"title": s.get("title", ""), "url": s.get("url", "")} for s in deep_search_results[:8]],
                "style_id": request.style_id,
                "include_charts": include_charts,
            }]

        generation.status = GenerationStatus.COMPLETED
        generation.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(generation)

        logger.info(f"内容生成完成: {generation_id}")

    except Exception as e:
        logger.error(f"内容生成失败: {str(e)}")

        # 更新为失败状态
        try:
            generation = db.query(ContentGeneration).filter(
                ContentGeneration.id == generation_id
            ).first()

            if generation:
                generation.status = GenerationStatus.FAILED
                generation.error_message = str(e)
                generation.completed_at = datetime.utcnow()
                db.commit()
        except:
            pass


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    触发内容生成

    流程：
    1. 接收主题输入
    2. 智能判断内容类型（如果未指定）
    3. 爬取 LinkedIn 和公司资料（如果提供了 URL）
    4. 调用 AI 生成专业内容
    5. 生成高质量配图
    6. 返回生成 ID
    """
    try:
        # 创建生成记录
        generation_id = str(uuid.uuid4())

        content_gen = ContentGeneration(
            id=generation_id,
            user_id="mock-user-123",  # TODO: 从认证获取真实用户 ID
            job_title=request.job_title,
            content_quality=request.content_quality,
            output_format=request.output_format,
            linkedin_url=str(request.linkedin_url),
            company_url=str(request.company_url) if request.company_url else None,
            selected_topic=request.selected_topic,
            additional_context=request.additional_context,
            generated_content=f"Topic: {request.selected_topic}",
            status=GenerationStatus.PENDING,
        )

        db.add(content_gen)
        db.commit()

        # 在后台启动生成任务
        background_tasks.add_task(
            generate_content_task,
            generation_id,
            request,
            db
        )

        return ContentGenerateResponse(
            id=generation_id,
            status=GenerationStatus.PROCESSING,
            message="Content generation started",
            execution_id=generation_id
        )

    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ContentResponse])
async def get_content_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取内容生成历史列表"""
    try:
        # TODO: 从认证获取真实用户 ID
        user_id = "mock-user-123"

        generations = db.query(ContentGeneration).filter(
            ContentGeneration.user_id == user_id
        ).order_by(
            ContentGeneration.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [
            ContentResponse(
                id=str(g.id),
                user_id=g.user_id,
                job_title=g.job_title,
                content_quality=g.content_quality,
                output_format=g.output_format,
                linkedin_url=g.linkedin_url,
                company_url=g.company_url,
                selected_topic=g.selected_topic,
                status=g.status,
                generated_content=g.generated_content,
                image_url=g.generated_images[0]["url"] if g.generated_images and len(g.generated_images) > 0 else None,
                content_structure=g.content_structure,
                target_audience=g.target_audience,
                research_summary=_extract_image_meta(g.generated_images).get("research_summary"),
                image_prompt=_extract_image_meta(g.generated_images).get("image_prompt"),
                infographic_spec=_extract_image_meta(g.generated_images).get("infographic_spec"),
                sources=_extract_image_meta(g.generated_images).get("sources"),
                style_id=_extract_image_meta(g.generated_images).get("style_id"),
                include_charts=_extract_image_meta(g.generated_images).get("include_charts"),
                is_favorited=g.is_favorited,
                created_at=g.created_at,
                completed_at=g.completed_at
            )
            for g in generations
        ]

    except Exception as e:
        logger.error(f"Failed to fetch history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str, db: Session = Depends(get_db)):
    """获取单条内容详情"""
    content = db.query(ContentGeneration).filter(
        ContentGeneration.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    return ContentResponse(
        id=str(content.id),
        user_id=content.user_id,
        job_title=content.job_title,
        content_quality=content.content_quality,
        output_format=content.output_format,
        linkedin_url=content.linkedin_url,
        company_url=content.company_url,
        selected_topic=content.selected_topic,
        status=content.status,
        generated_content=content.generated_content,
        image_url=content.generated_images[0]["url"] if content.generated_images and len(content.generated_images) > 0 else None,
        content_structure=content.content_structure,
        target_audience=content.target_audience,
        research_summary=_extract_image_meta(content.generated_images).get("research_summary"),
        image_prompt=_extract_image_meta(content.generated_images).get("image_prompt"),
        infographic_spec=_extract_image_meta(content.generated_images).get("infographic_spec"),
        sources=_extract_image_meta(content.generated_images).get("sources"),
        style_id=_extract_image_meta(content.generated_images).get("style_id"),
        include_charts=_extract_image_meta(content.generated_images).get("include_charts"),
        is_favorited=content.is_favorited,
        created_at=content.created_at,
        completed_at=content.completed_at
    )


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    request: ContentUpdateRequest,
    db: Session = Depends(get_db)
):
    """编辑生成的内容"""
    content = db.query(ContentGeneration).filter(
        ContentGeneration.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    content.generated_content = request.generated_content
    db.commit()
    db.refresh(content)

    return ContentResponse(
        id=str(content.id),
        user_id=content.user_id,
        job_title=content.job_title,
        content_quality=content.content_quality,
        output_format=content.output_format,
        linkedin_url=content.linkedin_url,
        company_url=content.company_url,
        selected_topic=content.selected_topic,
        status=content.status,
        generated_content=content.generated_content,
        image_url=content.generated_images[0]["url"] if content.generated_images and len(content.generated_images) > 0 else None,
        content_structure=content.content_structure,
        target_audience=content.target_audience,
        research_summary=_extract_image_meta(content.generated_images).get("research_summary"),
        image_prompt=_extract_image_meta(content.generated_images).get("image_prompt"),
        infographic_spec=_extract_image_meta(content.generated_images).get("infographic_spec"),
        sources=_extract_image_meta(content.generated_images).get("sources"),
        style_id=_extract_image_meta(content.generated_images).get("style_id"),
        include_charts=_extract_image_meta(content.generated_images).get("include_charts"),
        is_favorited=content.is_favorited,
        created_at=content.created_at,
        completed_at=content.completed_at
    )


@router.post("/{content_id}/favorite", response_model=ContentResponse)
async def toggle_favorite(content_id: str, db: Session = Depends(get_db)):
    """切换收藏状态"""
    content = db.query(ContentGeneration).filter(
        ContentGeneration.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    content.is_favorited = not content.is_favorited
    db.commit()
    db.refresh(content)

    return ContentResponse(
        id=str(content.id),
        user_id=content.user_id,
        job_title=content.job_title,
        content_quality=content.content_quality,
        output_format=content.output_format,
        linkedin_url=content.linkedin_url,
        company_url=content.company_url,
        selected_topic=content.selected_topic,
        status=content.status,
        generated_content=content.generated_content,
        image_url=content.generated_images[0]["url"] if content.generated_images and len(content.generated_images) > 0 else None,
        content_structure=content.content_structure,
        target_audience=content.target_audience,
        research_summary=_extract_image_meta(content.generated_images).get("research_summary"),
        image_prompt=_extract_image_meta(content.generated_images).get("image_prompt"),
        infographic_spec=_extract_image_meta(content.generated_images).get("infographic_spec"),
        sources=_extract_image_meta(content.generated_images).get("sources"),
        style_id=_extract_image_meta(content.generated_images).get("style_id"),
        include_charts=_extract_image_meta(content.generated_images).get("include_charts"),
        is_favorited=content.is_favorited,
        created_at=content.created_at,
        completed_at=content.completed_at
    )


@router.delete("/{content_id}")
async def delete_content(content_id: str, db: Session = Depends(get_db)):
    """删除内容"""
    content = db.query(ContentGeneration).filter(
        ContentGeneration.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    db.delete(content)
    return {"message": "Content deleted successfully"}


@router.post("/{content_id}/regenerate", response_model=ContentGenerateResponse)
async def regenerate_content(
    content_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    使用相同参数重新生成内容（文字+图片）
    保留原设置但生成新的内容
    """
    # 获取原内容记录
    original_content = db.query(ContentGeneration).filter(
        ContentGeneration.id == content_id
    ).first()

    if not original_content:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    try:
        # 使用原主题或从生成内容中提取
        topic = original_content.selected_topic or (
            original_content.generated_content.split('\n')[0][:100]
            if original_content.generated_content else "Regenerated Content"
        )

        # 创建新的生成记录
        new_generation_id = str(uuid.uuid4())

        # 构建请求对象（复用原设置）
        from api.schemas.content import ContentGenerateRequest
        request = ContentGenerateRequest(
            linkedin_url=original_content.linkedin_url,
            company_url=original_content.company_url,
            job_title=original_content.job_title,
            content_quality=original_content.content_quality,
            output_format=original_content.output_format,
            selected_topic=topic,
            additional_context=original_content.additional_context
        )

        content_gen = ContentGeneration(
            id=new_generation_id,
            user_id=original_content.user_id,
            job_title=request.job_title,
            content_quality=request.content_quality,
            output_format=request.output_format,
            linkedin_url=request.linkedin_url,
            company_url=request.company_url,
            selected_topic=request.selected_topic,
            additional_context=request.additional_context,
            generated_content=f"Regenerating from: {content_id}",
            status=GenerationStatus.PENDING,
        )

        db.add(content_gen)
        db.commit()

        # 在后台启动生成任务
        background_tasks.add_task(
            generate_content_task,
            new_generation_id,
            request,
            db
        )

        return ContentGenerateResponse(
            id=new_generation_id,
            status=GenerationStatus.PROCESSING,
            message="Content regeneration started",
            execution_id=new_generation_id
        )

    except Exception as e:
        logger.error(f"Content regeneration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
