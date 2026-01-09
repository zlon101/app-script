# Android App 数据爬虫框架

一个通用的、可配置化的 Android App 数据抓取框架，支持自动化滚动、智能去重、智能停止等功能。

## 📦 项目结构

```
app-script/
├── generic_app_spider.py       # 通用爬虫核心类
├── boss_spider_example.py      # Boss直聘爬虫示例
├── multi_app_examples.py       # 多App配置示例
├── advanced_examples.py        # 高级功能示例
├── config_template.py          # 配置模板和向导
├── requirements.txt            # 依赖包
├── README.md                   # 说明文档
├── CHANGELOG.md               # 更新日志
└── REFACTOR.md                # 重构说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt

pip install uiautomator2
pip install -U uiautodev -i https://pypi.doubanio.com/simple

# 手机连接电脑，开启usb调试，执行命令
python -m uiautomator2 init
# 执行成功后，手机上会出现一个小汽车图标的 App (ATX)。

# 执行命令，查看页面元素
uiauto.dev
```


### 2. 连接设备

确保 Android 设备通过 USB 连接到电脑，并开启 USB 调试模式。

### 3. 运行示例

```bash
# 运行 Boss直聘爬虫
python boss_spider_example.py

# 或运行多App示例
python multi_app_examples.py

# 或运行高级示例
python advanced_examples.py
```

## 💡 核心特性

- ✅ **通用性强**: 适用于任何 Android App 的列表页面数据抓取
- ✅ **配置简单**: 只需提供包名和字段选择器即可
- ✅ **智能去重**: 支持多字段组合去重
- ✅ **智能停止**: 自动检测无新数据，避免无效滚动
- ✅ **精确控制**: 按数据条数而非滚动次数控制
- ✅ **美化输出**: 使用 Rich 库提供友好的终端界面
- ✅ **中断恢复**: 支持 Ctrl+C 中断并保存已抓取数据
- ✅ **扩展性强**: 支持回调函数、自定义滚动等高级功能

## 📖 基础使用

### 最简配置

```python
from generic_app_spider import GenericAppSpider

spider = GenericAppSpider(
    app_package="com.example.app",
    selectors={
        "标题": "com.example.app:id/title",
        "内容": "com.example.app:id/content"
    }
    # 默认抓取100条数据
)

spider.run()
```

### 完整配置

```python
spider = GenericAppSpider(
    app_package="com.hpbr.bosszhipin",           # App包名
    selectors={                                   # 字段选择器（中文key）
        "职位名称": "com.hpbr.bosszhipin:id/tv_position_name",
        "薪资待遇": "com.hpbr.bosszhipin:id/tv_salary_statue",
        "公司名称": "com.hpbr.bosszhipin:id/tv_company_name"
    },
    max_items=100,                                # 最大数据条数（v2.0新特性）
    scroll_sleep=2.5,                             # 滚动后等待时间（秒）
    unique_keys=["职位名称", "公司名称"],          # 去重字段组合
    output_prefix="boss_jobs",                    # 输出文件前缀
    title="Boss直聘职位爬虫",                     # 显示标题
    max_empty_scrolls=3                           # 连续3次无数据停止
)

spider.run()
```

## 🎯 参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `app_package` | str | App的包名，如 `com.hpbr.bosszhipin` |
| `selectors` | Dict[str, str] | 字段选择器映射，key为中文字段名，value为resourceId |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_items` | int | 100 | 最大数据条数 ⭐ v2.0新特性 |
| `scroll_sleep` | float | 2.5 | 滚动后等待时间（秒） |
| `unique_keys` | List[str] | 第一个字段 | 用于去重的字段列表 |
| `output_prefix` | str | "data" | 输出JSON文件名前缀 |
| `title` | str | "通用数据爬虫" | 爬虫显示标题 |
| `max_empty_scrolls` | int | 3 | 连续多少次无新数据时停止 ⭐ v2.0新特性 |

## 🆕 v2.0 新特性

### 1. 数据条数控制（取代滚动次数）

```python
# ❌ v1.0 方式（已弃用）
spider = GenericAppSpider(
    max_pages=10  # 滚动10次，不知道能抓多少数据
)

