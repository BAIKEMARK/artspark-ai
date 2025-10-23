// ==========================================================
// 全局变量和 DOM 元素
// ==========================================================

// 动态设置后端 URL 以适应本地和生产环境
const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const BACKEND_URL = isLocalDev ? 'http://localhost:7860' : '';
console.log(`[App] 运行在 ${isLocalDev ? '本地开发' : '生产'} 模式. API URL: '${BACKEND_URL || "(相对路径)"}'`);

const AUTH_TOKEN_KEY = 'art_spark_auth_token'; // 用于 localStorage

const MODEL_SCOPE_TOKEN_KEY = 'modelscope_api_key';
const apiKeyModal = document.getElementById('api-key-modal');
const apiKeySection = document.getElementById('api-key-section');
const apiKeyInput = document.getElementById('api-key-input');
const saveKeyBtn = document.getElementById('save-key-btn');
const apiError = document.getElementById('api-error');
const mainContentWrapper = document.getElementById('main-content-wrapper');
const homeView = document.getElementById('home-view');
const toolContent = document.getElementById('tool-content');
// 首页功能区
const homeFeaturesSection = document.getElementById('home-features-section'); // [V9] 此元素现在是空的
const globalNav = document.getElementById('global-nav');
const navLinks = globalNav.querySelector('.nav-links');
const allNavButtons = globalNav.querySelectorAll('.nav-btn');
const homeLogoButton = document.getElementById('home-logo-btn');
const homeContentOverlay = homeView.querySelector('.home-content-overlay');
// [V9] 卡片现在位于 homeContentOverlay 内部
const featureCards = homeContentOverlay.querySelectorAll('.feature-card');
const heroSlider = document.querySelector('.slider-container');
const sliderDotsContainer = document.querySelector('.slider-dots');
let heroSlides = [];
let currentHeroSlide = 0;
let slideInterval;
const featurePanels = document.querySelectorAll('.feature-panel');
const toolPanelsWrapper = document.getElementById('tool-panels-wrapper');
const contextualSidebar = document.getElementById('contextual-sidebar');
const footerGuide = document.getElementById('footer-guide'); // Get footer


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

