// ==========================================================
// 全局变量和 DOM 元素
// ==========================================================
let modelScopeToken = '';
const MODEL_SCOPE_TOKEN_KEY = 'modelscope_api_key';
const apiKeyModal = document.getElementById('api-key-modal');
const apiKeySection = document.getElementById('api-key-section');
const apiKeyInput = document.getElementById('api-key-input');
const saveKeyBtn = document.getElementById('save-key-btn');
const apiError = document.getElementById('api-error');
const homeView = document.getElementById('home-view');
const toolContent = document.getElementById('tool-content');
// 首页功能区
const homeFeaturesSection = document.getElementById('home-features-section');
const globalNav = document.getElementById('global-nav');
const navLinks = globalNav.querySelector('.nav-links');
const allNavButtons = globalNav.querySelectorAll('.nav-btn');
const homeLogoButton = document.getElementById('home-logo-btn');
const homeContentOverlay = homeView.querySelector('.home-content-overlay');
const featureCards = document.querySelectorAll('.feature-card'); // [V7 修改] 它现在位于 homeFeaturesSection 中
const heroSlider = document.querySelector('.slider-container');
const sliderDotsContainer = document.querySelector('.slider-dots');
let heroSlides = [];
let currentHeroSlide = 0;
let slideInterval;
const featurePanels = document.querySelectorAll('.feature-panel');
const footerGuide = document.getElementById('footer-guide');
// ... (功能1-4 DOM元素不变) ...
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
const styleSelect = document.getElementById('style-select');
const styleContentInput = document.getElementById('style-content-input');
const generateStyleBtn = document.getElementById('generate-style-btn');
const styleLoader = document.getElementById('style-loader');
const styleError = document.getElementById('style-error');
const styleResult = document.getElementById('style-result');
const qaInput = document.getElementById('qa-input');
const askQaBtn = document.getElementById('ask-qa-btn');
const qaLoader = document.getElementById('qa-loader');
const qaError = document.getElementById('qa-error');
const qaResult = document.getElementById('qa-result');
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
    initHeroSlider();
    initNavigation();
    initStepGenerator();
    initStyleWorkshop();
    initArtQA();
    initIdeaGenerator();
});

// ==========================================================
// 核心模块 1: API 密钥管理 (不变)
// ==========================================================
function initApiKeyManager() {
    const storedKey = localStorage.getItem(MODEL_SCOPE_TOKEN_KEY);
    if (storedKey) {
        modelScopeToken = storedKey;
        showMainContent();
    } else {
        showApiKeyModal();
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
    apiKeyModal.classList.add('hidden');
    footerGuide.classList.remove('hidden');
    navigateTo('home-view'); // 默认显示首页
}
function showApiKeyModal() {
    apiKeyModal.classList.remove('hidden');
    footerGuide.classList.add('hidden');
}

// ==========================================================
// 核心模块 1.5: 头部画廊滑块 (不变)
// ==========================================================
function initHeroSlider() {
    heroSlides = heroSlider.querySelectorAll('.slide');
    if (heroSlides.length === 0) return;
    heroSlides.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => showHeroSlide(index));
        sliderDotsContainer.appendChild(dot);
    });
    startSlideShow();
}
function showHeroSlide(index) { heroSlides.forEach((slide, i) => slide.classList.toggle('active', i === index)); sliderDotsContainer.querySelectorAll('.dot').forEach((dot, i) => dot.classList.toggle('active', i === index)); currentHeroSlide = index; }
function nextHeroSlide() { const nextIndex = (currentHeroSlide + 1) % heroSlides.length; showHeroSlide(nextIndex); }
function startSlideShow() { showHeroSlide(0); clearInterval(slideInterval); slideInterval = setInterval(nextHeroSlide, 5000); }


