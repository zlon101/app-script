#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘职位数据爬虫 - 使用通用爬虫类的示例
"""

from generic_app_spider import GenericAppSpider

# Boss直聘配置
BOSS_CONFIG = {
    "app_package": "com.hpbr.bosszhipin",
    "selectors": {
        "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
        "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
        "公司名称": "com.hpbr.bosszhipin:id/tv_company_name",
        "地址": "com.hpbr.bosszhipin:id/tv_distance",
        "活跃度": "com.hpbr.bosszhipin:id/tv_active_status"
    },
    "max_items": 10,  # 最多抓取100条数据
    "scroll_sleep": 2.5,
    "unique_keys": ["职位名称", "公司名称"],  # 使用职位名+公司名去重
    "output_prefix": "test_boss_jobs",
    "title": "Boss直聘职位数据爬虫",
    "container_selector": "com.hpbr.bosszhipin:id/cl_card_container",  # 容器选择器
}


def main():
    """主函数"""
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