// ==========================================================
// [新增] 侧边栏内容数据库
// ==========================================================
const sidebarContentData = {
    'default': {
        tips: `
            <h3><i class="icon ph-bold ph-lightbulb-filament"></i> 教学小贴士</h3>
            <p>欢迎来到“艺启智AI”！从左侧导航栏选择一个工具，开始您的创意之旅。</p>
            <p>您可以利用这些工具，帮助学生们理解色彩、风格和构图。</p>
        `,
        examples: `
            <h3><i class="icon ph-bold ph-image"></i> 示例作品</h3>
            <div class="example-images">
                <img src="img/Starry Night.jpg" alt="示例1">
                <img src="img/千里江山图.jpg" alt="示例2">
            </div>
        `
    },
    'line-coloring': {
        tips: `
            <h3><i class="icon ph-bold ph-paint-brush"></i> 上色小贴士</h3>
            <ul>
                <li><strong>风格多样：</strong> 尝试“水彩画”、“油画”、“动漫风格”或“赛博朋克”等关键词。</li>
                <li><strong>色彩词：</strong> 使用“明亮的颜色”、“柔和的色调”或“复古色”来引导AI。</li>
                <li><strong>教学应用：</strong> 让学生上传同一张线稿，但使用不同的风格提示词，比较结果。</li>
            </ul>
        `,
        examples: `
            <h3><i class="icon ph-bold ph-image"></i> 上色示例</h3>
            <div class="example-images">
                <img src="img/Starry Night.jpg" alt="上色示例1">
                <img src="img/Starry Night.jpg" alt="上色示例2">
            </div>
        `
    },
    'style-workshop': {
        tips: `
            <h3><i class="icon ph-bold ph-sparkle"></i> 风格小贴士</h3>
            <ul>
                <li><strong>上传草图：</strong> 上传一张简单的草图（比如一只猫），再选择“梵高”风格，效果惊人。</li>
                <li><strong>内容描述：</strong> 即使不上传草图，也可以只通过描述来创作，例如“一只戴帽子的狗”。</li>
            </ul>
        `,
        examples: `
            <h3><i class="icon ph-bold ph-image"></i> 风格示例</h3>
            <div class="example-images">
                <img src="img/Starry Night.jpg" alt="梵高">
                <img src="img/千里江山图.jpg" alt="水墨画">
            </div>
        `
    },
    'self-portrait': {
        tips: `
            <h3><i class="icon ph-bold ph-user-square"></i> 自画像小贴士</h3>
            <ul>
                <li><strong>风格探索：</strong> 尝试“迪士尼卡通风格”、“像素风”、“超级英雄漫画”或“黏土动画”。</li>
                <li><strong>清晰照片：</strong> 使用面部清晰、光线明亮的照片，AI更容易识别特征。</li>
            </ul>
        `,
        examples: `
            <h3><i class="icon ph-bold ph-image"></i> 风格示例</h3>
            <div class="example-images">
                <img src="img/Starry Night.jpg" alt="自画像1">
                <img src="img/Starry Night.jpg" alt="自画像2">
            </div>
        `
    },
    'art-fusion': {
        tips: `
            <h3><i class="icon ph-bold ph-paint-roller"></i> 融合小贴士</h3>
            <ul>
                <li><strong>内容为王：</strong> “内容图片”决定了画面的主体结构（如人物、建筑）。</li>
                <li><strong>风格至上：</strong> “风格图片”决定了颜色和笔触（如《星空》或一张火焰图片）。</li>
                <li><strong>大胆尝试：</strong> 试试用一张电路板的图片作为“风格”来融合你的宠物照片！</li>
            </ul>
        `,
        examples: `
            <h3><i class="icon ph-bold ph-image"></i> 融合示例</h3>
            <div class="example-images">
                <img src="img/Starry Night.jpg" alt="融合1">
                <img src="img/Starry Night.jpg" alt="融合2">
            </div>
        `
    },
    'art-qa': {
        tips: `
            <h3><i class="icon ph-bold ph-question"></i> 提问小贴士</h3>
            <ul>
                <li><strong>保持好奇：</strong> 你可以问任何关于艺术的问题，比如“什么是印象派？”</li>
                <li><strong>艺术家：</strong> “文森特·梵高是谁？”</li>
                <li><strong>技巧：</strong> “怎么画透视？”</li>
            </ul>
        `,
        examples: ``
    },
    'idea-generator': {
        tips: `
            <h3><i class="icon ph-bold ph-lightbulb"></i> 灵感小贴士</h3>
            <ul>
                <li><strong>激发创意：</strong> 当你不知道画什么时，这是最好的起点。</li>
                <li><strong>主题词：</strong> 尝试输入“节日”、“动物”、“太空”或“梦想”等主题。</li>
                <li><strong>再创作：</strong> AI生成的示例图只是参考，鼓励学生在此基础上进行自己的创作！</li>
            </ul>
        `,
        examples: ``
    }
};

// ==========================================================
// 初始化
// ==========================================================
document.addEventListener('DOMContentLoaded', () => {
    initApiKeyManager();
    initHeroSlider();
    initNavigation();
    initColoring();
    initStyleWorkshop();
    initSelfPortrait();
    initArtFusion();
    initArtQA();
    initIdeaGenerator();
    setupImagePreview(coloringFileInput, coloringPreview);
    setupImagePreview(styleFileInput, stylePreview);
    setupImagePreview(portraitFileInput, portraitPreview);
    setupImagePreview(fusionContentInput, fusionContentPreview);
    setupImagePreview(fusionStyleInput, fusionStylePreview);
});

// ==========================================================
// 核心模块 1: API 密钥管理
// ==========================================================