// ==========================================================
// [V7 修复] 核心模块 2: 主导航逻辑
// ==========================================================
function initNavigation() {
    navLinks.addEventListener('click', (e) => { if (e.target.tagName === 'BUTTON') { const targetId = e.target.dataset.target; navigateTo(targetId); } });
    homeLogoButton.addEventListener('click', (e) => { e.preventDefault(); navigateTo('home-view'); });
    featureCards.forEach(card => { card.addEventListener('click', () => { const targetId = card.dataset.target; navigateTo(targetId); }); });
}

/**
 * [V7 修复] 核心导航函数
 * @param {string} targetId - 要导航到的视图/面板的ID
 */
function navigateTo(targetId) {

    // 1. 更新导航栏按钮 'active' 状态
    allNavButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.target === targetId);
    });

    // 2. 更新 body 类以控制背景
    const isHomePage = (targetId === 'home-view');
    if (isHomePage) {
        document.body.classList.add('showing-home');
        document.body.classList.remove('showing-tools');
    } else {
        document.body.classList.add('showing-tools');
        document.body.classList.remove('showing-home');
    }

    // 3. [V7 核心修复] 切换首页和工具区
    homeView.style.display = isHomePage ? 'flex' : 'none'; // 首页画廊
    homeFeaturesSection.style.display = isHomePage ? 'block' : 'none'; // 首页功能区
    toolContent.style.display = isHomePage ? 'none' : 'block'; // 工具区

    // 4. 如果进入工具区，切换内部面板
    if (!isHomePage) {
        let panelFound = false;
        featurePanels.forEach(panel => {
            const shouldShow = (panel.id === targetId);
            panel.classList.toggle('hidden', !shouldShow);
            panel.classList.toggle('active', shouldShow);
            if(shouldShow) panelFound = true;
        });
        if (!panelFound) {
             console.warn(`Panel with id "${targetId}" not found. Hiding tool content.`);
             // 如果找不到面板，也隐藏工具区
             toolContent.style.display = 'none';
        }
    } else {
         // 回到首页时，确保所有工具面板都隐藏
         featurePanels.forEach(panel => {
            panel.classList.add('hidden');
            panel.classList.remove('active');
        });
    }

    window.scrollTo(0, 0);
}


