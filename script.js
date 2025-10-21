// ==========================================================
// 全局变量和 DOM 元素
// ==========================================================

let modelScopeToken = '';
const MODEL_SCOPE_TOKEN_KEY = 'modelscope_api_key';

// API 密钥区
const apiKeySection = document.getElementById('api-key-section');
const apiKeyInput = document.getElementById('api-key-input');
const saveKeyBtn = document.getElementById('save-key-btn');
const apiError = document.getElementById('api-error');

// 主内容区
const mainContent = document.getElementById('main-content');
const footerGuide = document.getElementById('footer-guide');
const mainNav = document.getElementById('main-nav');
const featurePanels = document.querySelectorAll('.feature-panel');

// 功能1: 分步绘画
const themeInput = document.getElementById('theme-input');
const difficultySelect = document.getElementById('difficulty-select');
const generateStepsBtn = document.getElementById('generate-steps-btn');
const stepsLoader = document.getElementById('steps-loader');
const stepsError = document.getElementById('steps-error');
const stepsResult = document.getElementById('steps-result');
const slideshowContent = document.getElementById('slideshow-content');
const prevStepBtn = document.getElementById('prev-step');
const nextStepBtn = document.getElementById('next-step');
const stepCounter = document.getElementById('step-counter');
let currentSlideIndex = 0;
let slides = [];

// 功能2: 风格工坊
const styleSelect = document.getElementById('style-select');
const styleContentInput = document.getElementById('style-content-input');
const generateStyleBtn = document.getElementById('generate-style-btn');
const styleLoader = document.getElementById('style-loader');
const styleError = document.getElementById('style-error');
const styleResult = document.getElementById('style-result');

// 功能3: 艺术问答
const qaInput = document.getElementById('qa-input');
const askQaBtn = document.getElementById('ask-qa-btn');
const qaLoader = document.getElementById('qa-loader');
const qaError = document.getElementById('qa-error');
const qaResult = document.getElementById('qa-result');

// 功能4: 创意灵感
const ideaThemeInput = document.getElementById('idea-theme-input');
const generateIdeasBtn = document.getElementById('generate-ideas-btn');
const ideasLoader = document.getElementById('ideas-loader');
const ideasError = document.getElementById('ideas-error');
const ideasResult = document.getElementById('ideas-result');


// ==========================================================
// 初始化
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
    initApiKeyManager();
    initNavigation();
    initStepGenerator();
    initStyleWorkshop();
    initArtQA();
    initIdeaGenerator();
});

// ==========================================================
// 核心模块 1: API 密钥管理
// ==========================================================

function initApiKeyManager() {
    const storedKey = localStorage.getItem(MODEL_SCOPE_TOKEN_KEY);
    if (storedKey) {
        modelScopeToken = storedKey;
        showMainContent();
    } else {
        showApiKeySection();
    }

    saveKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            modelScopeToken = key;
            localStorage.setItem(MODEL_SCOPE_TOKEN_KEY, key);
            showMainContent();
            apiError.textContent = '';
        } else {
            apiError.textContent = 'API KEY 不能为空';
        }
    });
}

function showMainContent() {
    apiKeySection.classList.add('hidden');
    mainContent.classList.remove('hidden');
    footerGuide.classList.remove('hidden');
}

function showApiKeySection() {
    apiKeySection.classList.remove('hidden');
    mainContent.classList.add('hidden');
    footerGuide.classList.add('hidden');
}

// ==========================================================
// 核心模块 2: 主导航切换
// ==========================================================

function initNavigation() {
    mainNav.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            const targetId = e.target.dataset.target;

            mainNav.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');

            featurePanels.forEach(panel => {
                panel.classList.add('hidden');
                panel.classList.remove('active');
            });

            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.remove('hidden');
                targetPanel.classList.add('active');
            }
        }
    });
}

// ==========================================================
// 核心模块 3: 分步绘画指导 (功能1)
// ==========================================================