// 检查 Token 是否存在且有效
async function checkTokenValidity() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
        return false;
    }

    try {
        // [V10 修改] 将 token 作为 query 参数附加到 URL
        const requestUrl = `${BACKEND_URL}/api/check_key?token=${encodeURIComponent(token)}`;

        const response = await fetch(requestUrl, {
            method: 'GET'
        });
        if (response.ok) {
            return true;
        } else {
            localStorage.removeItem(AUTH_TOKEN_KEY);
            return false;
        }
    } catch (error) {
        console.error("Error during token validity check:", error);
        return false;
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
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '设置Key失败');
            }

            if (result.token) {
                localStorage.setItem(AUTH_TOKEN_KEY, result.token);
                showMainContent();
                apiError.textContent = '';
            } else {
                throw new Error('未能从服务器获取 Token');
            }

        } catch (error) {
            apiError.textContent = `错误: ${error.message}`;
        }
    });

    (async () => {
        const hasValidToken = await checkTokenValidity();

        if (hasValidToken) {
            console.log("Token valid, showing main content.");
            showMainContent();
        } else {
            console.log("No valid token found, showing API key modal.");
            showApiKeyModal();
        }
    })();
}
function showMainContent() {
    apiKeyModal.classList.add('hidden');
    footerGuide.classList.remove('hidden');
    document.body.classList.add('showing-home');
    document.body.classList.remove('showing-tools');
    requestAnimationFrame(() => {
        navigateTo('home-view');
    });
}
function showApiKeyModal() {
    apiKeyModal.classList.remove('hidden');
    footerGuide.classList.add('hidden');
    localStorage.removeItem(AUTH_TOKEN_KEY);
    homeView.style.display = 'none';
    homeFeaturesSection.style.display = 'none';
    toolContent.style.display = 'none';
    contextualSidebar.classList.add('hidden');
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
// 核心模块 2: 主导航逻辑 (V9 恢复)
// ==========================================================
function initNavigation() {
    navLinks.addEventListener('click', (e) => {
        const button = e.target.closest('button.nav-btn');
        if (button) {
            const targetId = button.dataset.target;
            navigateTo(targetId);
        }
    });
    homeLogoButton.addEventListener('click', (e) => { e.preventDefault(); navigateTo('home-view'); });
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
    toolContent.style.display = isHomePage ? 'none' : 'flex';

    if (isHomePage) {
        contextualSidebar.classList.add('hidden');
        featurePanels.forEach(panel => {
           panel.classList.add('hidden');
           panel.classList.remove('active');
       });
    } else {
        contextualSidebar.classList.remove('hidden');
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
             contextualSidebar.classList.add('hidden');
        } else {
            // Update sidebar content only if a valid tool panel is shown
            updateSidebarContent(targetId);
        }
    }
    window.scrollTo(0, 0);
}

// 动态更新侧边栏的函数
function updateSidebarContent(targetId) {
    const contentKey = sidebarContentData[targetId] ? targetId : 'default';
    const content = sidebarContentData[contentKey];

    let html = '';

    if (content.tips) {
        html += `<div class="sidebar-widget">${content.tips}</div>`;
    }
    if (content.examples) {
        html += `<div class="sidebar-widget">${content.examples}</div>`;
    }

    contextualSidebar.innerHTML = html;
}

