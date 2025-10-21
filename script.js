// ==========================================================
// 全局变量和 DOM 元素
// ==========================================================

const BACKEND_URL = 'http://localhost:5000';

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

/**
 * [新增] 辅助函数：调用后端检查 session 状态
 */
async function checkKeyValidity() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/check_key`, {
            method: 'GET',
            credentials: 'include' // [关键] 必须发送 cookie 才能检查 session
        });

        // 如果 response.ok 是 false (例如 401)，
        // response.ok 会是 false，fetch 不会抛出错误，但 !response.ok 是 true
        if (!response.ok) {
            throw new Error('Session key not valid');
        }

        // 如果服务器返回 200 OK，则 session 有效
        return true;

    } catch (error) {
        // 网络错误或 401 错误都会导致验证失败
        console.warn("Key validity check failed:", error.message);
        throw error;
    }
}


function initApiKeyManager() {

    // 1. [不变] 绑定保存按钮事件
    saveKeyBtn.addEventListener('click', async () => {
        const key = apiKeyInput.value.trim();
        if (!key) {
            apiError.textContent = 'API KEY 不能为空';
            return;
        }

        try {
            // [不变] 将 Key 发送到后端安全存储
            const response = await fetch(`${BACKEND_URL}/api/set_key`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: key }),
                credentials: 'include' // [关键] 必须发送 cookie 才能使用 session
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || '设置Key失败');
            }

            // [不变] 成功后，在本地设置一个“标志”
            localStorage.setItem(MODEL_SCOPE_TOKEN_KEY, 'true'); // 只存一个标志
            showMainContent();
            apiError.textContent = '';

        } catch (error) {
            apiError.textContent = `错误: ${error.message}`;
        }
    });

    // 2. [修改] 使用 IIFE (立即执行的异步函数) 来处理页面加载时的严谨验证
    (async () => {
        const storedKeyFlag = localStorage.getItem(MODEL_SCOPE_TOKEN_KEY);

        if (storedKeyFlag) {
            // 标志存在，我们必须验证它
            try {
                // [关键] 调用后端验证
                await checkKeyValidity();

                // 验证成功 (没有抛出错误)，显示主内容
                showMainContent();

            } catch (error) {
                // 验证失败 (session 过期等)，显示模态框
                console.warn("Session expired or invalid. Please re-enter key.");
                showApiKeyModal(); // 调用我们修改后的 showApiKeyModal
            }
        } else {
            // 标志不存在，直接显示模态框
            showApiKeyModal();
        }
    })();
}
function showMainContent() {
    apiKeyModal.classList.add('hidden');
    footerGuide.classList.remove('hidden');
    navigateTo('home-view'); // 默认显示首页
}
function showApiKeyModal() {
    apiKeyModal.classList.remove('hidden');
    footerGuide.classList.add('hidden');
    localStorage.removeItem(MODEL_SCOPE_TOKEN_KEY);
}

// ==========================================================
// 核心模块 1.5: 头部画廊滑块
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
 * 核心导航函数
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
// 核心模块 3-6: 工具功能
// ==========================================================
// 模块 3: 分步绘画
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
            // [修复] 移除 modelScopeToken 参数
            const results = await generatePaintingSteps(theme, difficulty);
            if (!results || results.length === 0) {
                throw new Error("未能生成绘画步骤。");
            }
            displayPaintingSteps(results);
        } catch (error) {
            stepsError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateStepsBtn, stepsLoader, stepsError, false);
        }
    });
    prevStepBtn.addEventListener('click', () => { currentSlideIndex = (currentSlideIndex - 1 + slides.length) % slides.length; showSlide(currentSlideIndex); });
    nextStepBtn.addEventListener('click', () => { currentSlideIndex = (currentSlideIndex + 1) % slides.length; showSlide(currentSlideIndex); });
}function displayPaintingSteps(steps) { slideshowContent.innerHTML = ''; slides = []; steps.forEach((step) => { const slide = document.createElement('div'); slide.className = 'slide'; const img = document.createElement('img'); img.src = step.imageUrl; img.alt = `步骤 ${step.step}: ${step.description}`; const desc = document.createElement('p'); desc.textContent = `第 ${step.step} 步：${step.description}`; slide.appendChild(img); slide.appendChild(desc); slideshowContent.appendChild(slide); slides.push(slide); }); currentSlideIndex = 0; showSlide(currentSlideIndex); stepsResult.classList.remove('hidden'); }
function showSlide(index) { slides.forEach((slide, i) => slide.classList.toggle('active', i === index)); stepCounter.textContent = `步骤 ${index + 1} / ${slides.length}`; }
// 模块 4: 风格工坊
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
            // [修复] 移除 modelScopeToken 参数
            const result = await generateArtStyle(content, style);
            displayArtStyle(result);
        } catch (error) {
            styleError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateStyleBtn, styleLoader, styleError, false);
        }
    });
}function displayArtStyle(result) { styleResult.innerHTML = ''; const img = document.createElement('img'); img.src = result.imageUrl; img.alt = `风格画作: ${styleContentInput.value.trim()}`; const desc = document.createElement('p'); desc.className = 'style-desc'; desc.textContent = result.styleDescription; styleResult.appendChild(img); styleResult.appendChild(desc); styleResult.classList.remove('hidden'); }
// 模块 5: 艺术问答
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
            // [修复] 移除 modelScopeToken 参数
            const result = await askArtQuestion(question);
            if (result.choices && result.choices[0] && result.choices[0].message) {
                displayQAResult(result.choices[0].message.content);
            } else if (result.message) {
                throw new Error(result.message);
            } else {
                throw new Error("未能获取回答。");
            }
        } catch (error) {
            qaError.textContent = `回答失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(askQaBtn, qaLoader, qaError, false);
        }
    });
}function displayQAResult(answer) { qaResult.textContent = answer; qaResult.classList.remove('hidden'); }
// 模块 6: 创意灵感
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
            // [修复] 移除 modelScopeToken 参数
            const ideas = await generateArtIdeas(theme);
            displayArtIdeas(ideas);
        } catch (error) {
            ideasError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateIdeasBtn, ideasLoader, ideasError, false);
        }
    });
}function displayArtIdeas(ideas) { ideasResult.innerHTML = ''; if (!ideas || ideas.length === 0) { ideasError.textContent = '未能解析创意。'; return; } ideas.forEach(idea => { const card = document.createElement('div'); card.className = 'idea-card'; const img = document.createElement('img'); img.src = idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image'; img.alt = idea.name; const title = document.createElement('h3'); title.textContent = idea.name; const desc = document.createElement('p'); desc.textContent = idea.description; const elements = document.createElement('small'); elements.textContent = `关键元素: ${idea.elements}`; card.appendChild(img); card.appendChild(title); card.appendChild(desc); card.appendChild(elements); ideasResult.appendChild(card); }); ideasResult.classList.remove('hidden'); }


// ==========================================================
// 辅助函数 (不变)
// ==========================================================
function toggleUIState(button, loader, errorEl, isLoading) { if (isLoading) { button.disabled = true; loader.classList.remove('hidden'); errorEl.textContent = ''; } else { button.disabled = false; loader.classList.add('hidden'); } }

// ==========================================================
// AI 调用函数
// ==========================================================

// 辅助函数：处理所有到后端的 fetch 请求
async function fetchFromBackend(endpoint, body) {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body),
        credentials: 'include' // [关键] 必须发送 cookie 才能使用 session
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `请求失败: ${response.status}`);
    }

    return response.json();
}


async function generatePaintingSteps(theme, difficulty) {
    const data = await fetchFromBackend('/api/generate-steps', { theme, difficulty });
    return data.steps; // 后端直接返回了 {steps: [...]}
}

async function generateArtStyle(content, style) {
    return fetchFromBackend('/api/generate-style', { content, style });
}


async function askArtQuestion(question) {
    return fetchFromBackend('/api/ask-question', { question });
}

async function generateArtIdeas(theme) {
    return fetchFromBackend('/api/generate-ideas', { theme });
}