// ==========================================================
// 核心模块 3-6: 工具功能 (JS逻辑不变)
// ==========================================================
// 模块 3: 分步绘画
function initStepGenerator() { generateStepsBtn.addEventListener('click', async () => { const theme = themeInput.value.trim(); const difficulty = difficultySelect.value; if (!theme) { stepsError.textContent = '请输入绘画主题'; return; } toggleUIState(generateStepsBtn, stepsLoader, stepsError, true); stepsResult.classList.add('hidden'); try { const results = await generatePaintingSteps(modelScopeToken, theme, difficulty); if (!results || results.length === 0) { throw new Error("未能生成绘画步骤。"); } displayPaintingSteps(results); } catch (error) { stepsError.textContent = `生成失败: ${error.message}`; console.error(error); } finally { toggleUIState(generateStepsBtn, stepsLoader, stepsError, false); } }); prevStepBtn.addEventListener('click', () => { currentSlideIndex = (currentSlideIndex - 1 + slides.length) % slides.length; showSlide(currentSlideIndex); }); nextStepBtn.addEventListener('click', () => { currentSlideIndex = (currentSlideIndex + 1) % slides.length; showSlide(currentSlideIndex); }); }
function displayPaintingSteps(steps) { slideshowContent.innerHTML = ''; slides = []; steps.forEach((step) => { const slide = document.createElement('div'); slide.className = 'slide'; const img = document.createElement('img'); img.src = step.imageUrl; img.alt = `步骤 ${step.step}: ${step.description}`; const desc = document.createElement('p'); desc.textContent = `第 ${step.step} 步：${step.description}`; slide.appendChild(img); slide.appendChild(desc); slideshowContent.appendChild(slide); slides.push(slide); }); currentSlideIndex = 0; showSlide(currentSlideIndex); stepsResult.classList.remove('hidden'); }
function showSlide(index) { slides.forEach((slide, i) => slide.classList.toggle('active', i === index)); stepCounter.textContent = `步骤 ${index + 1} / ${slides.length}`; }
// 模块 4: 风格工坊
function initStyleWorkshop() { generateStyleBtn.addEventListener('click', async () => { const style = styleSelect.value; const content = styleContentInput.value.trim(); if (!content) { styleError.textContent = '请输入绘制内容'; return; } toggleUIState(generateStyleBtn, styleLoader, styleError, true); styleResult.classList.add('hidden'); try { const result = await generateArtStyle(modelScopeToken, content, style); displayArtStyle(result); } catch (error) { styleError.textContent = `生成失败: ${error.message}`; console.error(error); } finally { toggleUIState(generateStyleBtn, styleLoader, styleError, false); } }); }
function displayArtStyle(result) { styleResult.innerHTML = ''; const img = document.createElement('img'); img.src = result.imageUrl; img.alt = `风格画作: ${styleContentInput.value.trim()}`; const desc = document.createElement('p'); desc.className = 'style-desc'; desc.textContent = result.styleDescription; styleResult.appendChild(img); styleResult.appendChild(desc); styleResult.classList.remove('hidden'); }
// 模块 5: 艺术问答
function initArtQA() { askQaBtn.addEventListener('click', async () => { const question = qaInput.value.trim(); if (!question) { qaError.textContent = '请输入你的问题'; return; } toggleUIState(askQaBtn, qaLoader, qaError, true); qaResult.classList.add('hidden'); try { const result = await askArtQuestion(modelScopeToken, question); if (result.choices && result.choices[0] && result.choices[0].message) { displayQAResult(result.choices[0].message.content); } else if (result.message) { throw new Error(result.message); } else { throw new Error("未能获取回答。"); } } catch (error) { qaError.textContent = `回答失败: ${error.message}`; console.error(error); } finally { toggleUIState(askQaBtn, qaLoader, qaError, false); } }); }
function displayQAResult(answer) { qaResult.textContent = answer; qaResult.classList.remove('hidden'); }
// 模块 6: 创意灵感
function initIdeaGenerator() { generateIdeasBtn.addEventListener('click', async () => { const theme = ideaThemeInput.value.trim(); if (!theme) { ideasError.textContent = '请输入灵感主题'; return; } toggleUIState(generateIdeasBtn, ideasLoader, ideasError, true); ideasResult.classList.add('hidden'); try { const ideas = await generateArtIdeas(modelScopeToken, theme); displayArtIdeas(ideas); } catch (error) { ideasError.textContent = `生成失败: ${error.message}`; console.error(error); } finally { toggleUIState(generateIdeasBtn, ideasLoader, ideasError, false); } }); }
function displayArtIdeas(ideas) { ideasResult.innerHTML = ''; if (!ideas || ideas.length === 0) { ideasError.textContent = '未能解析创意。'; return; } ideas.forEach(idea => { const card = document.createElement('div'); card.className = 'idea-card'; const img = document.createElement('img'); img.src = idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image'; img.alt = idea.name; const title = document.createElement('h3'); title.textContent = idea.name; const desc = document.createElement('p'); desc.textContent = idea.description; const elements = document.createElement('small'); elements.textContent = `关键元素: ${idea.elements}`; card.appendChild(img); card.appendChild(title); card.appendChild(desc); card.appendChild(elements); ideasResult.appendChild(card); }); ideasResult.classList.remove('hidden'); }


// ==========================================================
// 辅助函数 (不变)
// ==========================================================
function toggleUIState(button, loader, errorEl, isLoading) { if (isLoading) { button.disabled = true; loader.classList.remove('hidden'); errorEl.textContent = ''; } else { button.disabled = false; loader.classList.add('hidden'); } }

// ==========================================================
// AI 调用函数 (修改)
// ==========================================================

/**
 * [修改] 优化了系统提示词
 */
async function generateEnglishPrompt(token, chinesePrompt, contextDescription) {
    // [关键] 修改 systemPrompt，强制要求只返回提示词
    const systemPrompt = `You are a professional AI painting prompt engineer. Your task is to translate the user's Chinese description into a concise, effective English prompt for an image generation model (like FLUX).
ONLY return the English prompt itself, without any conversational text, markdown, greetings, or explanations.
Context: ${contextDescription}`;

    const userPrompt = `Chinese Description: "${chinesePrompt}"`;

    const response = await fetch("https://api-inference.modelscope.cn/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            model: "Qwen/Qwen2.5-72B-Instruct",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt }
            ],
            max_tokens: 200,
            temperature: 0.5
        })
    });

    if (!response.ok) {
        throw new Error(`LLM prompt generation failed: ${response.status}`);
    }
    const data = await response.json();
    if (data.choices && data.choices[0] && data.choices[0].message) {
        const englishPrompt = data.choices[0].message.content.replace(/"/g, '').trim();
        console.log(`[Prompt Enhanced] Chinese: ${chinesePrompt} -> English: ${englishPrompt}`);
        return englishPrompt;
    } else {
        throw new Error("LLM returned invalid data for prompt generation.");
    }
}