// ==========================================================
// 核心模块 3-8: 工具功能 (不变)
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
            // [修改] 传入下载文件名
            displaySingleImageResult(coloringResult, result.imageUrl, "AI上色作品", "ai-coloring.png");
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

        if (!content && !file) {
            styleError.textContent = '请输入绘制内容或上传一张草图';
            return;
        }

        toggleUIState(generateStyleBtn, styleLoader, styleError, true);
        styleResult.classList.add('hidden');

        try {
            let base64_image = null;
            if (file) {
                base64_image = await fileToBase64(file);
            }
            const result = await generateArtStyle(content, style, base64_image);
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
    styleResult.innerHTML = '';
    const img = document.createElement('img');
    img.src = result.imageUrl;
    img.alt = `风格画作`;
    const desc = document.createElement('p');
    desc.className = 'style-desc';
    desc.textContent = result.styleDescription;
    const downloadBtn = createDownloadButton(result.imageUrl, "style-workshop.png");
    styleResult.appendChild(img);
    styleResult.appendChild(desc);
    styleResult.appendChild(downloadBtn);
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
            displaySingleImageResult(portraitResult, result.imageUrl, "AI自画像", "ai-portrait.png");
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
            displaySingleImageResult(fusionResult, result.imageUrl, "艺术融合作品", "art-fusion.png");
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
function displayArtIdeas(ideas) {
    ideasResult.innerHTML = '';
    if (!ideas || ideas.length === 0) {
        ideasError.textContent = '未能解析创意。';
        return;
    }
    ideas.forEach(idea => {
        const card = document.createElement('div');
        card.className = 'idea-card';
        const img = document.createElement('img');
        img.src = idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image';
        img.alt = idea.name;
        const title = document.createElement('h3');
        title.textContent = idea.name;
        const desc = document.createElement('p');
        desc.textContent = idea.description;
        const elements = document.createElement('small');
        elements.textContent = `关键元素: ${idea.elements}`;

        let downloadBtn = null;
        if(idea.exampleImage) {
            downloadBtn = createDownloadButton(idea.exampleImage, `${idea.name.replace(/\s/g, '_')}.png`);
        }

        card.appendChild(img);
        card.appendChild(title);
        card.appendChild(desc);
        card.appendChild(elements);
        if (downloadBtn) {
            card.appendChild(downloadBtn);
        }
        ideasResult.appendChild(card);
    });
    ideasResult.classList.remove('hidden');
}

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
 * 辅助函数：创建下载按钮 (使用后端代理)
 */
function createDownloadButton(imageUrl, filename) {
    const button = document.createElement('a');
    button.href = `${BACKEND_URL}/api/proxy-download?url=${encodeURIComponent(imageUrl)}`;
    button.className = 'download-btn';
    button.innerHTML = `<i class="icon ph-bold ph-download-simple"></i> 下载图片`;

    button.download = filename || 'art-ai-image.png';
    button.target = '_blank';
    button.rel = 'noopener noreferrer';
    return button;
}


/**
 * [修改] 辅助函数：用于显示单张图片的通用函数 (增加下载按钮)
 */
function displaySingleImageResult(resultContainer, imageUrl, altText, filename) {
    resultContainer.innerHTML = ''; // 清空旧结果

    // 1. 创建图片
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = altText;

    // 2. 创建下载按钮
    const downloadBtn = createDownloadButton(imageUrl, filename);

    // 3. 添加到容器
    resultContainer.appendChild(img);
    resultContainer.appendChild(downloadBtn);
    resultContainer.classList.remove('hidden');
}


// ==========================================================
// AI 调用函数 (不变)
// ==========================================================

// 辅助函数：处理所有到后端的 fetch 请求
async function fetchFromBackend(endpoint, body) {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token && endpoint !== '/api/set_key') {
        showApiKeyModal();
        throw new Error("您尚未登录。");
    }

    const headers = {
        'Content-Type': 'application/json'
    };
    // [V10 新增] 将 token 作为 query 参数附加到 URL
    let requestUrl = `${BACKEND_URL}${endpoint}`;
    if (token) {
        // 确保只添加 '?' 或 '&'，以防 endpoint 自身已包含参数
        requestUrl += (requestUrl.includes('?') ? '&' : '?') + `token=${encodeURIComponent(token)}`;
    }

    const response = await fetch(requestUrl, { // [V10 修改] 使用新的 requestUrl
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        // [修改] 捕获 401 错误并弹出模态框
        if (response.status === 401) {
            console.error("Authentication error (401). Token is invalid or expired.");
            showApiKeyModal();
            const err = await response.json();
            throw new Error(err.error || "API 密钥已失效，请重新输入");
        }
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