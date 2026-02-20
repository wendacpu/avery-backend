"""
受众映射服务
根据用户职位自动推断LinkedIn内容的目标受众
"""

from typing import Dict, Optional

# 职位到目标受众的映射
AUDIENCE_MAPPING = {
    "ceo_founder": "创业者、投资人、企业决策者",
    "product_manager": "产品从业者、互联网从业者、PM社群",
    "sales_director": "销售团队、B2B从业者、企业主、销售管理者",
    "marketing_leader": "营销人员、增长黑客、市场从业者",
    "tech_lead": "技术管理者、开发者、CTO、技术团队",
    "hr_director": "HR从业者、企业管理者、人力资源团队",
    "operations_manager": "运营人员、增长团队、企业管理者",
    "consultant": "企业主、高管、决策者、管理团队",
    "freelancer": "自由职业者、独立工作者、SOHO一族",
    "other": None,  # 需要AI判断
}


def get_target_audience(job_title: str, custom_title: Optional[str] = None) -> str:
    """
    获取目标受众

    Args:
        job_title: 职位类型代码
        custom_title: 如果职位是"other"，使用自定义职位描述进行AI判断

    Returns:
        目标受众描述
    """
    # 如果有自定义职位，使用映射的职位
    if job_title == "other" and custom_title:
        # 可以基于自定义职位进行AI判断（这里暂时返回通用受众）
        return "行业从业者、专业人士、决策者"

    # 直接从映射表获取
    audience = AUDIENCE_MAPPING.get(job_title)

    if audience:
        return audience

    # 默认返回通用受众
    return "行业从业者、专业人士"


def get_audience_by_custom_title(custom_title: str) -> str:
    """
    基于自定义职位描述推断目标受众

    Args:
        custom_title: 自定义职位描述，如"高级软件工程师"

    Returns:
        推断的目标受众
    """
    # 关键词映射
    keyword_mapping = {
        # 技术相关
        "engineer": "技术团队、开发者、CTO",
        "developer": "开发者、程序员、技术团队",
        "cto": "CTO、技术管理者、开发者",

        # 产品相关
        "product": "产品从业者、PM、互联网团队",

        # 设计相关
        "designer": "设计师、创意团队、产品团队",
        "ux": "UX从业者、产品团队、设计师",
        "ui": "UI从业者、设计师、前端开发者",

        # 销售相关
        "sales": "销售团队、B2B从业者、业务团队",
        "business": "企业主、创业者、管理者",

        # 市场相关
        "marketing": "营销人员、增长团队、市场从业者",
        "growth": "增长团队、运营人员、创业者",

        # 管理相关
        "manager": "管理者、团队负责人、企业主",
        "director": "高管、决策者、管理者",
        "vp": "高管、决策者、管理者",
    }

    custom_title_lower = custom_title.lower()

    # 匹配关键词
    for keyword, audience in keyword_mapping.items():
        if keyword in custom_title_lower:
            return audience

    # 默认返回通用受众
    return "行业从业者、专业人士"


def get_all_job_titles() -> Dict[str, str]:
    """
    获取所有职位选项

    Returns:
        职位代码到名称的映射
    """
    return {
        "ceo_founder": "CEO / 创始人",
        "product_manager": "产品经理",
        "sales_director": "销售总监 / Sales VP",
        "marketing_leader": "市场营销负责人",
        "tech_lead": "技术负责人 / CTO",
        "hr_director": "HR总监",
        "operations_manager": "运营经理",
        "consultant": "顾问 / 咨询师",
        "freelancer": "自由职业者",
        "other": "其他",
    }
