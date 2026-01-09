#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Android App 数据爬虫
可配置化的自动化数据抓取框架
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
    
    支持自定义配置，适用于各种 Android App 的数据抓取
    """
    
    def __init__(
        self,
        app_package: str,
        selectors: Dict[str, str],
        max_items: int = 100,
        scroll_sleep: float = 2.5,
        unique_keys: Optional[List[str]] = None,
        output_prefix: str = "data",
        title: str = "通用数据爬虫",
        max_empty_scrolls: int = 3,
        container_selector: Optional[str] = None
    ):
        """
        初始化爬虫
        
        Args:
            app_package: App包名，如 "com.hpbr.bosszhipin"
            selectors: 字段选择器映射，key为中文字段名，value为resourceId
                      例如: {"职位名称": "com.xxx:id/tv_name"}
            max_items: 最大数据条数，默认100
            scroll_sleep: 滚动后等待时间（秒），默认2.5
            unique_keys: 用于去重的字段列表，默认使用第一个字段
            output_prefix: 输出文件名前缀，默认"data"
            title: 爬虫标题，用于显示
            max_empty_scrolls: 连续多少次无新数据时停止，默认3次
            container_selector: 列表项容器的resourceId（可选）
                               例如: "com.xxx:id/item_container"
                               配置后将使用更稳定的容器解析方案
        """
        self.app_package = app_package
        self.selectors = selectors
        self.max_items = max_items
        self.scroll_sleep = scroll_sleep
        self.output_prefix = output_prefix
        self.title = title
        self.max_empty_scrolls = max_empty_scrolls
        self.container_selector = container_selector
        
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
    
    def _parse_items_with_container(self) -> List[Dict[str, Any]]:
        """
        基于容器的解析方案（方案1）
        
        优点:
        - 最准确: 利用 UI 层次结构，确保字段关联性
        - 最稳定: 不依赖索引对齐
        - 适用场景: ListView/RecyclerView 等有容器的列表
        
        Returns:
            数据项列表
        """
        items_in_page: List[Dict[str, Any]] = []
        if not self.device or not self.container_selector:
            return items_in_page
        
        try:
            # 查找所有容器
            containers = self.device(resourceId=self.container_selector)
            container_count = containers.count
            
            if container_count == 0:
                console.print("[yellow]⚠ 未找到容器元素，将回退到索引方案[/yellow]")
                return self._parse_items_with_index()
            
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
    
    def _parse_items_with_index(self) -> List[Dict[str, Any]]:
        """
        基于索引的增强解析方案（方案2）
        
        优点:
        - 无需容器配置
        - 添加了验证和边界检查
        - 性能优化（预查询）
        
        Returns:
            数据项列表
        """
        items_in_page: List[Dict[str, Any]] = []
        if not self.device:
            return items_in_page
        
        try:
            # 步骤1: 预先查询所有字段的元素（性能优化）
            field_elements: Dict[str, Any] = {}
            element_counts: Dict[str, int] = {}
            
            for field_name, resource_id in self.selectors.items():
                try:
                    elements = self.device(resourceId=resource_id)
                    field_elements[field_name] = elements
                    element_counts[field_name] = elements.count
                except Exception as e:
                    console.print(f"[yellow]⚠ 获取字段 '{field_name}' 失败: {e}[/yellow]")
                    field_elements[field_name] = None
                    element_counts[field_name] = 0
            
            # 步骤2: 验证是否有有效元素
            if not element_counts or max(element_counts.values()) == 0:
                return items_in_page
            
            # 步骤3: 检查元素数量一致性
            first_field = list(self.selectors.keys())[0]
            primary_count = element_counts.get(first_field, 0)
            
            if primary_count == 0:
                console.print("[yellow]⚠ 未找到主字段元素[/yellow]")
                return items_in_page
            
            # 警告：如果字段数量不一致
            unique_counts = set(element_counts.values())
            if len(unique_counts) > 1:
                console.print(
                    f"[yellow]⚠ 字段元素数量不一致: {element_counts}\n"
                    f"   将按最小数量 {min(element_counts.values())} 解析，可能导致数据不完整[/yellow]"
                )
            
            # 步骤4: 按最小数量遍历
            safe_count = min(element_counts.values())
            
            # 步骤5: 遍历并组装数据
            for i in range(safe_count):
                try:
                    item: Dict[str, Any] = {}
                    has_valid_data = False
                    
                    # 获取所有字段
                    for field_name, elements in field_elements.items():
                        if elements is None:
                            item[field_name] = ""
                            continue
                        
                        try:
                            if i < elements.count:
                                text = elements[i].get_text()
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
                    
                    # 只添加有效数据
                    if has_valid_data:
                        item_key = self._generate_unique_key(item)
                        if item_key and item_key not in self.seen_items:
                            self.seen_items.add(item_key)
                            items_in_page.append(item)
                        
                except Exception as e:
                    console.print(f"[yellow]解析第{i}个项目时出错: {e}[/yellow]")
                    continue
            
        except Exception as e:
            console.print(f"[red]页面解析错误: {e}[/red]")
        
        return items_in_page
    
    def parse_items(self) -> List[Dict[str, Any]]:
        """
        解析当前页面的数据项（智能选择策略）
        
        解析策略:
        1. 如果配置了 container_selector -> 使用容器方案（最准确）
        2. 否则 -> 使用增强索引方案（升级版）
        
        Returns:
            数据项列表
        """
        if not self.device:
            return []
        
        # 智能选择解析策略
        if self.container_selector:
            # 方案1：基于容器解析（最稳定）
            console.print("[dim]使用容器解析方案[/dim]")
            return self._parse_items_with_container()
        else:
            # 方案2：基于索引增强解析
            console.print("[dim]使用索引增强解析方案[/dim]")
            return self._parse_items_with_index()
    
    def scroll_page(self) -> None:
        """向上滚动页面"""
        if not self.device:
            return
        
        try:
            screen_width, screen_height = self.device.window_size()

            # 从屏幕90%位置向20%位置滑动，差值约大滚动距离越大
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
