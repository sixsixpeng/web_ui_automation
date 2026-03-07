# -*- coding: UTF-8 -*-
"""
测试用例模块 (test_case)

提供自动化测试框架的测试用例实现，包括：
- UI 自动化测试用例：基于 Playwright 的 Web UI 测试，支持多浏览器、多页面交互
- API 自动化测试用例：基于 requests 的 API 测试，支持 RESTful API、GraphQL 等
- 混合测试用例：UI 和 API 结合的测试，实现端到端业务流程验证
- 数据驱动测试：使用参数化实现多组数据测试，支持 Excel、YAML、JSON 数据源
- 并发测试：使用 pytest-xdist 实现测试并行执行，提高测试效率

测试用例设计原则：
1. 使用 pytest 测试框架，利用其丰富的插件生态系统
2. 使用 Allure 注解增强测试报告（@allure.epic, @allure.feature, @allure.story）
3. 使用夹具管理测试资源（browser, page, api_client），确保资源正确初始化和清理
4. 使用页面对象和 API 封装进行测试，实现测试逻辑与实现细节分离
5. 使用标记（@pytest.mark）对测试进行分类（ui, api, smoke, regression）
6. 使用参数化（@pytest.mark.parametrize）实现数据驱动测试
7. 使用断言验证测试结果，优先使用 pytest 内置断言，支持多断言

主要测试用例：
- test_login.py: 登录功能测试用例，包含成功登录、失败登录、边界情况等
- test_user_api.py: 用户 API 测试用例，包含用户 CRUD、权限验证等
- test_example.py: 示例测试用例，展示成功、失败、跳过、预期失败等测试场景
- test_demo_all_features.py: 综合演示测试用例，展示框架所有高级功能
- 其他测试：按业务需求添加的测试用例（如 test_dashboard.py, test_order.py）

运行测试：

#### 简化模式（推荐）
```bash
# 编辑 run_tests.py，取消注释要运行的测试类型，然后直接运行：
python run_tests.py
```

#### 命令行模式（备选）
```bash
# 使用运行脚本（需切换回命令行模式）
python run_tests.py ui        # 运行所有 UI 测试
python run_tests.py api       # 运行所有 API 测试
python run_tests.py demo      # 运行演示测试
python run_tests.py smoke     # 运行冒烟测试
python run_tests.py all       # 运行所有测试

# 使用 pytest 直接运行
pytest test_case/ -v                          # 运行所有测试，显示详细信息
pytest test_case/ -m ui -v                   # 只运行 UI 测试
pytest test_case/ -m demo -v                 # 只运行演示测试
pytest test_case/ -m "smoke or regression" -v # 运行冒烟或回归测试
pytest test_case/test_demo_all_features.py -v # 运行演示测试文件

# 并行执行
pytest test_case/ -n auto -v                 # 自动检测 CPU 核心数并行执行

# 生成报告
pytest test_case/ --alluredir=report/allure_raw
allure generate report/allure_raw -o report/allure_html --clean
allure open report/allure_html
```

注意：
- 此目录下的文件会被 pytest 自动发现，遵循命名规范 test_*.py 或 *_test.py
- conftest.py 中定义了共享夹具，如 browser, page, login_page, user_api 等
- 测试数据应放在 test_data/ 目录中，使用 file_utils 加载
- 测试失败时会自动截图，截图保存在 screenshot/ 目录中
- 测试日志会记录在 log/ 目录中，按天分割
"""

# 测试用例模块通常不需要导出具体测试类
# 测试类通过 pytest 自动发现和执行

__all__ = []  # 空列表，不导出任何内容