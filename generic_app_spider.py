#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Android App 数据爬虫
可配置化的自动化数据抓取框架 - 基于容器解析
"""

import uiautomator2 as u2
import time
import json
from datetime import datetime
from typing import Any, Dict, List, Set, Optional, Callable

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel

console = Console()


class GenericAppSpider:
    """
    通用 App 爬虫类
    
    基于容器解析方案，利用UI层次结构确保数据准确性
    """
    
    def __init__(
        self,
        app_package: str,
        container_selector: str,
        selectors: Dict[str, str],
        max_items: int = 100,
        scroll_sleep: float = 2.5,
        unique_keys: Optional[List[str]] = None,
        output_prefix: str = "data",
        title: str = "通用数据爬虫",
        max_empty_scrolls: int = 3
    ):
        """
        初始化爬虫
        
        Args:
            app_package: App包名，如 "com.hpbr.bosszhipin"
            container_selector: 列表项容器的resourceId（必需）
                               例如: "com.hpbr.bosszhipin:id/job_item_layout"
                               通过 weditor 工具可以找到容器的resource-id
            selectors: 字段选择器映射，key为中文字段名，value为resourceId
                      例如: {"职位名称": "com.xxx:id/tv_name"}
            max_items: 最大数据条数，默认100
            scroll_sleep: 滚动后等待时间（秒），默认2.5
            unique_keys: 用于去重的字段列表，默认使用第一个字段
            output_prefix: 输出文件名前缀，默认"data"
            title: 爬虫标题，用于显示
            max_empty_scrolls: 连续多少次无新数据时停止，默认3次
        """
        self.app_package = app_package
        self.container_selector = container_selector
        self.selectors = selectors
        self.max_items = max_items
        self.scroll_sleep = scroll_sleep
        self.output_prefix = output_prefix
        self.title = title
        self.max_empty_scrolls = max_empty_scrolls
        
        # 去重字段配置
        if unique_keys:
            self.unique_keys = unique_keys
        else:
            # 默认使用第一个字段作为去重键
            self.unique_keys = [list(selectors.keys())[0]] if selectors else []
        
        # 运行时数据
        self.device: Optional[u2.Device] = None
        self.data_list: List[Dict[str, Any]] = []
        self.seen_items: Set[str] = set()
        
        # 获取主字段名（用于统计）
        self.primary_field = list(selectors.keys())[0] if selectors else "数据"
    
    def connect_device(self) -> bool:
        """连接USB设备"""
        console.print("[cyan]正在连接设备...[/cyan]")
        try:
            self.device = u2.connect()
            if self.device:
                device_name = self.device.info.get('productName', '未知设备')
                console.print(f"[green]✓ 设备已连接: {device_name}[/green]")
                return True
            else:
                console.print("[red]✗ 未找到设备[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ 设备连接失败: {e}[/red]")
            return False
    
    def launch_app(self) -> bool:
        """启动目标App"""
        console.print(f"[cyan]正在启动 {self.app_package}...[/cyan]")
        if not self.device:
            console.print("[red]✗ 设备未连接，无法启动App[/red]")
            return False
        
        try:
            self.device.app_start(self.app_package)
            time.sleep(3)  # 等待App启动
            
            # 检查App是否在前台
            current_app = self.device.app_current()
            if current_app and current_app.get('package') == self.app_package:
                console.print("[green]✓ App已启动并在前台运行[/green]")
                return True
            else:
                current_package = current_app.get('package') if current_app else '无'
                console.print(f"[yellow]⚠ 当前前台App: {current_package}[/yellow]")
                return False
        except Exception as e:
            console.print(f"[red]✗ App启动失败: {e}[/red]")
            return False
    
    def _generate_unique_key(self, item: Dict[str, Any]) -> str:
        """
        根据配置的字段生成唯一键
        
        Args:
            item: 数据项
            
        Returns:
            唯一键字符串
        """
        key_parts = [str(item.get(field, '')) for field in self.unique_keys]
        return "_".join(key_parts)
    
    def parse_items(self) -> List[Dict[str, Any]]:
        """
        基于容器的解析方案
        
        原理:
        1. 查找所有列表项容器（通过 container_selector）
        2. 在每个容器内查找子元素（利用 UI 层次结构）
        3. 确保每个容器内的字段属于同一条数据
        
        优点:
        - 最准确: 利用 UI 层次结构，字段关联性100%正确
        - 最稳定: 不依赖索引对齐，不受元素数量影响
        - 零错配: 每个容器内的字段必然属于同一条数据
        - 支持复杂布局: 即使字段分布不规则也能正确解析
        
        Returns:
            数据项列表
        """
        items_in_page: List[Dict[str, Any]] = []
        if not self.device:
            return items_in_page
        
        try:
            # 查找所有容器
            containers = self.device(resourceId=self.container_selector)
            container_count = containers.count
            
            if container_count == 0:
                console.print("[yellow]⚠ 未找到容器元素，请检查 container_selector 配置[/yellow]")
                console.print(f"[yellow]   配置的容器: {self.container_selector}[/yellow]")
                return items_in_page
            
            console.print(f"[dim]找到 {container_count} 个容器[/dim]")
            
            # 遍历每个容器
            for i in range(container_count):
                try:
                    container = containers[i]
                    item: Dict[str, Any] = {}
                    has_valid_data = False
                    
                    # 在容器内查找各个字段
                    for field_name, resource_id in self.selectors.items():
                        try:
                            # 在容器内查找元素（关键：child 方法）
                            element = container.child(resourceId=resource_id)
                            if element.exists:
                                text = element.get_text()
                                if text and text.strip():
                                    item[field_name] = text.strip()
                                    has_valid_data = True
                                else:
                                    item[field_name] = ""
                            else:
                                item[field_name] = ""
                        except Exception as e:
                            item[field_name] = ""
                            continue
                    
                    # 只有至少有一个有效字段才添加
                    if has_valid_data:
                        # 去重检查
                        item_key = self._generate_unique_key(item)
                        if item_key and item_key not in self.seen_items:
                            self.seen_items.add(item_key)
                            items_in_page.append(item)
                            
                except Exception as e:
                    console.print(f"[yellow]解析第{i}个容器时出错: {e}[/yellow]")
                    continue
            
        except Exception as e:
            console.print(f"[red]容器解析错误: {e}[/red]")
        
        return items_in_page
    
    def scroll_page(self) -> None:
        """向上滚动页面"""
        if not self.device:
            return
        
        try:
            screen_width, screen_height = self.device.window_size()
            
            # 从屏幕90%位置向20%位置滑动
            start_y = int(screen_height * 0.9)
            end_y = int(screen_height * 0.2)
            x = int(screen_width / 2)
            
            self.device.swipe(x, start_y, x, end_y, duration=0.3)
            time.sleep(self.scroll_sleep)
            
        except Exception as e:
            console.print(f"[red]滚动失败: {e}[/red]")
    
    def save_data(self, filename: Optional[str] = None) -> None:
        """
        保存数据为JSON文件
        
        Args:
            filename: 自定义文件名，不传则自动生成
        """
        if not self.data_list:
            console.print("[yellow]⚠ 没有数据需要保存[/yellow]")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_prefix}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data_list, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n[green]✓ 数据已保存: {filename}[/green]")
            console.print(f"[green]  共抓取 {len(self.data_list)} 条数据[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ 保存失败: {e}[/red]")
    
    def show_statistics(self) -> None:
        """显示抓取统计"""
        if not self.data_list:
            return
        
        table = Table(title="抓取统计", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", width=20)
        table.add_column("数值", style="green", width=20)
        
        table.add_row(f"总{self.primary_field}数", str(len(self.data_list)))
        table.add_row("去重后数量", str(len(self.seen_items)))
        
        # 如果有多个去重字段，显示每个字段的唯一值数量
        for field in self.unique_keys:
            if field in self.selectors:
                unique_values = set(
                    item.get(field, "") 
                    for item in self.data_list 
                    if item.get(field)
                )
                if unique_values:
                    table.add_row(f"不同{field}数", str(len(unique_values)))
        
        console.print(table)
    
    def run(
        self, 
        before_parse: Optional[Callable] = None,
        after_parse: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ) -> None:
        """
        主运行函数
        
        Args:
            before_parse: 每次解析前的回调函数
            after_parse: 每次解析后的回调函数，接收解析结果
        """
        console.print(Panel.fit(
            f"[bold cyan]{self.title}[/bold cyan]\n"
            "[dim]使用容器解析方案 - 数据准确性100%[/dim]\n"
            "[dim]按 Ctrl+C 随时停止抓取[/dim]",
            border_style="cyan"
        ))
        
        # 连接设备
        if not self.connect_device():
            return
        
        # 启动App
        if not self.launch_app():
            return
        
        console.print(f"\n[cyan]开始抓取，目标数据量: {self.max_items} 条...[/cyan]\n")
        
        # 用于检测是否还有新数据
        empty_scroll_count = 0
        scroll_count = 0
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                
                task = progress.add_task(
                    f"[cyan]正在抓取... (0/{self.max_items})",
                    total=self.max_items
                )
                
                while len(self.data_list) < self.max_items:
                    scroll_count += 1
                    
                    # 解析前回调
                    if before_parse:
                        before_parse()
                    
                    # 解析当前页面
                    items = self.parse_items()
                    
                    # 解析后回调
                    if after_parse:
                        after_parse(items)
                    
                    if items:
                        self.data_list.extend(items)
                        empty_scroll_count = 0  # 重置空滚动计数
                        
                        # 更新进度
                        current_count = len(self.data_list)
                        progress.update(
                            task,
                            completed=min(current_count, self.max_items),
                            description=f"[cyan]正在抓取... ({current_count}/{self.max_items})"
                        )
                        
                        console.print(
                            f"[green]第 {scroll_count} 次滚动: 新增 {len(items)} 条，"
                            f"累计 {current_count} 条[/green]"
                        )
                        
                        # 达到目标数量
                        if current_count >= self.max_items:
                            console.print(f"\n[green]✓ 已达到目标数据量 {self.max_items} 条[/green]")
                            break
                    else:
                        empty_scroll_count += 1
                        console.print(
                            f"[yellow]第 {scroll_count} 次滚动: 未获取到新数据 "
                            f"({empty_scroll_count}/{self.max_empty_scrolls})[/yellow]"
                        )
                        
                        # 连续多次无新数据，认为已到底部
                        if empty_scroll_count >= self.max_empty_scrolls:
                            console.print(
                                f"\n[yellow]⚠ 连续 {self.max_empty_scrolls} 次无新数据，"
                                f"已到达列表底部[/yellow]"
                            )
                            break
                    
                    # 滚动到下一页
                    self.scroll_page()
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ 用户中断抓取[/yellow]")
        
        except Exception as e:
            console.print(f"\n[red]✗ 抓取过程中出错: {e}[/red]")
        
        finally:
            # 显示统计
            self.show_statistics()
            
            # 保存数据
            self.save_data()
    
    def get_data(self) -> List[Dict[str, Any]]:
        """
        获取已抓取的数据
        
        Returns:
            数据列表
        """
        return self.data_list
