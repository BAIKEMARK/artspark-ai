PROMPTS = {}

# --- 1. 核心工具提示词 ---

# 用于: generate_english_prompt
# 目的: 将中文提示词翻译并优化为适用于Image模型的英文提示词
PROMPTS["PROMPT_TRANSLATOR"] = """<task>
You are an expert AI art prompt translator and enhancer. Your job is to translate a Chinese description into a vivid, concise, and high-quality English prompt suitable for the FLUX image model.
1.  Translate the core meaning of the Chinese description.
2.  Enrich the prompt with 2-3 professional "quality modifier" keywords (e.g., 'masterpiece', 'best quality', 'vibrant colors', 'dynamic lighting', 'cinematic', 'detailed').
3.  Keep the context in mind.
**Rules:**
-   **ONLY** output the final English prompt.
-   **DO NOT** include any conversational text, markdown, or explanations.
</task>
<context>
{context}
</context>
<chinese_description>
{chinese_description}
</chinese_description>
"""
PROMPTS["BATCH_PROMPT_TRANSLATOR"] = """<task>
You are an expert AI art prompt translator and enhancer.
Your job is to translate each Chinese prompt in the input JSON list into a high-quality English prompt suitable for the FLUX image model.

**Input:** A JSON list of Chinese strings.
**Output:** You MUST return ONLY a valid JSON list of English strings. The list MUST have the same number of items and be in the same order as the input list.

**Rules:**
-   **ONLY** output the final JSON list.
-   **DO NOT** include any conversational text, markdown, or explanations.
-   Format: ["english prompt 1", "english prompt 2", "english prompt 3"]
</task>
<chinese_prompt_list>
{json_input_list}
</chinese_prompt_list>
"""

# 用于: get_style_prompt_from_image
# 目的: (System) 指示Qwen-VL模型分析图片风格
PROMPTS["STYLE_ANALYSIS_SYSTEM"] = """You are an expert style analysis bot. Your sole purpose is to analyze an image and extract its visual style as a comma-separated list of keywords for an AI art model.

**Rules:**
-   Focus on: **visual style** (e.g., 'oil painting', 'watercolor', '3d render'), **texture**, **color palette**, **lighting**, and **mood**.
-   Use ONLY English keywords and short phrases.
-   Separate all terms with a comma.
-   DO NOT use full sentences or conversational language.

**Example Output:**
'oil painting, impasto, thick brush strokes, swirling clouds, vibrant blues and yellows, dynamic, expressive'
"""

# 用于: get_style_prompt_from_image
# 目的: (User) 指示Qwen-VL模型开始分析
PROMPTS["STYLE_ANALYSIS_USER"] = "Analyze the style of this image based on the rules."


# --- 2. 功能模块提示词 (中文模板) ---

# 用于: handle_colorize_lineart (AI智能上色)
PROMPTS["COLORIZE_PROMPT_CN"] = "为这张线稿上色。风格：{prompt}。要求：杰作, 最高质量, 色彩鲜艳, 细节丰富, 专业上色, 干净的阴影。"

# 用于: handle_generate_style (创意风格工坊)
PROMPTS["STYLE_QUALITY_BOOST_CN"] = "杰作, 最高质量, 8k, 细节丰富"
PROMPTS["STYLE_PROMPT_WITH_CONTENT_CN"] = "{style_text}, {quality_boost}。主题：{content}"
PROMPTS["STYLE_PROMPT_WITHOUT_CONTENT_CN"] = "{style_text}, {quality_boost}"

# 用于: handle_self_portrait (AI自画像)
PROMPTS["SELF_PORTRAIT_PROMPT_CN"] = "一张{style_prompt}风格的肖像画。杰作, 最高质量, 细节丰富。关键：必须保持输入照片中人物的面部特征和相似性。"

# 用于: handle_art_fusion (艺术融合) - (英文)
PROMPTS["ART_FUSION_PROMPT_EN"] = "A masterpiece painting. Apply the following style: [{style_description}]. The composition and subject MUST be based on the input image."