function initStepGenerator() {
    generateStepsBtn.addEventListener('click', async () => {
        const theme = themeInput.value.trim();
        const difficulty = difficultySelect.value;

        if (!theme) {
            stepsError.textContent = '请输入绘画主题';
            return;
        }

        toggleUIState(generateStepsBtn, stepsLoader, stepsError, true);
        stepsResult.classList.add('hidden');

        try {
            // [!!!] 注意：这里现在会调用LLM进行提示词生成，会比以前慢
            const results = await generatePaintingSteps(modelScopeToken, theme, difficulty);
            if (!results || results.length === 0) {
                throw new Error("未能生成绘画步骤，请检查API KEY或网络。");
            }
            displayPaintingSteps(results);
        } catch (error) {
            stepsError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateStepsBtn, stepsLoader, stepsError, false);
        }
    });

    prevStepBtn.addEventListener('click', () => {
        currentSlideIndex = (currentSlideIndex - 1 + slides.length) % slides.length;
        showSlide(currentSlideIndex);
    });

    nextStepBtn.addEventListener('click', () => {
        currentSlideIndex = (currentSlideIndex + 1) % slides.length;
        showSlide(currentSlideIndex);
    });
}

function displayPaintingSteps(steps) {
    slideshowContent.innerHTML = ''; // 清空
    slides = []; // 重置幻灯片数组

    steps.forEach((step, index) => {
        const slide = document.createElement('div');
        slide.className = 'slide';

        const img = document.createElement('img');
        img.src = step.imageUrl;
        img.alt = `步骤 ${step.step}: ${step.description}`;

        const desc = document.createElement('p');
        desc.textContent = `第 ${step.step} 步：${step.description}`;

        slide.appendChild(img);
        slide.appendChild(desc);
        slideshowContent.appendChild(slide);
        slides.push(slide);
    });

    currentSlideIndex = 0;
    showSlide(currentSlideIndex);
    stepsResult.classList.remove('hidden');
}

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
    });
    stepCounter.textContent = `步骤 ${index + 1} / ${slides.length}`;
}

// ==========================================================
// 核心模块 4: 名画风格体验 (功能2)
// ==========================================================

function initStyleWorkshop() {
    generateStyleBtn.addEventListener('click', async () => {
        const style = styleSelect.value;
        const content = styleContentInput.value.trim();

        if (!content) {
            styleError.textContent = '请输入绘制内容';
            return;
        }

        toggleUIState(generateStyleBtn, styleLoader, styleError, true);
        styleResult.classList.add('hidden');

        try {
            const result = await generateArtStyle(modelScopeToken, content, style);
            displayArtStyle(result);
        } catch (error) {
            styleError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateStyleBtn, styleLoader, styleError, false);
        }
    });
}

function displayArtStyle(result) {
    styleResult.innerHTML = ''; // 清空

    const img = document.createElement('img');
    img.src = result.imageUrl;
    img.alt = `风格画作: ${styleContentInput.value.trim()}`;

    const desc = document.createElement('p');
    desc.className = 'style-desc';
    desc.textContent = result.styleDescription;

    styleResult.appendChild(img);
    styleResult.appendChild(desc);
    styleResult.classList.remove('hidden');
}

// ==========================================================
// 核心模块 5: 艺术知识问答 (功能3)
// ==========================================================

