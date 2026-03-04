import streamlit as st
import os
import hashlib
import time
import json
from datetime import datetime
from huggingface_hub import InferenceClient
import requests

# 设置页面配置
st.set_page_config(
    page_title="Prompt工程实验平台",
    page_icon="🔬",
    layout="wide"
)

# ============================================================================
# 初始化会话状态
# ============================================================================

if "experiments" not in st.session_state:
    st.session_state.experiments = []  # 存储实验记录

if "client" not in st.session_state:
    st.session_state.client = None

if "client_config" not in st.session_state:
    st.session_state.client_config = {"token": None}

if "cache" not in st.session_state:
    st.session_state.cache = {}

# ============================================================================
# 预设 Prompt 模板
# ============================================================================

PROMPT_TEMPLATES = {
    "角色扮演": {
        "template": "你是一个{role}，你的任务是{task}。请以专业、友好的方式回答用户的问题。",
        "variables": ["role", "task"],
        "example": {
            "role": "Python编程老师",
            "task": "解释编程概念，帮助初学者理解"
        }
    },
    "思维链（Chain of Thought）": {
        "template": "让我们一步步思考这个问题：\n1. 首先，分析问题的关键点\n2. 然后，列出可能的解决方案\n3. 最后，给出结论和理由\n\n问题：{question}",
        "variables": ["question"],
        "example": {
            "question": "如何学习Python？"
        }
    },
    "少样本学习（Few-shot）": {
        "template": "以下是几个示例：\n\n示例1：\n输入：{example1_input}\n输出：{example1_output}\n\n示例2：\n输入：{example2_input}\n输出：{example2_output}\n\n现在处理：\n输入：{input}",
        "variables": ["example1_input", "example1_output", "example2_input", "example2_output", "input"],
        "example": {
            "example1_input": "今天天气很好",
            "example1_output": "情感：积极",
            "example2_input": "今天下雨了",
            "example2_output": "情感：消极",
            "input": "今天阳光明媚"
        }
    },
    "结构化输出": {
        "template": "请以JSON格式输出，包含以下字段：{fields}\n\n输入：{input}",
        "variables": ["fields", "input"],
        "example": {
            "fields": "name, age, city",
            "input": "张三，25岁，住在北京"
        }
    },
    "零样本分类": {
        "template": "请将以下文本分类到以下类别之一：{categories}\n\n文本：{text}\n\n只输出类别名称。",
        "variables": ["categories", "text"],
        "example": {
            "categories": "科技、体育、娱乐、财经",
            "text": "今天股市大涨"
        }
    },
    "文本摘要": {
        "template": "请用一句话总结以下文本的核心内容：\n\n{text}",
        "variables": ["text"],
        "example": {
            "text": "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。"
        }
    },
    "代码生成": {
        "template": "你是一个专业的{language}程序员。请根据以下需求生成代码：\n\n需求：{requirement}\n\n要求：\n1. 代码要有注释\n2. 遵循最佳实践\n3. 处理边界情况",
        "variables": ["language", "requirement"],
        "example": {
            "language": "Python",
            "requirement": "写一个函数，计算斐波那契数列的第n项"
        }
    },
    "自定义": {
        "template": "{custom_prompt}",
        "variables": ["custom_prompt"],
        "example": {
            "custom_prompt": "你是一个AI助手，请回答问题。"
        }
    }
}

# 支持的模型列表
SUPPORTED_MODELS = [
    "moonshotai/Kimi-K2-Thinking",
    "deepseek-ai/DeepSeek-V3.2",
    "meta-llama/Llama-3.1-8B-Instruct"
]

# ============================================================================
# 辅助函数
# ============================================================================

def get_client(token):
    """获取或创建 InferenceClient 客户端"""
    if (st.session_state.client is None or 
        st.session_state.client_config["token"] != token):
        st.session_state.client = InferenceClient(token=token if token else None)
        st.session_state.client_config["token"] = token
    return st.session_state.client

def format_template(template, variables):
    """格式化模板，替换变量"""
    try:
        return template.format(**variables)
    except KeyError as e:
        st.error(f"模板变量错误：缺少变量 {e}")
        return template

def call_hf_llm(token, model_name, system_prompt, user_input, temperature=0.7, max_tokens=500):
    """调用 Hugging Face LLM API"""
    try:
        client = get_client(token)
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_input})
        
        # 调用 API（使用 chat_completion 接口）
        response = client.chat_completion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 解析响应
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content
            usage = getattr(response, 'usage', None)
            return {
                "success": True,
                "content": content,
                "usage": usage
            }
        else:
            return {
                "success": False,
                "error": "响应格式异常"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_experiment(system_prompt, user_input, model_name, temperature, max_tokens, response, usage_info):
    """保存实验记录"""
    experiment = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_prompt": system_prompt,
        "user_input": user_input,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response": response,
        "usage": usage_info
    }
    st.session_state.experiments.append(experiment)
    
    # 限制实验记录数量（最多保留100条）
    if len(st.session_state.experiments) > 100:
        st.session_state.experiments = st.session_state.experiments[-100:]

