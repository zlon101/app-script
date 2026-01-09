#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用爬虫高级使用示例
展示回调函数、数据处理等高级功能
"""

import time
from typing import List, Dict, Any
from generic_app_spider import GenericAppSpider
from rich.console import Console

console = Console()


# ==================== 示例1: 使用回调函数 ====================
def example_with_callbacks():
    """演示如何使用回调函数"""
    
    # 解析前的处理
    def before_parse():
        """每次解析前执行"""
        console.print("[dim]准备解析当前页面...[/dim]")
    
    # 解析后的处理
    def after_parse(items: List[Dict[str, Any]]):
        """每次解析后执行"""
        if items:
            console.print(f"[green]✓ 本次获取到 {len(items)} 条新数据[/green]")
            # 可以在这里做实时数据处理
            for item in items[:2]:  # 显示前2条数据
                console.print(f"  - {item}")
    
    config = {
        "app_package": "com.hpbr.bosszhipin",
        "selectors": {
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
            "公司名称": "com.hpbr.bosszhipin:id/tv_company_name"
        },
        "max_items": 50,  # 抓取50条数据
        "scroll_sleep": 2.0,
        "unique_keys": ["职位名称", "公司名称"],
        "output_prefix": "boss_jobs_with_callbacks",
        "title": "带回调的Boss直聘爬虫"
    }
    
    spider = GenericAppSpider(**config)
    spider.run(before_parse=before_parse, after_parse=after_parse)


# ==================== 示例2: 自定义滚动策略 ====================
class CustomScrollSpider(GenericAppSpider):
    """自定义滚动策略的爬虫"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scroll_count = 0
    
    def scroll_page(self) -> None:
        """自定义滚动逻辑"""
        if not self.device:
            return
        
        self.scroll_count += 1
        
        try:
            screen_width, screen_height = self.device.window_size()
            
            # 根据滚动次数调整滚动幅度
            if self.scroll_count % 3 == 0:
                # 每3次做一次大幅度滚动
                start_y = int(screen_height * 0.9)
                end_y = int(screen_height * 0.2)
                console.print("[yellow]执行大幅度滚动...[/yellow]")
            else:
                # 正常滚动
                start_y = int(screen_height * 0.8)
                end_y = int(screen_height * 0.3)
            
            x = int(screen_width / 2)
            self.device.swipe(x, start_y, x, end_y, duration=0.3)
            time.sleep(self.scroll_sleep)
            
        except Exception as e:
            console.print(f"[red]滚动失败: {e}[/red]")


def example_custom_scroll():
    """演示自定义滚动策略"""
    config = {
        "app_package": "com.hpbr.bosszhipin",
        "selectors": {
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue"
        },
        "max_items": 80,  # 抓取80条数据
        "scroll_sleep": 2.0,
        "output_prefix": "boss_custom_scroll",
        "title": "自定义滚动策略爬虫"
    }
    
    spider = CustomScrollSpider(**config)
    spider.run()


# ==================== 示例3: 数据后处理 ====================
def example_data_processing():
    """演示数据获取后的处理"""
    
    config = {
        "app_package": "com.hpbr.bosszhipin",
        "selectors": {
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
            "公司名称": "com.hpbr.bosszhipin:id/tv_company_name"
        },
        "max_items": 50,  # 抓取50条数据
        "scroll_sleep": 2.0,
        "output_prefix": "boss_processed",
        "title": "数据处理示例爬虫"
    }
    
    spider = GenericAppSpider(**config)
    spider.run()
    
    # 获取数据进行处理
    data = spider.get_data()
    
    if data:
        console.print("\n[cyan]== 数据分析 ==[/cyan]")
        
        # 统计薪资分布
        salary_ranges = {}
        for item in data:
            salary = item.get("薪资待遇", "未知")
            salary_ranges[salary] = salary_ranges.get(salary, 0) + 1
        
        console.print("\n[yellow]薪资分布:[/yellow]")
        for salary, count in sorted(salary_ranges.items(), key=lambda x: x[1], reverse=True)[:5]:
            console.print(f"  {salary}: {count} 个职位")
        
        # 统计热门公司
        companies = {}
        for item in data:
            company = item.get("公司名称", "未知")
            companies[company] = companies.get(company, 0) + 1
        
        console.print("\n[yellow]招聘最多的公司 TOP 5:[/yellow]")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
            console.print(f"  {company}: {count} 个职位")


# ==================== 示例4: 最小配置 ====================
def example_minimal_config():
    """最小配置示例 - 只传必需参数"""
    
    spider = GenericAppSpider(
        app_package="com.hpbr.bosszhipin",
        selectors={
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资": "com.hpbr.bosszhipin:id/tv_salary_statue"
        }
        # 其他参数使用默认值（max_items=100）
    )
    
    spider.run()


# ==================== 示例5: 完整配置 ====================
def example_full_config():
    """完整配置示例 - 所有参数都传"""
    
    spider = GenericAppSpider(
        app_package="com.hpbr.bosszhipin",
        selectors={
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
            "公司名称": "com.hpbr.bosszhipin:id/tv_company_name",
            "招聘者": "com.hpbr.bosszhipin:id/tv_employer",
            "公司信息": "com.hpbr.bosszhipin:id/tv_company_industry"
        },
        max_items=150,                                    # 抓取150条数据
        scroll_sleep=3.0,                                # 每次滚动后等待3秒
        unique_keys=["职位名称", "公司名称"],              # 组合去重
        output_prefix="boss_jobs_full",                  # 输出文件前缀
        title="Boss直聘完整配置爬虫",                     # 显示标题
        max_empty_scrolls=5                              # 连续5次无数据停止
    )
    
    spider.run()


# ==================== 示例6: 智能停止 ====================
def example_smart_stop():
    """演示智能停止功能 - 无新数据时自动停止"""
    
    spider = GenericAppSpider(
        app_package="com.hpbr.bosszhipin",
        selectors={
            "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
            "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
            "公司名称": "com.hpbr.bosszhipin:id/tv_company_name"
        },
        max_items=1000,                    # 设置一个很大的值
        scroll_sleep=2.0,
        max_empty_scrolls=3,               # 连续3次无数据就停止
        output_prefix="boss_smart_stop",
        title="智能停止示例"
    )
    
    console.print("\n[cyan]提示: 虽然设置了max_items=1000，但会在连续3次无新数据时自动停止[/cyan]\n")
    spider.run()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("通用爬虫高级使用示例")
    print("=" * 60)
    print("1. 使用回调函数")
    print("2. 自定义滚动策略")
    print("3. 数据后处理")
    print("4. 最小配置")
    print("5. 完整配置")
    print("6. 智能停止（无新数据自动结束）")
    print("=" * 60)
    
    choice = input("\n请选择示例 (1-6): ").strip()
    
    examples = {
        "1": example_with_callbacks,
        "2": example_custom_scroll,
        "3": example_data_processing,
        "4": example_minimal_config,
        "5": example_full_config,
        "6": example_smart_stop
    }
    
    if choice in examples:
        print(f"\n运行示例 {choice}...\n")
        examples[choice]()
    else:
        print("无效的选项！")


if __name__ == "__main__":
    # 运行示例6：智能停止
    example_smart_stop()
    
    # 或者交互式选择
    # main()