function initArtQA() {
    askQaBtn.addEventListener('click', async () => {
        const question = qaInput.value.trim();
        if (!question) {
            qaError.textContent = '请输入你的问题';
            return;
        }

        toggleUIState(askQaBtn, qaLoader, qaError, true);
        qaResult.classList.add('hidden');

        try {
            const result = await askArtQuestion(modelScopeToken, question);
            if (result.choices && result.choices[0] && result.choices[0].message) {
                displayQARSult(result.choices[0].message.content);
            } else if (result.message) {
                // 兼容某些API可能直接返回message
                throw new Error(result.message);
            }
            else {
                throw new Error("未能获取回答，请检查API KEY或网络。");
            }
        } catch (error) {
            qaError.textContent = `回答失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(askQaBtn, qaLoader, qaError, false);
        }
    });
}

function displayQAResult(answer) {
    qaResult.textContent = answer;
    qaResult.classList.remove('hidden');
}

// ==========================================================
// 核心模块 6: 创意灵感生成 (功能4)
// ==========================================================

function initIdeaGenerator() {
    generateIdeasBtn.addEventListener('click', async () => {
        const theme = ideaThemeInput.value.trim();
        if (!theme) {
            ideasError.textContent = '请输入灵感主题';
            return;
        }

        toggleUIState(generateIdeasBtn, ideasLoader, ideasError, true);
        ideasResult.classList.add('hidden');

        try {
            const ideas = await generateArtIdeas(modelScopeToken, theme);
            displayArtIdeas(ideas);
        } catch (error) {
            ideasError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateIdeasBtn, ideasLoader, ideasError, false);
        }
    });
}

function displayArtIdeas(ideas) {
    ideasResult.innerHTML = ''; // 清空

    if (!ideas || ideas.length === 0) {
        ideasError.textContent = '未能解析创意，模型可能返回了无效格式。';
        return;
    }

    ideas.forEach(idea => {
        const card = document.createElement('div');
        card.className = 'idea-card';

        const img = document.createElement('img');
        img.src = idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image'; // 占位图
        img.alt = idea.name;

        const title = document.createElement('h3');
        title.textContent = idea.name;

        const desc = document.createElement('p');
        desc.textContent = idea.description;

        const elements = document.createElement('small');
        elements.textContent = `关键元素: ${idea.elements}`;

        card.appendChild(img);
        card.appendChild(title);
        card.appendChild(desc);
        card.appendChild(elements);
        ideasResult.appendChild(card);
    });

    ideasResult.classList.remove('hidden');
}


// ==========================================================
// 辅助函数
// ==========================================================

/**
 * 切换按钮、加载器和错误消息的UI状态
 */
function toggleUIState(button, loader, errorEl, isLoading) {
    if (isLoading) {
        button.disabled = true;
        loader.classList.remove('hidden');
        errorEl.textContent = ''; // 清除旧错误
    } else {
        button.disabled = false;
        loader.classList.add('hidden');
    }
}


// ==========================================================
// AI 调用函数
// ==========================================================

/**
 * @param {string} token - API token
 * @param {string} chinesePrompt - 用户的原始中文输入
 * @param {string} contextDescription - 提示词的上下文（例如：这是一个教学步骤）
 * @returns {Promise<string>} - 返回优化后的英文提示词
 */
async function generateEnglishPrompt(token, chinesePrompt, contextDescription) {
    const systemPrompt = `You are a professional AI painting prompt engineer. Your task is to translate a Chinese description into a high-quality, detailed English prompt suitable for an advanced model like FLUX.1.
- The prompt MUST be in English.
- The prompt should be a comma-separated list of descriptive keywords.
- Add relevant artistic details (e.g., 'digital art', 'vibrant colors', 'clean lines', 'white background', 'instructional diagram') based on the context.
- Context for this image: ${contextDescription}`;

    const userPrompt = `Chinese Description: "${chinesePrompt}"`;

    const response = await fetch("https://api-inference.modelscope.cn/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            model: "Qwen/Qwen2.5-72B-Instruct", // 使用Qwen来生成提示词
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt }
            ],
            max_tokens: 200,
            temperature: 0.5 // 较低的温度使提示词更稳定
        })
    });

    if (!response.ok) {
        throw new Error(`LLM prompt generation failed: ${response.status}`);
    }

    const data = await response.json();
    if (data.choices && data.choices[0] && data.choices[0].message) {
        // 清理LLM可能返回的多余引号
        const englishPrompt = data.choices[0].message.content.replace(/"/g, '').trim();
        console.log(`[Prompt Enhanced] Chinese: ${chinesePrompt} -> English: ${englishPrompt}`); // 方便调试
        return englishPrompt;
    } else {
        throw new Error("LLM returned invalid data for prompt generation.");
    }
}


/**
 * 功能1: 文生图模型调用 - 分步绘画指导 (已修改)
 */
async function generatePaintingSteps(token, theme, difficulty) {
    const stepConfigs = {
        '初级': [
            '第一步轮廓：简单轮廓图，黑色线条，白色背景',
            '第二步基本形状：填充主要形状，简洁明了',
            '第三步细节添加：添加关键特征细节',
            '第四步完成：简单上色，完整图画'
        ],
        '中级': [
            '第一步构图：整体构图规划，轻线条草图',
            '第二步轮廓：清晰轮廓线条，比例准确',
            '第三步基础色：填充基础颜色区块',
            '第四步细节刻画：重要细节强化',
            '第五步完成：整体调整，完整作品'
        ],
        '高级': [
            '第一步构思：初步构思草图',
            '第二步精细线稿：精确的线条描绘',
            '第三步色彩设计：色彩搭配和规划',
            '第四步分层上色：逐层渲染颜色',
            '第五步光影处理：阴影和高光效果',
            '第六步最终完善：细节修正，作品完成'
        ]
    };

    const steps = stepConfigs[difficulty];
    const results = [];

    for (let i = 0; i < steps.length; i++) {
        // [!!!] 修改点 1: 先生成英文提示词
        const chineseStepPrompt = `绘画教学步骤图，主题：${theme}，${steps[i]}，教学示意图，清晰易懂，白色背景，适合小学生学习`;
        const englishPrompt = await generateEnglishPrompt(
            token,
            chineseStepPrompt,
            `This is step ${i + 1} of ${steps.length} in a drawing tutorial for kids. It must be a clear, simple instructional diagram with a white background.`
        );

        // [!!!] 修改点 2: 使用英文提示词调用生图模型
        const response = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token,
            },
            body: JSON.stringify({
                model: "black-forest-labs/FLUX.1-Krea-dev",
                prompt: englishPrompt, // 使用优化后的英文提示词
                size: "1024x1024" // 保持你设置的尺寸
            })
        });

        if (!response.ok) {
             throw new Error(`HTTP error! status: ${response.status} - 步骤 ${i+1} 失败`);
        }

        const result = await response.json();

        if (result.images && result.images[0] && result.images[0].url) {
            results.push({
                step: i + 1,
                description: steps[i].split('：')[1], // 描述部分仍然用中文
                imageUrl: result.images[0].url
            });
        } else {
            throw new Error(`API返回无效数据 - 步骤 ${i+1}`);
        }
    }
    return results;
}

/**
 * 功能2: 文生图模型调用 - 名画风格生成 (已修改)
 */
async function generateArtStyle(token, content, style) {
    const stylePrompts = {
        '梵高': `梵高风格，${content}，浓烈的笔触，鲜艳的色彩，后印象派风格`,
        '毕加索': `毕加索立体主义风格，${content}，几何化的形体，多角度视角`,
        '水墨画': `中国传统水墨画风格，${content}，黑白灰调，写意笔法，留白艺术`,
        '剪纸风格': `中国剪纸艺术风格，${content}，红色为主，轮廓分明，传统图案`,
        '水彩画': `水彩画风格，${content}，透明感，柔和色彩，自然晕染效果`
    };

    const chinesePrompt = stylePrompts[style] || `${style}风格，${content}`;

    // [!!!] 修改点 1: 生成英文提示词
    const englishPrompt = await generateEnglishPrompt(
        token,
        chinesePrompt,
        `A beautiful artwork depicting '${content}' in the distinct style of '${style}'.`
    );

    // [!!!] 修改点 2: 使用英文提示词
    const response = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({
            model: "black-forest-labs/FLUX.1-Krea-dev",
            prompt: englishPrompt, // 使用优化后的英文提示词
            size: "1024x1024"
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (!result.images || !result.images[0] || !result.images[0].url) {
         throw new Error("API返回无效图像数据");
    }

    return {
        imageUrl: result.images[0].url,
        styleDescription: getStyleDescription(style) // 描述仍然用中文
    };
}

/**
 * 功能2: 名画风格 - 辅助函数
 */
function getStyleDescription(style) {
    const descriptions = {
        '梵高': '梵高是荷兰后印象派画家，以鲜艳色彩和强烈笔触著称',
        '毕加索': '毕加索是西班牙画家，创立了立体主义，打破传统透视',
        '水墨画': '水墨画是中国传统绘画，用墨色的浓淡变化表现意境',
        '剪纸风格': '剪纸是中国民间艺术，用剪刀在纸上剪出花纹图案',
        '水彩画': '水彩画用水调和颜料作画，色彩透明，层次丰富'
    };
    // 修复你代码里的一个小拼写错误 '毕加SO' -> '毕加索'
    return descriptions[style] || '这是一种独特的艺术风格';
}

/**
 * 功能3: 多模态大模型调用 - 艺术知识问答 (不变)
 */
function askArtQuestion(token, question) {
    return fetch("https://api-inference.modelscope.cn/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            model: "Qwen/Qwen2.5-72B-Instruct",
            messages: [{
                role: "user",
                content: `请用小学生能理解的简单语言回答这个美术问题：${question}。回答要生动有趣，包含具体例子，长度在100-200字之间。如果涉及艺术家或作品，请简要介绍。`
            }],
            max_tokens: 500,
            temperature: 0.7
        })
    }).then(r => r.json());
}

/**
 * 功能4: 创意灵感生成 (文本 + 图像) (已修改)
 */
async function generateArtIdeas(token, theme) {
    // 首先获取创意方案文本 (这部分不变)
    const textResponse = await fetch("https://api-inference.modelscope.cn/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            model: "Qwen/Qwen2.5-72B-Instruct",
            messages: [{
                role: "user",
                content: `为主题"${theme}"生成3个适合小学生的绘画创意方案。每个方案包括：1.创意名称 2.简要描述（30字内）3.关键元素提示。用JSON格式返回：{"ideas": [{"name": "", "description": "", "elements": ""}]}`
            }],
            max_tokens: 500,
            temperature: 0.8
        })
    });

    if (!textResponse.ok) {
        throw new Error(`获取创意文本失败: ${textResponse.status}`);
    }

    const ideasData = await textResponse.json();
    let ideas;

    try {
        const content = ideasData.choices[0].message.content;
        const jsonString = content.replace(/```json\n|```/g, '').trim();
        ideas = JSON.parse(jsonString).ideas;
    } catch (e) {
        console.error("解析LLM返回的JSON失败:", ideasData.choices[0].message.content);
        throw new Error("模型返回的创意方案格式错误。");
    }

    const imagePromises = ideas.map(async (idea) => {
        const chinesePrompt = `绘画创意示例，${idea.description}，关键元素：${idea.elements}，简洁明了，彩色，适合小学生参考`;
        const englishPrompt = await generateEnglishPrompt(
            token,
            chinesePrompt,
            `A simple, colorful, and cute example illustration for a child's art idea. Title: ${idea.name}`
        );

        try {
            const imageResponse = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token,
                },
                body: JSON.stringify({
                    model: "black-forest-labs/FLUX.1-Krea-dev",
                    prompt: englishPrompt, // 使用优化后的英文提示词
                    size: "1024x1024" // 保持你设置的尺寸
                })
            });

            if (!imageResponse.ok) {
                throw new Error(`Image generation HTTP error: ${imageResponse.status}`);
            }

            const result = await imageResponse.json();
            if (result.images && result.images[0] && result.images[0].url) {
                idea.exampleImage = result.images[0].url;
            } else {
                idea.exampleImage = null; // 生成失败
            }
        } catch (err) {
            console.error(`为 "${idea.name}" 生成图片失败:`, err);
            idea.exampleImage = null; // 出错
        }
        return idea;
    });

    // 等待所有图片生成请求完成
    const completedIdeas = await Promise.all(imagePromises);

    return completedIdeas;
}