# ============================================================================
# 主界面
# ============================================================================

st.title("🔬 Prompt工程实验平台")
st.markdown("---")

# 侧边栏：配置
with st.sidebar:
    st.header("⚙️ 配置")
    
    # Hugging Face Token
    hf_token = st.text_input(
        "Hugging Face Token",
        type="password",
        help="输入你的 Hugging Face API Token"
    )
    
    # Token 状态检查
    if hf_token:
        if len(hf_token) > 10 and hf_token.startswith("hf_"):
            st.success("✅ Token 格式正确")
        else:
            st.warning("⚠️ Token 格式可能不正确（应以 hf_ 开头）")
    else:
        st.info("💡 请输入 Hugging Face Token")
    
    st.markdown("---")
    
    # 模型选择
    st.subheader("🤖 模型选择")
    selected_model = st.selectbox(
        "选择模型",
        SUPPORTED_MODELS,
        help="选择要使用的 LLM 模型"
    )
    
    st.markdown("---")
    
    # 参数调整
    st.subheader("🎛️ 参数调整")
    temperature = st.slider(
        "Temperature",
        0.0, 2.0, 0.7, 0.1,
        help="控制输出的随机性。值越高，输出越随机；值越低，输出越确定。"
    )
    max_tokens = st.slider(
        "Max Tokens",
        100, 2000, 500, 50,
        help="生成的最大 token 数量"
    )
    
    st.markdown("---")
    
    # 统计信息
    st.subheader("📊 统计信息")
    st.metric("实验次数", len(st.session_state.experiments))
    st.metric("缓存条目", len(st.session_state.cache))
    
    # 清除按钮
    if st.button("🗑️ 清除所有实验记录", type="secondary"):
        st.session_state.experiments = []
        st.rerun()

# 主内容区
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Prompt 模板")
    
    # 模板选择
    template_name = st.selectbox(
        "选择模板类型",
        list(PROMPT_TEMPLATES.keys()),
        help="选择预设的 Prompt 模板"
    )
    
    template_info = PROMPT_TEMPLATES[template_name]
    
    # 显示模板说明
    with st.expander("📖 模板说明"):
        st.write(f"**模板类型**：{template_name}")
        st.write(f"**变量**：{', '.join(template_info['variables'])}")
        st.write("**示例**：")
        st.json(template_info['example'])
    
    # 变量输入
    st.markdown("### 填写变量")
    variables = {}
    for var in template_info['variables']:
        if var == "custom_prompt":
            variables[var] = st.text_area(
                f"自定义 Prompt",
                value=template_info['example'].get(var, ""),
                height=150,
                help="输入你的自定义 Prompt"
            )
        else:
            variables[var] = st.text_input(
                f"{var}",
                value=template_info['example'].get(var, ""),
                help=f"输入变量 {var} 的值"
            )
    
    # 生成系统提示词
    system_prompt = format_template(template_info['template'], variables)
    
    st.markdown("### 生成的系统提示词")
    st.text_area(
        "系统提示词",
        value=system_prompt,
        height=150,
        key="system_prompt_display",
        help="这是将发送给模型的系统提示词"
    )

with col2:
    st.subheader("💬 用户输入")
    
    user_input = st.text_area(
        "输入你的问题或文本",
        height=200,
        placeholder="例如：解释什么是Python？",
        help="输入你想要测试的用户输入"
    )
    
    st.markdown("---")
    
    # 运行按钮
    run_button = st.button("🚀 运行实验", type="primary", use_container_width=True)
    
    if run_button:
        if not hf_token:
            st.error("❌ 请先输入 Hugging Face Token")
        elif not user_input:
            st.error("❌ 请输入用户输入")
        else:
            with st.spinner("🤔 生成中..."):
                # 调用 API
                result = call_hf_llm(
                    hf_token,
                    selected_model,
                    system_prompt,
                    user_input,
                    temperature,
                    max_tokens
                )
                
                if result["success"]:
                    # 显示结果
                    st.markdown("### ✅ 输出结果")
                    st.write(result["content"])
                    
                    # 显示使用信息
                    if result.get("usage"):
                        usage = result["usage"]
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("输入 Tokens", getattr(usage, 'prompt_tokens', 'N/A'))
                        with col_b:
                            st.metric("输出 Tokens", getattr(usage, 'completion_tokens', 'N/A'))
                        with col_c:
                            st.metric("总计 Tokens", getattr(usage, 'total_tokens', 'N/A'))
                    
                    # 保存实验记录
                    save_experiment(
                        system_prompt,
                        user_input,
                        selected_model,
                        temperature,
                        max_tokens,
                        result["content"],
                        result.get("usage")
                    )
                    
                    st.success("✅ 实验完成！已保存到实验记录")
                else:
                    st.error(f"❌ 生成失败：{result.get('error', '未知错误')}")