# ✅ v2.0 方式（推荐）
spider = GenericAppSpider(
    max_items=100  # 精确抓取100条数据
)
```

**优势**：
- 更直观：直接知道会获取多少数据
- 更精确：达到目标条数即停止
- 更智能：配合智能停止机制

### 2. 智能停止机制

```python
spider = GenericAppSpider(
    max_items=1000,           # 设置较大值
    max_empty_scrolls=3       # 连续3次无数据则停止
)
```

**场景说明**：
- 列表有200条数据，设置 `max_items=1000`
- 爬虫会在抓取完200条后，连续3次滚动无新数据
- 自动停止，不会无效滚动到1000次

**优势**：
- ✅ 自动检测列表底部
- ✅ 避免无效滚动
- ✅ 节省时间和资源

### 3. 改进的进度显示

```
正在抓取... (45/100) ████████░░░░░░░░ 45%
第 5 次滚动: 新增 8 条，累计 45 条
```

## 📝 配置示例

### Boss直聘

```python
BOSS_CONFIG = {
    "app_package": "com.hpbr.bosszhipin",
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
```

### 58同城

```python
WUBA_CONFIG = {
    "app_package": "com.wuba",
    "selectors": {
        "标题": "com.wuba:id/title",
        "价格": "com.wuba:id/price",
        "位置": "com.wuba:id/location"
    },
    "max_items": 200,
    "scroll_sleep": 3.0,
    "unique_keys": ["标题", "位置"],
    "output_prefix": "wuba_data"
}
```

## 🔥 高级功能

### 1. 使用回调函数

```python
def before_parse():
    """每次解析前执行"""
    print("准备解析...")

def after_parse(items):
    """每次解析后执行"""
    print(f"获取到 {len(items)} 条数据")

spider.run(before_parse=before_parse, after_parse=after_parse)
```

### 2. 自定义滚动策略

```python
class CustomSpider(GenericAppSpider):
    def scroll_page(self):
        # 自定义滚动逻辑
        pass

spider = CustomSpider(...)
spider.run()
```

### 3. 数据后处理

```python
spider.run()
data = spider.get_data()

# 对数据进行分析处理
for item in data:
    # 处理每条数据
    pass
```

### 4. 智能停止示例

```python
# 场景：不确定列表有多少数据，抓取所有可用数据
spider = GenericAppSpider(
    app_package="com.hpbr.bosszhipin",
    selectors={...},
    max_items=99999,           # 设置很大的值
    max_empty_scrolls=3        # 依赖智能停止
)
spider.run()
# 优点：会自动抓到列表底部后停止，不用担心设置太大
```

## 🔍 如何获取 Resource ID

### 方法1: 使用 uiautomator2 自带工具

```bash
# 启动设备inspector
python -m uiautomator2 init
python -m weditor
```

访问 `http://localhost:17310` 查看页面元素。

### 方法2: 使用 Android Studio Layout Inspector

1. 打开 Android Studio
2. Tools → Layout Inspector
3. 选择设备和进程
4. 查看元素的 resource-id

### 方法3: 使用 ADB

```bash
adb shell uiautomator dump
adb pull /sdcard/window_dump.xml
```

在 XML 文件中查找 resource-id。

## 📤 输出格式

数据保存为 JSON 格式，文件名格式：`{output_prefix}_{timestamp}.json`

```json
[
  {
    "职位名称": "Python开发工程师",
    "薪资待遇": "20-35K",
    "公司名称": "某科技公司",
    "招聘者": "张先生",
    "公司信息": "D轮 · 500-999人"
  },
  ...
]
```

## ⚙️ 环境要求

- Python 3.7+
- MacOS / Linux / Windows
- Android 设备（USB连接）
- ADB 工具已配置

## 🔧 故障排查

### 问题1: 设备连接失败

**解决方案:**
```bash
# 检查设备连接
adb devices

# 重启 ADB
adb kill-server
adb start-server
```

### 问题2: 未获取到数据

**可能原因:**
- Resource ID 不正确
- 页面未加载完成
- 需要先手动进入列表页

**解决方案:**
- 使用 weditor 重新确认 Resource ID
- 增加 `scroll_sleep` 时间
- 运行前手动打开 App 并进入目标页面

### 问题3: 数据重复

**解决方案:**
- 检查 `unique_keys` 配置是否合理
- 确保去重字段具有唯一性

### 问题4: 过早停止或过度滚动

**解决方案:**
- 调整 `max_empty_scrolls` 参数
  - 列表加载慢：增大值（如5）
  - 列表加载快：减小值（如2）
- 调整 `scroll_sleep` 等待时间

## 📚 更多示例

查看以下文件获取更多使用示例：

- `boss_spider_example.py` - Boss直聘基础示例
- `multi_app_examples.py` - 多种App配置示例
- `advanced_examples.py` - 高级功能演示
- `CHANGELOG.md` - 版本更新记录
- `REFACTOR.md` - 重构说明文档

## 🔄 从 v1.0 迁移

如果你正在使用旧版本（v1.0），请参考迁移指南：

```python
# v1.0 (旧代码) ❌
spider = GenericAppSpider(
    max_pages=10  # 已弃用
)

# v2.0 (新代码) ✅
spider = GenericAppSpider(
    max_items=100,          # 使用数据条数
    max_empty_scrolls=3     # 新增智能停止
)
```

详细迁移指南请参考 `CHANGELOG.md`。

## 💡 使用建议

### 场景1：明确需要多少数据

```python
spider = GenericAppSpider(
    max_items=100,          # 我需要100条
    max_empty_scrolls=3
)
```

### 场景2：抓取所有可用数据

```python
spider = GenericAppSpider(
    max_items=99999,        # 很大的值
    max_empty_scrolls=3     # 依赖智能停止
)
```

### 场景3：快速测试

```python
spider = GenericAppSpider(
    max_items=10,           # 只抓10条
    max_empty_scrolls=2     # 更快停止
)
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## ⚠️ 免责声明

本工具仅用于学习和研究目的，使用者需遵守相关法律法规和目标App的服务条款。请勿用于商业用途或大规模数据抓取。
