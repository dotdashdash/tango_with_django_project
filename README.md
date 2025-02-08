# TimeHero

**TimeHero** 是一款任务与成就管理 Web 应用，旨在帮助用户跟踪日常任务、完成成就，并通过游戏化体验提升生产力。

## 功能特性

- 📝 **任务管理**：创建、更新、完成任务，设置截止日期和优先级。
- 🎖️ **成就系统**：根据任务完成情况解锁成就。
- 📊 **用户仪表盘**：查看任务统计、成就进度和个人绩效。
- 🌍 **Web 界面**：可在浏览器访问，交互式 UI 设计。
- 🗺️ **成就墙**：可视化展示已解锁的成就。

## 技术栈

- **后端**：Django, Django REST Framework
- **前端**：Django 模板引擎, JavaScript, HTML, CSS
- **数据库**：SQLite3
- **API**：提供 RESTful API 进行任务和成就管理

## 安装指南

### 先决条件
请确保已安装以下环境：
- Python 3.x
- pip
- 虚拟环境（推荐）

### 安装步骤

1. **克隆代码仓库**
   ```sh
   git clone https://github.com/dotdashdash/tango_with_django_project.git
   cd TimeHero
2. **创建并激活虚拟环境**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Windows 用户使用：venv\Scripts\activate
3. **安装依赖**
   ```sh
   pip install -r requirements.txt
4. **数据库迁移**
   ```sh
   python manage.py migrate
5. **启动服务器**
   ```sh
   python manage.py migrate
6. **访问**
   ```sh
   http://127.0.0.1:8000/
## 使用指南
- **注册/登录：** 创建账户或登录管理任务。
- **添加任务：** 定义新任务，设置截止时间和优先级。
- **完成任务：** 标记任务完成，获得经验值。
- **解锁成就：** 完成任务可解锁成就并进行展示。
## 贡献指南
欢迎贡献代码！请按照以下步骤操作：

- **1.** Fork 本仓库。
- **2.** 创建 新分支。
- **3.** 提交修改 并推送到你的 Fork 仓库。
- **4.** 提交 Pull Request 以合并代码。
