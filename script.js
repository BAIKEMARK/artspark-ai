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
const featureCards = document.querySelectorAll('.feature-card');
const heroSlider = document.querySelector('.slider-container');
const sliderDotsContainer = document.querySelector('.slider-dots');
let heroSlides = [];
let currentHeroSlide = 0;
let slideInterval;
const featurePanels = document.querySelectorAll('.feature-panel');
const footerGuide = document.getElementById('footer-guide');

// 功能一：AI智能上色
const coloringFileInput = document.getElementById('coloring-file-input');
const coloringPreview = document.getElementById('coloring-preview');
const coloringPromptInput = document.getElementById('coloring-prompt-input');
const generateColoringBtn = document.getElementById('generate-coloring-btn');
const coloringLoader = document.getElementById('coloring-loader');
const coloringError = document.getElementById('coloring-error');
const coloringResult = document.getElementById('coloring-result');

// 功能二：创意风格工坊
const styleSelect = document.getElementById('style-select');
const styleFileInput = document.getElementById('style-file-input');
const stylePreview = document.getElementById('style-preview');
const styleContentInput = document.getElementById('style-content-input');
const generateStyleBtn = document.getElementById('generate-style-btn');
const styleLoader = document.getElementById('style-loader');
const styleError = document.getElementById('style-error');
const styleResult = document.getElementById('style-result');

// 功能三：AI自画像
const portraitFileInput = document.getElementById('portrait-file-input');
const portraitPreview = document.getElementById('portrait-preview');
const portraitStyleInput = document.getElementById('portrait-style-input');
const generatePortraitBtn = document.getElementById('generate-portrait-btn');
const portraitLoader = document.getElementById('portrait-loader');
const portraitError = document.getElementById('portrait-error');
const portraitResult = document.getElementById('portrait-result');

// 功能四：艺术融合
const fusionContentInput = document.getElementById('fusion-content-input');
const fusionContentPreview = document.getElementById('fusion-content-preview');
const fusionStyleInput = document.getElementById('fusion-style-input');
const fusionStylePreview = document.getElementById('fusion-style-preview');
const generateFusionBtn = document.getElementById('generate-fusion-btn');
const fusionLoader = document.getElementById('fusion-loader');
const fusionError = document.getElementById('fusion-error');
const fusionResult = document.getElementById('fusion-result');

// 功能五：艺术问答
const qaInput = document.getElementById('qa-input');
const askQaBtn = document.getElementById('ask-qa-btn');
const qaLoader = document.getElementById('qa-loader');
const qaError = document.getElementById('qa-error');
const qaResult = document.getElementById('qa-result');

// 功能六：创意灵感
const ideaThemeInput = document.getElementById('idea-theme-input');
const generateIdeasBtn = document.getElementById('generate-ideas-btn');
const ideasLoader = document.getElementById('ideas-loader');
const ideasError = document.getElementById('ideas-error');
const ideasResult = document.getElementById('ideas-result');

// [移除] 旧的分步绘画DOM
// const themeInput = document.getElementById('theme-input');
// ... (等)


// ==========================================================
// 初始化
// ==========================================================
document.addEventListener('DOMContentLoaded', () => {
    initApiKeyManager();
    initHeroSlider();
    initNavigation();

    // 初始化所有新功能
    initColoring();       // (新)
    initStyleWorkshop();  // (修改)
    initSelfPortrait();   // (新)
    initArtFusion();      // (新)
    initArtQA();          // (保留)
    initIdeaGenerator();  // (保留)

    // 为所有文件输入框绑定预览
    setupImagePreview(coloringFileInput, coloringPreview);
    setupImagePreview(styleFileInput, stylePreview);
    setupImagePreview(portraitFileInput, portraitPreview);
    setupImagePreview(fusionContentInput, fusionContentPreview);
    setupImagePreview(fusionStyleInput, fusionStylePreview);
});

// ==========================================================
// 核心模块 1: API 密钥管理 (不变)
// ==========================================================

