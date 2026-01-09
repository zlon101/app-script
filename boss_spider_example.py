#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘职位数据爬虫 - 基于容器解析方案
"""

from generic_app_spider import GenericAppSpider

# Boss直聘配置
BOSS_CONFIG = {
    "app_package": "com.hpbr.bosszhipin",
    "container_selector": "com.hpbr.bosszhipin:id/job_item_layout",  # 容器选择器（必需）
    "selectors": {
        "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
        "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
        "公司名称": "com.hpbr.bosszhipin:id/tv_company_name",
        "招聘者": "com.hpbr.bosszhipin:id/tv_employer",
        "公司信息": "com.hpbr.bosszhipin:id/tv_company_industry"
    },
    "max_items": 100,
    "scroll_sleep": 2.5,
    "unique_keys": ["职位名称", "公司名称"],
    "output_prefix": "boss_jobs",
    "title": "Boss直聘职位数据爬虫"
}


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Boss直聘职位数据爬虫")
    print("=" * 60)
    print("使用容器解析方案 - 数据准确性100%")
    print("=" * 60)
    print()
    print("提示:")
    print("1. 如果首次使用，请先用 weditor 工具找到容器的 resourceId")
    print("2. 运行命令: python -m weditor")
    print("3. 访问 http://localhost:17310 查看页面结构")
    print("4. 找到包含所有字段的父容器")
    print()
    print("=" * 60 + "\n")
    
    # 创建爬虫实例
    spider = GenericAppSpider(
        app_package=BOSS_CONFIG["app_package"],
        container_selector=BOSS_CONFIG["container_selector"],
        selectors=BOSS_CONFIG["selectors"],
        max_items=BOSS_CONFIG["max_items"],
        scroll_sleep=BOSS_CONFIG["scroll_sleep"],
        unique_keys=BOSS_CONFIG["unique_keys"],
        output_prefix=BOSS_CONFIG["output_prefix"],
        title=BOSS_CONFIG["title"]
    )
    
    # 运行爬虫
    spider.run()
    
    # 如果需要获取数据进行后续处理
    # data = spider.get_data()
    # print(f"获取到 {len(data)} 条数据")


if __name__ == "__main__":
    main()
