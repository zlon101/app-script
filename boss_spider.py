#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘职位数据爬虫
自动抓取职位列表并保存为JSON文件
"""

import uiautomator2 as u2
import time
import json
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

# 配置参数
APP_PACKAGE = "com.hpbr.bosszhipin"
MAX_PAGES = 10  # 最大滚动次数
SCROLL_SLEEP = 2.5  # 滚动后等待时间（秒）

# Resource ID 定义
SELECTORS = {
    "position_name": "com.hpbr.bosszhipin:id/tv_position_name",
    "salary": "com.hpbr.bosszhipin:id/tv_salary_statue",
    "company_name": "com.hpbr.bosszhipin:id/tv_company_name",
    "employer": "com.hpbr.bosszhipin:id/tv_employer",
    "company_info": "com.hpbr.bosszhipin:id/tv_company_industry"
}


class BossSpider:
    def __init__(self):
        """初始化爬虫"""
        self.device = None
        self.jobs_data = []
        self.seen_jobs = set()  # 用于去重
        
    def connect_device(self):
        """连接USB设备"""
        console.print("[cyan]正在连接设备...[/cyan]")
        try:
            self.device = u2.connect()  # 自动连接第一台设备
            console.print(f"[green]✓ 设备已连接: {self.device.info['productName']}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ 设备连接失败: {e}[/red]")
            return False
    
    def launch_app(self):
        """启动Boss直聘App"""
        console.print(f"[cyan]正在启动 {APP_PACKAGE}...[/cyan]")
        try:
            self.device.app_start(APP_PACKAGE)
            time.sleep(3)  # 等待App启动
            
            # 检查App是否在前台
            current_app = self.device.app_current()
            if current_app['package'] == APP_PACKAGE:
                console.print("[green]✓ App已启动并在前台运行[/green]")
                return True
            else:
                console.print(f"[yellow]⚠ 当前前台App: {current_app['package']}[/yellow]")
                return False
        except Exception as e:
            console.print(f"[red]✗ App启动失败: {e}[/red]")
            return False
    
    def parse_job_item(self):
        """解析当前页面的职位信息"""
        jobs_in_page = []
        
        try:
            # 获取所有职位名称元素
            position_elements = self.device(resourceId=SELECTORS["position_name"])
            
            for i in range(position_elements.count):
                try:
                    job = {}
                    
                    # 职位名称
                    position = position_elements[i].get_text()
                    if not position:
                        continue
                    job["职位名称"] = position
                    
                    # 薪资
                    salary_elements = self.device(resourceId=SELECTORS["salary"])
                    if i < salary_elements.count:
                        job["薪资待遇"] = salary_elements[i].get_text()
                    
                    # 公司名称
                    company_elements = self.device(resourceId=SELECTORS["company_name"])
                    if i < company_elements.count:
                        job["公司名称"] = company_elements[i].get_text()
                    
                    # 招聘者
                    employer_elements = self.device(resourceId=SELECTORS["employer"])
                    if i < employer_elements.count:
                        job["招聘者"] = employer_elements[i].get_text()
                    
                    # 公司信息（规模/融资）
                    info_elements = self.device(resourceId=SELECTORS["company_info"])
                    if i < info_elements.count:
                        job["公司信息"] = info_elements[i].get_text()
                    
                    # 去重检查
                    job_key = f"{job.get('职位名称', '')}_{job.get('公司名称', '')}"
                    if job_key not in self.seen_jobs:
                        self.seen_jobs.add(job_key)
                        jobs_in_page.append(job)
                        
                except Exception as e:
                    console.print(f"[yellow]解析第{i}个职位时出错: {e}[/yellow]")
                    continue
            
        except Exception as e:
            console.print(f"[red]页面解析错误: {e}[/red]")
        
        return jobs_in_page
    
    def scroll_page(self):
        """向上滚动页面"""
        try:
            screen_width = self.device.window_size()[0]
            screen_height = self.device.window_size()[1]
            
            # 从屏幕80%位置向30%位置滑动
            start_y = int(screen_height * 0.8)
            end_y = int(screen_height * 0.3)
            x = int(screen_width / 2)
            
            self.device.swipe(x, start_y, x, end_y, duration=0.3)
            time.sleep(SCROLL_SLEEP)
            
        except Exception as e:
            console.print(f"[red]滚动失败: {e}[/red]")
    
    def save_data(self):
        """保存数据为JSON文件"""
        if not self.jobs_data:
            console.print("[yellow]⚠ 没有数据需要保存[/yellow]")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"boss_jobs_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n[green]✓ 数据已保存: {filename}[/green]")
            console.print(f"[green]  共抓取 {len(self.jobs_data)} 条职位信息[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ 保存失败: {e}[/red]")
    
    def show_statistics(self):
        """显示抓取统计"""
        if not self.jobs_data:
            return
        
        table = Table(title="抓取统计", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", width=20)
        table.add_column("数值", style="green", width=20)
        
        table.add_row("总职位数", str(len(self.jobs_data)))
        table.add_row("去重后职位数", str(len(self.seen_jobs)))
        
        # 统计公司数量
        companies = set(job.get("公司名称", "") for job in self.jobs_data if job.get("公司名称"))
        table.add_row("涉及公司数", str(len(companies)))
        
        console.print(table)
    
    def run(self):
        """主运行函数"""
        console.print(Panel.fit(
            "[bold cyan]Boss直聘职位数据爬虫[/bold cyan]\n"
            "[dim]按 Ctrl+C 随时停止抓取[/dim]",
            border_style="cyan"
        ))
        
        # 连接设备
        if not self.connect_device():
            return
        
        # 启动App
        if not self.launch_app():
            return
        
        console.print(f"\n[cyan]开始抓取，最多滚动 {MAX_PAGES} 次...[/cyan]\n")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("[cyan]正在抓取...", total=MAX_PAGES)
                
                for page in range(MAX_PAGES):
                    # 解析当前页面
                    jobs = self.parse_job_item()
                    
                    if jobs:
                        self.jobs_data.extend(jobs)
                        console.print(f"[green]第 {page + 1} 页: 新增 {len(jobs)} 条职位[/green]")
                    else:
                        console.print(f"[yellow]第 {page + 1} 页: 未获取到新数据[/yellow]")
                    
                    # 滚动到下一页
                    if page < MAX_PAGES - 1:
                        self.scroll_page()
                    
                    progress.update(task, advance=1)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ 用户中断抓取[/yellow]")
        
        except Exception as e:
            console.print(f"\n[red]✗ 抓取过程中出错: {e}[/red]")
        
        finally:
            # 显示统计
            self.show_statistics()
            
            # 保存数据
            self.save_data()


def main():
    """主函数"""
    spider = BossSpider()
    spider.run()


if __name__ == "__main__":
    main()
