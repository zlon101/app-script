# Boss直聘职位数据爬虫

自动化抓取 Boss直聘 App 的职位列表数据。

## 环境要求

- Python 3.7+
- MacOS 系统
- Android 设备（通过 USB 连接）
- ADB 工具已配置

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. **连接设备**: 确保 Android 设备通过 USB 连接到电脑，并开启 USB 调试
2. **打开 Boss直聘**: 建议先手动打开 App 并进入职位列表页面
3. **运行脚本**:
```bash
python boss_spider.py
```

## 功能特性

- ✅ 自动连接 USB 设备
- ✅ 自动启动 Boss直聘 App
- ✅ 智能去重（根据职位名+公司名）
- ✅ 自动滚动加载更多职位
- ✅ 美化的终端输出
- ✅ 支持 Ctrl+C 随时中断
- ✅ 数据自动保存为 JSON 文件

## 抓取数据字段

- 职位名称
- 薪资待遇
- 公司名称
- 招聘者/HR
- 公司信息（规模/融资）

## 配置说明

可在 `boss_spider.py` 中修改以下参数：

```python
MAX_PAGES = 10  # 最大滚动次数
SCROLL_SLEEP = 2.5  # 滚动后等待时间（秒）
```

## 输出文件

数据会保存为 `boss_jobs_[时间戳].json` 格式，例如：
- `boss_jobs_20250108_143052.json`

## 注意事项

- 首次使用需要在手机上授权 uiautomator2 的权限
- 请确保在职位列表页面运行脚本
- 滚动速度不宜过快，避免触发 App 的反爬机制
- 建议抓取时保持屏幕常亮

## 故障排查

**问题**: 设备连接失败
- 检查 USB 线是否连接正常
- 确认已开启开发者选项和 USB 调试
- 运行 `adb devices` 检查设备是否识别

**问题**: 未获取到数据
- 确认当前页面是职位列表页
- 检查 Resource ID 是否发生变化（可用 uiautodev 重新分析）
- 尝试增加等待时间 `SCROLL_SLEEP`
