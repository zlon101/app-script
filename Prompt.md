# Role
你是 Python 自动化开发专家，精通 Android `uiautomator2` 库和数据抓取。

# Context
我正在 MacOS 环境下开发一个 Android 爬虫，目标是抓取 "Boss直聘" App 的职位列表数据。
我已经配置好了 ADB 和 `uiautomator2` 环境，并且通过 uiautodev 分析了页面结构。

# Task
请帮我生成一个完整的 Python 项目代码，用于自动化抓取职位列表并保存为 JSON 文件。

# Technical Requirements
1. **库依赖**: 使用 `uiautomator2` 进行控制，使用 `pandas` 处理数据，使用 `rich` 库美化终端输出。
2. **设备连接**: 自动连接 USB 设备（默认连接第一台）。
3. **App控制**: 确保 App (包名 `com.hpbr.bosszhipin`)在前台运行。

# Data & Selectors (Based on uiautodev analysis)
请基于以下 Resource-ID 抓取当前屏幕可见的列表项：
*   职位名称: `com.hpbr.bosszhipin:id/tv_position_name`
*   薪资待遇: `com.hpbr.bosszhipin:id/tv_salary_statue` (注意：App源码里 ID 就是 statue 不是 status，请保留此拼写)
*   公司名称: `com.hpbr.bosszhipin:id/tv_company_name` (如果这一项存在)
*   招聘者/HR: `com.hpbr.bosszhipin:id/tv_employer`
*   公司规模/融资: `com.hpbr.bosszhipin:id/tv_company_industry` (可选)

# Logic Flow
1. **初始化**: 连接手机，检查并启动 App。
2. **抓取循环**:
    *   获取当前页面的所有职位元素。
    *   解析每个职位的文本信息。
    *   **去重处理**: 使用 (职位名+公司名) 作为唯一键，避免滚动产生的重复数据。
    *   **滚动操作**: 模拟手指从屏幕下部(80%)向上滑到上部(30%)。
    *   **等待**: 每次滑动后 `time.sleep` 2-3秒等待加载。
3. **终止条件**:
    *   用户可以通过 `Ctrl+C` 手动停止。
    *   或者设定默认抓取 `MAX_PAGES = 10` 页。
4. **数据保存**:
    *   程序结束或中断时，将已抓取的数据保存为 `boss_jobs_[timestamp].json`。

# require
1. 语言使用中文
2. 简化输出