async function generatePaintingSteps(token, theme, difficulty) {
    const stepConfigs = {
        '初级': ['第一步：画一个简单的轮廓', '第二步：添加五官', '第三步：画上身体', '第四步：涂上颜色'],
        '中级': ['第一步：构思草图', '第二步：明确主体轮廓', '第三步：添加背景元素', '第四步：细化阴影', '第五步：上色和高光'],
        '高级': ['第一步：基础构图', '第二步：主体轮廓', '第三步：添加主要细节', '第四步：深入刻画（例如：阴影）', '第五步：添加背景和环境', '第六步：最终上色和高光']
    };

    const steps = stepConfigs[difficulty];
    const results = [];

    // 1. [关键] 在循环外定义一个固定的Seed
    const constantSeed = Math.floor(Math.random() * 2**31 - 1);

    let previousImageUrl = null; // 用于存储上一步的图像URL

    // 2. [关键] 使用 'for...of' 循环来确保串行（等待）
    for (let i = 0; i < steps.length; i++) {

        const chineseStepPrompt = `绘画教学步骤图，主题：${theme}，${steps[i]}`;
        const englishPrompt = await generateEnglishPrompt(token, chineseStepPrompt, `This is step ${i + 1}/${steps.length} of a drawing tutorial.`);

        // 3. 构建请求体
        const requestBody = {
            model: "black-forest-labs/FLUX.1-Krea-dev",
            prompt: englishPrompt,
            seed: constantSeed, // [关键] 每次都使用同一个Seed
            size: "1024x1024" // 注意：FLUX文档说最大1024x1024
            // 可以在这里添加 negative_prompt, steps, guidance 等
        };

        // 4. [关键] 从第二步开始，传入上一步的图像
        if (previousImageUrl) {
            requestBody.image_url = previousImageUrl;
        }

        try {
            // 5. [关键] 直接调用同步API (像 generateArtStyle 一样)
            const response = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                let errorMsg = `HTTP error! status: ${response.status}`;
                try {
                    const errData = await response.json();
                    errorMsg = errData.message || JSON.stringify(errData);
                } catch(e) {}
                throw new Error(errorMsg);
            }

            const result = await response.json();

            // 6. [关键] 从同步响应中获取图像URL (注意: 字段是 'images')
            if (!result.images || !result.images[0] || !result.images[0].url) {
                throw new Error("API返回无效图像数据");
            }

            const imageUrl = result.images[0].url;

            results.push({
                step: i + 1,
                description: steps[i].split('：')[1] || steps[i],
                imageUrl: imageUrl
            });
            previousImageUrl = imageUrl; // [关键] 保存当前URL，供下一步使用

        } catch (error) {
            // 如果一步失败，整个链条都失败
            console.error(error);
            throw new Error(`在步骤 ${i+1} ("${steps[i]}") 生成时失败: ${error.message}`);
        }
    }

    return results; // 返回完整的、一致的步骤数组
}

