# 🔬 Prompt工程实验平台

一个基于 Streamlit 和 Hugging Face API 的 Prompt 工程实验平台，帮助你系统性地测试和优化 Prompt，提升 LLM 应用效果。

## ✨ 功能特性

### 核心功能

* ✅ **多种 Prompt 模板**：预设 8 种常用 Prompt 模板（角色扮演、思维链、少样本学习等）

* ✅ **自定义模板**：支持创建自己的 Prompt 模板

* ✅ **多模型支持**：支持 Kimi、DeepSeek、Llama 3.1 等主流模型

* ✅ **参数调整**：可调整 Temperature、Max Tokens 等参数

* ✅ **实验记录**：自动保存所有实验记录，支持查看历史

* ✅ **实验对比**：支持对比多个实验的结果，分析不同 Prompt 效果

* ✅ **数据导出**：支持导出实验记录为 JSON 格式

### Prompt 模板类型

1. **角色扮演**：让模型扮演特定角色，提升回答的专业性

2. **思维链（Chain of Thought）**：引导模型逐步思考，提高复杂问题的准确性

3. **少样本学习（Few-shot）**：提供示例，让模型学习任务模式

4. **结构化输出**：要求模型输出特定格式（如 JSON）

5. **零样本分类**：无需训练即可进行分类任务

6. **文本摘要**：快速生成文本摘要

7. **代码生成**：生成特定语言的代码

8. **自定义**：创建自己的 Prompt 模板

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 Hugging Face Token

1. 访问 [Hugging Face](https://huggingface.co/)

2. 注册/登录账号

3. 进入 Settings → Access Tokens

4. 创建新的 Token（选择 Read 权限即可）

### 3. 运行应用

```bash
streamlit run Prompt.py
```

### 4. 使用步骤

1. **输入 Token**：在侧边栏输入你的 Hugging Face API Token

2. **选择模板**：从预设模板中选择一个，或选择"自定义"

3. **填写变量**：根据模板要求填写变量值

4. **输入问题**：在右侧输入你想要测试的用户输入

5. **调整参数**：设置 Temperature 和 Max Tokens

6. **运行实验**：点击"运行实验"按钮

7. **查看结果**：查看输出结果和实验记录

## 📖 使用示例

### 示例1：角色扮演 - Python 老师

1. 选择模板：**角色扮演**

2. 填写变量：

   * `role`: Python编程老师

   * `task`: 解释编程概念，帮助初学者理解

3. 用户输入：`什么是列表？`

4. 运行实验，查看结果

### 示例2：思维链 - 数学问题

1. 选择模板：**思维链（Chain of Thought）**

2. 填写变量：

   * `question`: 如何计算 1+2+3+...+100？

3. 运行实验，观察模型如何逐步思考

### 示例3：少样本学习 - 情感分析

1. 选择模板：**少样本学习（Few-shot）**

2. 填写变量：

   * `example1_input`: 今天天气很好

   * `example1_output`: 情感：积极

   * `example2_input`: 今天下雨了

   * `example2_output`: 情感：消极

   * `input`: 今天阳光明媚

3. 运行实验，查看模型是否能正确分类

## 🎯 Prompt 工程技巧

### 1. 明确角色和任务

```
❌ 不好的 Prompt：
"回答这个问题"

✅ 好的 Prompt：
"你是一个Python编程老师，你的任务是解释编程概念，帮助初学者理解。请以专业、友好的方式回答用户的问题。"
```

### 2. 使用思维链

```
❌ 直接问：
"如何学习Python？"

✅ 引导思考：
"让我们一步步思考：1. 首先，确定学习目标；2. 然后，选择学习资源；3. 最后，制定学习计划。问题：如何学习Python？"
```

### 3. 提供示例

```
✅ 少样本学习：
"示例1：输入'今天天气很好'，输出'情感：积极'
示例2：输入'今天下雨了'，输出'情感：消极'
现在处理：输入'今天阳光明媚'"
```

### 4. 明确输出格式

```
✅ 结构化输出：
"请以JSON格式输出，包含以下字段：name, age, city
输入：张三，25岁，住在北京"
```

## 📊 实验对比

使用"实验对比"功能可以：

* 对比不同 Prompt 的效果

* 分析不同参数（Temperature、Max Tokens）的影响

* 评估不同模型的性能

* 找出最优的 Prompt 组合

## 🔧 技术栈

* **Streamlit**：Web 应用框架

* **Hugging Face Hub**：LLM API 调用

* **Python 3.8+**：编程语言

## 📝 项目结构

```
项目3Prompt/
├── Prompt.py              # 主程序文件
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

## 💡 学习建议

### 第1天：角色扮演

* [ ] 让模型扮演 Python 老师，解释什么是列表

* [ ] 让模型扮演面试官，模拟技术面试

* [ ] 对比不同角色设定的效果

### 第2天：思维链（Chain of Thought）

* [ ] 解数学题，对比有无"让我们一步步思考"的差异

* [ ] 复杂推理任务

* [ ] 记录效果提升

### 第3天：结构化输出

* [ ] 让模型输出 JSON 格式

* [ ] 让模型输出 Markdown 表格

* [ ] 提取信息并结构化

## 🐛 常见问题

### Q: Token 格式错误？

A: Hugging Face Token 应该以 `hf_` 开头，长度通常为 30+ 字符。

### Q: API 调用失败？

A: 检查：

1. Token 是否正确

2. 网络连接是否正常

3. 模型是否可用（某些模型可能需要等待加载）

### Q: 如何保存实验记录？

A: 所有实验会自动保存到会话中。你可以点击"导出所有实验记录"下载 JSON 文件。

## 📚 相关资源

* [Hugging Face 文档](https://huggingface.co/docs)

* [Streamlit 文档](https://docs.streamlit.io/)

* [Prompt Engineering Guide](https://www.promptingguide.ai/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**开始你的 Prompt 工程之旅吧！** 🚀