# ============================================================================
# 实验记录和历史
# ============================================================================

st.markdown("---")
st.subheader("📚 实验记录")

if len(st.session_state.experiments) == 0:
    st.info("💡 还没有实验记录。运行一次实验后，记录会显示在这里。")
else:
    # 显示最近的实验
    st.markdown(f"**最近 {min(5, len(st.session_state.experiments))} 次实验**")
    
    for i, exp in enumerate(reversed(st.session_state.experiments[-5:])):
        with st.expander(f"实验 #{len(st.session_state.experiments) - i} - {exp['timestamp']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**模型**：", exp['model_name'])
                st.write("**Temperature**：", exp['temperature'])
                st.write("**Max Tokens**：", exp['max_tokens'])
            
            with col2:
                if exp.get('usage'):
                    usage = exp['usage']
                    st.write("**输入 Tokens**：", getattr(usage, 'prompt_tokens', 'N/A'))
                    st.write("**输出 Tokens**：", getattr(usage, 'completion_tokens', 'N/A'))
                    st.write("**总计 Tokens**：", getattr(usage, 'total_tokens', 'N/A'))
            
            st.markdown("**系统提示词**：")
            st.code(exp['system_prompt'], language=None)
            
            st.markdown("**用户输入**：")
            st.write(exp['user_input'])
            
            st.markdown("**模型输出**：")
            st.write(exp['response'])
    
    # 导出功能
    st.markdown("---")
    if st.button("📥 导出所有实验记录（JSON）"):
        experiments_json = json.dumps(st.session_state.experiments, ensure_ascii=False, indent=2)
        st.download_button(
            label="下载 JSON 文件",
            data=experiments_json,
            file_name=f"prompt_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# ============================================================================
# 实验对比功能
# ============================================================================

st.markdown("---")
st.subheader("🔍 实验对比")

if len(st.session_state.experiments) >= 2:
    # 选择要对比的实验
    exp_indices = st.multiselect(
        "选择要对比的实验（至少2个）",
        range(len(st.session_state.experiments)),
        format_func=lambda x: f"实验 #{x+1} - {st.session_state.experiments[x]['timestamp']}",
        help="选择多个实验进行对比"
    )
    
    if len(exp_indices) >= 2:
        st.markdown("### 对比结果")
        
        # 创建对比表格
        comparison_data = []
        for idx in exp_indices:
            exp = st.session_state.experiments[idx]
            comparison_data.append({
                "实验编号": f"#{idx+1}",
                "时间": exp['timestamp'],
                "模型": exp['model_name'],
                "Temperature": exp['temperature'],
                "Max Tokens": exp['max_tokens'],
                "输出长度": len(exp['response'])
            })
        
        st.dataframe(comparison_data, use_container_width=True)
        
        # 显示详细对比
        for idx in exp_indices:
            exp = st.session_state.experiments[idx]
            with st.expander(f"实验 #{idx+1} - {exp['timestamp']}"):
                st.write("**输出**：")
                st.write(exp['response'])
else:
    st.info("💡 需要至少2次实验才能进行对比。")

# ============================================================================
# 使用说明
# ============================================================================

with st.expander("📖 使用说明"):
    st.markdown("""
    ### 如何使用 Prompt 工程实验平台
    
    1. **输入 Token**：在侧边栏输入你的 Hugging Face API Token
    
    2. **选择模板**：从预设的 Prompt 模板中选择一个，或选择"自定义"创建自己的模板
    
    3. **填写变量**：根据模板要求填写变量值
    
    4. **输入问题**：在右侧输入你想要测试的用户输入
    
    5. **调整参数**：
       - **Temperature**：控制输出的随机性（0.0-2.0）
       - **Max Tokens**：限制生成的最大长度
    
    6. **运行实验**：点击"运行实验"按钮，查看结果
    
    7. **查看记录**：所有实验都会自动保存，可以在下方查看历史记录
    
    8. **对比实验**：选择多个实验进行对比，分析不同 Prompt 或参数的效果
    
    ### Prompt 工程技巧
    
    - **角色扮演**：明确告诉模型它的角色，能显著提升回答质量
    - **思维链**：要求模型"一步步思考"，能提高复杂问题的回答准确性
    - **少样本学习**：提供几个示例，让模型学习任务模式
    - **结构化输出**：明确要求输出格式，便于后续处理
    
    ### 实验建议
    
    - 尝试不同的 Temperature 值，观察输出变化
    - 对比不同模型的回答质量
    - 记录有效的 Prompt 模板，建立自己的 Prompt 库
    """)