async function checkKeyValidity() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/check_key`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Session key not valid');
        }
        return true;
    } catch (error) {
        console.warn("Key validity check failed:", error.message);
        throw error;
    }
}

function initApiKeyManager() {
    saveKeyBtn.addEventListener('click', async () => {
        const key = apiKeyInput.value.trim();
        if (!key) {
            apiError.textContent = 'API KEY 不能为空';
            return;
        }
        try {
            const response = await fetch(`${BACKEND_URL}/api/set_key`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: key }),
                credentials: 'include'
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || '设置Key失败');
            }
            localStorage.setItem(MODEL_SCOPE_TOKEN_KEY, 'true');
            showMainContent();
            apiError.textContent = '';
        } catch (error) {
            apiError.textContent = `错误: ${error.message}`;
        }
    });

    (async () => {
        const storedKeyFlag = localStorage.getItem(MODEL_SCOPE_TOKEN_KEY);
        if (storedKeyFlag) {
            try {
                await checkKeyValidity();
                showMainContent();
            } catch (error) {
                console.warn("Session expired or invalid. Please re-enter key.");
                showApiKeyModal();
            }
        } else {
            showApiKeyModal();
        }
    })();
}
function showMainContent() {
    apiKeyModal.classList.add('hidden');
    footerGuide.classList.remove('hidden');
    navigateTo('home-view');
}
function showApiKeyModal() {
    apiKeyModal.classList.remove('hidden');
    footerGuide.classList.add('hidden');
    localStorage.removeItem(MODEL_SCOPE_TOKEN_KEY);
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
// 核心模块 2: 主导航逻辑 (不变)
// ==========================================================
function initNavigation() {
    navLinks.addEventListener('click', (e) => { if (e.target.tagName === 'BUTTON') { const targetId = e.target.dataset.target; navigateTo(targetId); } });
    homeLogoButton.addEventListener('click', (e) => { e.preventDefault(); navigateTo('home-view'); });
    // 确保首页卡片导航正确
    featureCards.forEach(card => {
        card.addEventListener('click', () => {
            const targetId = card.dataset.target;
            if(targetId) { // 检查 data-target 是否存在
                navigateTo(targetId);
            }
        });
    });
}
function navigateTo(targetId) {
    allNavButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.target === targetId);
    });
    const isHomePage = (targetId === 'home-view');
    if (isHomePage) {
        document.body.classList.add('showing-home');
        document.body.classList.remove('showing-tools');
    } else {
        document.body.classList.add('showing-tools');
        document.body.classList.remove('showing-home');
    }
    homeView.style.display = isHomePage ? 'flex' : 'none';
    homeFeaturesSection.style.display = isHomePage ? 'block' : 'none';
    toolContent.style.display = isHomePage ? 'none' : 'block';
    if (!isHomePage) {
        let panelFound = false;
        featurePanels.forEach(panel => {
            const shouldShow = (panel.id === targetId);
            panel.classList.toggle('hidden', !shouldShow);
            panel.classList.toggle('active', shouldShow);
            if(shouldShow) panelFound = true;
        });
        if (!panelFound) {
             console.warn(`Panel with id "${targetId}" not found.`);
             toolContent.style.display = 'none';
        }
    } else {
         featurePanels.forEach(panel => {
            panel.classList.add('hidden');
            panel.classList.remove('active');
        });
    }
    window.scrollTo(0, 0);
}


// ==========================================================
// 核心模块 3-8: 工具功能 (重构)
// ==========================================================

// 模块 3: AI智能上色
function initColoring() {
    generateColoringBtn.addEventListener('click', async () => {
        const file = coloringFileInput.files[0];
        const prompt = coloringPromptInput.value.trim();

        if (!file) {
            coloringError.textContent = '请上传一张线稿图片';
            return;
        }
        if (!prompt) {
            coloringError.textContent = '请输入上色风格';
            return;
        }

        toggleUIState(generateColoringBtn, coloringLoader, coloringError, true);
        coloringResult.classList.add('hidden');

        try {
            const base64_image = await fileToBase64(file);
            const result = await generateColoring(base64_image, prompt);
            displaySingleImageResult(coloringResult, result.imageUrl, "AI上色作品");
        } catch (error) {
            coloringError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateColoringBtn, coloringLoader, coloringError, false);
        }
    });
}

// 模块 4: 创意风格工坊
function initStyleWorkshop() {
    generateStyleBtn.addEventListener('click', async () => {
        const style = styleSelect.value;
        const content = styleContentInput.value.trim();
        const file = styleFileInput.files[0];

        // 至少需要一个输入
        if (!content && !file) {
            styleError.textContent = '请输入绘制内容或上传一张草图';
            return;
        }

        toggleUIState(generateStyleBtn, styleLoader, styleError, true);
        styleResult.classList.add('hidden');

        try {
            // [关键] 动态处理 Base64
            let base64_image = null;
            if (file) {
                base64_image = await fileToBase64(file);
            }

            const result = await generateArtStyle(content, style, base64_image);
            displayArtStyle(result); // 复用旧的显示函数
        } catch (error) {
            styleError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateStyleBtn, styleLoader, styleError, false);
        }
    });
}
// (复用)
function displayArtStyle(result) {
    styleResult.innerHTML = '';
    const img = document.createElement('img');
    img.src = result.imageUrl;
    img.alt = `风格画作`;
    const desc = document.createElement('p');
    desc.className = 'style-desc';
    desc.textContent = result.styleDescription;
    styleResult.appendChild(img);
    styleResult.appendChild(desc);
    styleResult.classList.remove('hidden');
}

// 模块 5: AI自画像
function initSelfPortrait() {
    generatePortraitBtn.addEventListener('click', async () => {
        const file = portraitFileInput.files[0];
        const style_prompt = portraitStyleInput.value.trim();

        if (!file) {
            portraitError.textContent = '请上传一张你的照片';
            return;
        }
        if (!style_prompt) {
            portraitError.textContent = '请输入你想要的风格';
            return;
        }

        toggleUIState(generatePortraitBtn, portraitLoader, portraitError, true);
        portraitResult.classList.add('hidden');

        try {
            const base64_image = await fileToBase64(file);
            const result = await generateSelfPortrait(base64_image, style_prompt);
            displaySingleImageResult(portraitResult, result.imageUrl, "AI自画像");
        } catch (error) {
            portraitError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generatePortraitBtn, portraitLoader, portraitError, false);
        }
    });
}

// 模块 6: 艺术融合
function initArtFusion() {
    generateFusionBtn.addEventListener('click', async () => {
        const contentFile = fusionContentInput.files[0];
        const styleFile = fusionStyleInput.files[0];

        if (!contentFile) {
            fusionError.textContent = '请上传内容图片';
            return;
        }
        if (!styleFile) {
            fusionError.textContent = '请上传风格图片';
            return;
        }

        toggleUIState(generateFusionBtn, fusionLoader, fusionError, true);
        fusionResult.classList.add('hidden');

        try {
            const content_image = await fileToBase64(contentFile);
            const style_image = await fileToBase64(styleFile);
            const result = await generateArtFusion(content_image, style_image);
            displaySingleImageResult(fusionResult, result.imageUrl, "艺术融合作品");
        } catch (error) {
            fusionError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateFusionBtn, fusionLoader, fusionError, false);
        }
    });
}

// 模块 7: 艺术问答
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
}
function displayQAResult(answer) { qaResult.textContent = answer; qaResult.classList.remove('hidden'); }

// 模块 8: 创意灵感
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
            const ideas = await generateArtIdeas(theme);
            displayArtIdeas(ideas);
        } catch (error) {
            ideasError.textContent = `生成失败: ${error.message}`;
            console.error(error);
        } finally {
            toggleUIState(generateIdeasBtn, ideasLoader, ideasError, false);
        }
    });
}
function displayArtIdeas(ideas) { ideasResult.innerHTML = ''; if (!ideas || ideas.length === 0) { ideasError.textContent = '未能解析创意。'; return; } ideas.forEach(idea => { const card = document.createElement('div'); card.className = 'idea-card'; const img = document.createElement('img'); img.src = idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image'; img.alt = idea.name; const title = document.createElement('h3'); title.textContent = idea.name; const desc = document.createElement('p'); desc.textContent = idea.description; const elements = document.createElement('small'); elements.textContent = `关键元素: ${idea.elements}`; card.appendChild(img); card.appendChild(title); card.appendChild(desc); card.appendChild(elements); ideasResult.appendChild(card); }); ideasResult.classList.remove('hidden'); }

// ==========================================================
// 辅助函数
// ==========================================================
function toggleUIState(button, loader, errorEl, isLoading) { if (isLoading) { button.disabled = true; loader.classList.remove('hidden'); errorEl.textContent = ''; } else { button.disabled = false; loader.classList.add('hidden'); } }

/**
 * 辅助函数：将文件转为 Base64 Data URL
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result); // e.g., "data:image/png;base64,..."
        reader.onerror = error => reject(error);
    });
}

/**
 * 辅助函数：设置图片上传预览
 */
function setupImagePreview(fileInput, previewElement) {
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewElement.src = e.target.result;
                previewElement.style.display = 'block';
            }
            reader.readAsDataURL(file);
        } else {
            previewElement.src = '';
            previewElement.style.display = 'none';
        }
    });
}

/**
 * 辅助函数：用于显示单张图片的通用函数
 */
function displaySingleImageResult(resultContainer, imageUrl, altText) {
    resultContainer.innerHTML = ''; // 清空旧结果
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = altText;
    img.style.maxWidth = '100%';
    img.style.maxHeight = '512px';
    img.style.borderRadius = '8px';
    resultContainer.appendChild(img);
    resultContainer.classList.remove('hidden');
}


// ==========================================================
// AI 调用函数 (重构)
// ==========================================================

// 辅助函数：处理所有到后端的 fetch 请求
async function fetchFromBackend(endpoint, body) {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body),
        credentials: 'include'
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `请求失败: ${response.status}`);
    }

    return response.json();
}

// 调用 "AI智能上色"
async function generateColoring(base64_image, prompt) {
    return fetchFromBackend('/api/colorize-lineart', { base64_image, prompt });
}

// 调用 "创意风格工坊"
async function generateArtStyle(content, style, base64_image) {
    return fetchFromBackend('/api/generate-style', { content, style, base64_image });
}

// 调用 "AI自画像"
async function generateSelfPortrait(base64_image, style_prompt) {
    return fetchFromBackend('/api/self-portrait', { base64_image, style_prompt });
}

// 调用 "艺术融合"
async function generateArtFusion(content_image, style_image) {
    return fetchFromBackend('/api/art-fusion', { content_image, style_image });
}

// 调用 "艺术问答"
async function askArtQuestion(question) {
    return fetchFromBackend('/api/ask-question', { question });
}

// 调用 "创意灵感"
async function generateArtIdeas(theme) {
    return fetchFromBackend('/api/generate-ideas', { theme });
}

// [移除] generatePaintingSteps