// [不变] generateArtStyle 已在使用同步模式
async function generateArtStyle(token, content, style) {
    /* ... */
    const stylePrompts = {
        '梵高': `梵高风格，充满活力的笔触，厚涂颜料，主题：${content}`,
        '毕加索': `毕加索立体主义风格，破碎的视角，几何形状，主题：${content}`,
        '水墨画': `中国传统水墨画风格，黑白，留白，意境，主题：${content}`,
        '剪纸风格': `中国剪纸风格，鲜艳的红色，镂空，对称，主题：${content}`,
        '水彩画': `水彩画风格，透明的颜色，湿画法，主题：${content}`
    };
    const chinesePrompt = stylePrompts[style] || `${style}风格，${content}`;
    const englishPrompt = await generateEnglishPrompt(token, chinesePrompt, `A beautiful artwork in the style of ${style}.`);

    const response = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            model: "black-forest-labs/FLUX.1-Krea-dev",
            prompt: englishPrompt,
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
        styleDescription: getStyleDescription(style)
    };
}

function getStyleDescription(style) {
    const descriptions = {
        '梵高': '梵高：使用旋转、充满活力的笔触和厚重的颜料来表达情感。',
        '毕加SO': '毕加索：通过将物体分解成几何形状来从多个角度展示它们。',
        '水墨画': '水墨画：利用墨色的浓淡变化和笔触的力度来传达意境。',
        '剪纸风格': '剪纸风格：中国传统的民间艺术，通常使用红色纸张和镂空图案。',
        '水彩画': '水彩画：一种使用透明颜料和水在纸上作画的技法。'
    };
    return descriptions[style] || '这是一种独特的艺术风格';
}

// [不变] askArtQuestion
function askArtQuestion(token, question) {
    /* ... */
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
                content: `你是一位友好的艺术老师。请用小学生能轻松理解的、简洁的语言（大约100-150字）回答以下问题：${question}。不要使用复杂的专业术语。`
            }],
            max_tokens: 500,
            temperature: 0.7
        })
    }).then(r => r.json());
}

// [不变] generateArtIdeas
async function generateArtIdeas(token, theme) {
    /* ... */
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
                content: `为主题"${theme}"生成3个绘画创意灵感，适合小学生。请使用严格的JSON格式返回，包含一个 'ideas' 数组，每个对象有 'name' (创意名称), 'description' (一句话描述), 'elements' (3个关键词，用逗号分隔)。
                例如: {"ideas": [{"name": "...", "description": "...", "elements": "..."}]}`
            }],
            max_tokens: 500,
            temperature: 0.8
        })
    });
    if (!textResponse.ok) {
        throw new Error(`获取创意文本失败`);
    }
    const ideasData = await textResponse.json();
    let ideas;
    try {
        const content = ideasData.choices[0].message.content;
        const jsonString = content.replace(/```json\n|```/g, '').trim();
        ideas = JSON.parse(jsonString).ideas;
    } catch (e) {
        throw new Error("模型返回的创意方案格式错误。");
    }

    // [不变] 创意灵感的图片生成 (已在使用同步模式)
    const imagePromises = ideas.map(async (idea) => {
        const chinesePrompt = `绘画创意示例：${idea.name}，${idea.description}，包含元素：${idea.elements}`;
        const englishPrompt = await generateEnglishPrompt(token, chinesePrompt, `A simple, colorful illustration for a child, based on an art idea.`);
        try {
            const imageResponse = await fetch("https://api-inference.modelscope.cn/v1/images/generations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    model: "black-forest-labs/FLUX.1-Krea-dev",
                    prompt: englishPrompt,
                    size: "1024x1024" // 注意: 创意灵感卡片是 1:1 比例
                })
            });
            if (!imageResponse.ok) {
                throw new Error(`Image generation HTTP error`);
            }
            const result = await imageResponse.json();
            idea.exampleImage = (result.images && result.images[0] && result.images[0].url) ? result.images[0].url : null;
        } catch (err) {
            console.error(`为 "${idea.name}" 生成图片失败:`, err);
            idea.exampleImage = null;
        }
        return idea;
    });
    return await Promise.all(imagePromises);
}