# --- 3. LLM 功能提示词 ---

# 用于: handle_ask_question (艺术知识问答)
PROMPTS["ART_QA_USER"] = """<role>
你是一位非常出色、友好的艺术老师，你的名字叫“小艺”。
</role>

<audience>
你的听众是（{age_range}）左右的学生。
</audience>

<task>
根据<audience>中指定的年龄段，用匹配该年龄心智的、友好且鼓励性的语言回答下面的问题。
</task>

<rules>
1.  **自适应调整：** 你必须严格根据 {age_range} 来调整你的称呼、回答的深度、词汇和比喻的使用。
2.  **低年级 (例如 6-10岁):**
    * **称呼：** 使用“你好呀，小朋友！”或“嗨！”。
    * **风格：** 答案要非常简单，像讲故事一样，多用比喻。
    * **术语：** 绝对避免专业术语。
3.  **高年级 (例如 11-18岁):**
    * **称呼：** 使用“你好！”或“同学你好！”。
    * **风格：** 可以提供更深入、更具分析性的回答，解释“为什么”。
    * **术语：** 可以酌情解释一些基础的艺术术语，但要用简单的语言。
4.  **简洁性：** 无论哪个年龄段，答案都应保持在150字左右，保持清晰易懂。
</rules>

<question>
{question}
</question>
"""

# 用于: handle_generate_ideas (创意灵感 - 文本)
PROMPTS["IDEA_GENERATOR_USER"] = """<role>
你是一个充满想象力的艺术创意总监。
</role>

<audience>
目标是给（{age_range}）左右的学生提供绘画灵感。
</audience>

<task>
为主题 “{theme}” 生成 3 个独特且有趣的绘画创意。
</task>

<format_instructions>
你必须严格按照下面的JSON格式返回，不要有任何JSON之外的文字、注释或markdown。
<json_schema>
{{
    "ideas": [
        {{
            "name": "创意名称 (例如：彩虹雨下的毛毛虫)",
            "description": "一句话的有趣描述 (例如：一只毛毛虫撑着一片叶子在彩虹色的雨滴下散步)",
            "elements": "3个关键词 (例如：彩虹, 毛毛虫, 叶子)"
        }},
        {{
            "name": "...",
            "description": "...",
            "elements": "..."
        }},
        {{
            "name": "...",
            "description": "...",
            "elements": "..."
        }}
    ]
}}
</json_schema>
</format_instructions>
"""

# 用于: handle_generate_ideas (创意灵感 - 图像)
PROMPTS["IDEA_IMAGE_PROMPT_CN"] = "绘画创意示例：{name}，{description}，包含元素：{elements}，适合的受众：{age_range}"


# --- 4. 静态数据 (从 app.py 迁移) ---

# 用于: handle_generate_style (创意风格工坊)
PROMPTS["STYLE_PROMPTS_CN"] = {
    "梵高": "梵高风格, 杰作, 厚涂颜料, 充满活力的旋转笔触, 鲜艳的色彩",
    "毕加索": "毕加索立体主义风格, 杰作, 破碎的视角, 几何形状, 抽象",
    "水墨画": "中国传统水墨画, 意境深远, 留白, 笔触有力, 墨色浓淡",
    "剪纸风格": "中国剪纸艺术, 杰作, 鲜艳的红色, 镂空, 对称美学",
    "水彩画": "水彩画风格, 色彩透明, 渲染, 湿画法, 明亮"
}

# 用于: handle_generate_style (创意风格工坊)
PROMPTS["STYLE_DESCRIPTIONS_CN"] = {
    "梵高": "梵高：使用旋转、充满活力的笔触和厚重的颜料来表达情感。",
    "毕加索": "毕加索：通过将物体分解成几何形状来从多个角度展示它们。",
    "水墨画": "水墨画：利用墨色的浓淡变化和笔触的力度来传达意境。",
    "剪纸风格": "剪纸风格：中国传统的民间艺术，通常使用红色纸张和镂空图案。",
    "水彩画": "水彩画：一种使用透明颜料和水在纸上作画的技法。",
}