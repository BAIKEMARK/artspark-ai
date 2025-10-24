const { createApp } = Vue;

const AUTH_TOKEN_KEY = 'art_spark_auth_token';

const app = createApp({
    data() {
        return {
            // --- 全局状态 ---
            isLocalDev: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
            BACKEND_URL: '',
            isLoggedIn: false,
            isVerifyingApiKey: false,
            apiKeyInput: '',
            apiKeyError: '',
            apiKeyModal: {
                title: '欢迎来到 艺启智AI',
                description: '请输入您的ModelScope API KEY以激活助教功能。'
            },
            activeView: 'home-view',
            isSettingsSidebarOpen: false,

            // --- AI 全局设置 ---
            aiSettings: {
                chat_model: 'Qwen/Qwen3-30B-A3B-Instruct-2507',
                vl_model: 'Qwen/Qwen3-VL-8B-Instruct',
                image_model: 'black-forest-labs/FLUX.1-Krea-dev',
                age_range: '6-8岁',
            },

            // --- 首页 ---
            heroSlides: [
                { image: 'img/Starry-Night.jpg' },
                { image: 'img/千里江山图.jpg' },
                { image: 'img/Мона-Лиза.jpg' },
                { image: 'img/五牛图.jpeg' },
                { image: 'img/Monet-Impression-Sunrise.jpg' },
                { image: 'img/步辇图.jpeg' },
            ],
            currentHeroSlide: 0,
            slideInterval: null,
            navItems: [
                { id: 'home-view', text: '首页', icon: 'ph-house' },
                { id: 'art-gallery', text: '艺术画廊', icon: 'ph-palette' },
                { id: 'line-coloring', text: 'AI智能上色', icon: 'ph-paint-brush' },
                { id: 'style-workshop', text: '创意风格工坊', icon: 'ph-sparkle' },
                { id: 'self-portrait', text: 'AI自画像', icon: 'ph-user-square' },
                { id: 'art-fusion', text: '艺术融合', icon: 'ph-paint-roller' },
                { id: 'art-qa', text: '艺术知识问答', icon: 'ph-question' },
                { id: 'idea-generator', text: '创意灵感生成', icon: 'ph-lightbulb' },
            ],
            featureCards: [
                { id: 'line-coloring', icon: 'ph-paint-brush', title: 'AI智能上色', description: '上传线稿，一键变为专业彩绘' },
                { id: 'style-workshop', icon: 'ph-sparkle', title: '创意风格工坊', description: '用名画风格重绘你的草图' },
                { id: 'self-portrait', icon: 'ph-user-square', title: 'AI自画像', description: '上传照片，生成你的卡通肖像' },
                { id: 'art-fusion', icon: 'ph-paint-roller', title: '艺术融合', description: '将任意风格“刷”到你的照片上' },
            ],

            // --- 通用 ---
            previews: {
                coloring: null,
                styleWorkshop: null,
                selfPortrait: null,
                artFusionContent: null,
                artFusionStyle: null,
            },
            files: {
                coloring: null,
                styleWorkshop: null,
                selfPortrait: null,
                artFusionContent: null,
                artFusionStyle: null,
            },

            // --- 工具状态 ---
            coloring: { prompt: '', isLoading: false, error: '', resultUrl: null },
            styleWorkshop: { style: '梵高', content: '', isLoading: false, error: '', result: { imageUrl: null, styleDescription: '' } },
            selfPortrait: { style: '', isLoading: false, error: '', resultUrl: null },
            artFusion: { isLoading: false, error: '', resultUrl: null },
            artQA: { question: '', isLoading: false, error: '', answer: '' },
            ideaGenerator: { theme: '', isLoading: false, error: '', results: [] },
            gallery: {
                departments: [],
                filters: { departmentId: '', q: '', activeTags: {} },
                tagGroups: [
                    { title: '热门筛选', tags: [{ label: '博物馆精选', type: 'isHighlight', value: 'true' }] },
                    { title: '时代', tags: [
                        { label: '19世纪 (印象派等)', type: 'dateRange', begin: '1800', end: '1900' },
                        { label: '文艺复兴 (1400-1600)', type: 'dateRange', begin: '1400', end: '1600' },
                        { label: '古典时期 (希腊/罗马)', type: 'dateRange', begin: '-1000', end: '400' },
                    ]},
                    { title: '媒介', tags: [
                        { label: '绘画', type: 'medium', value: 'Paintings' },
                        { label: '雕塑', type: 'medium', value: 'Sculpture' },
                        { label: '陶瓷', type: 'medium', value: 'Ceramics' },
                    ]},
                    { title: '地区', tags: [
                        { label: '中国', type: 'geoLocation', value: 'China' },
                        { label: '日本', type: 'geoLocation', value: 'Japan' },
                        { label: '欧洲', type: 'geoLocation', value: 'Europe' },
                        { label: '埃及', type: 'geoLocation', value: 'Egypt' },
                    ]},
                ],
                isLoading: false,
                error: '',
                results: [],
            },

            // --- 侧边栏内容 ---
            sidebarContentData: {
                'default': { tips: `<h3><i class="icon ph-bold ph-lightbulb-filament"></i> 教学小贴士</h3><p>欢迎来到“艺启智AI”！从左侧导航栏选择一个工具，开始您的创意之旅。</p><p>您可以利用这些工具，帮助学生们理解色彩、风格和构图。</p>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 示例作品</h3><div class="example-images"><img src="img/Starry-Night.jpg" alt="示例1"><img src="img/千里江山图.jpg" alt="示例2"></div>` },
                'line-coloring': { tips: `<h3><i class="icon ph-bold ph-paint-brush"></i> 上色小贴士</h3><ul><li><strong>风格多样：</strong> 尝试“水彩画”、“油画”、“动漫风格”或“赛博朋克”等关键词。</li><li><strong>色彩词：</strong> 使用“明亮的颜色”、“柔和的色调”或“复古色”来引导AI。</li><li><strong>教学应用：</strong> 让学生上传同一张线稿，但使用不同的风格提示词，比较结果。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 上色示例</h3><div class="example-images"><img src="img/Starry-Night.jpg" alt="上色示例1"><img src="img/Starry-Night.jpg" alt="上色示例2"></div>` },
                'style-workshop': { tips: `<h3><i class="icon ph-bold ph-sparkle"></i> 风格小贴士</h3><ul><li><strong>上传草图：</strong> 上传一张简单的草图（比如一只猫），再选择“梵高”风格，效果惊人。</li><li><strong>内容描述：</strong> 即使不上传草图，也可以只通过描述来创作，例如“一只戴帽子的狗”。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="img/Starry-Night.jpg" alt="梵高"><img src="img/千里江山图.jpg" alt="水墨画"></div>` },
                'self-portrait': { tips: `<h3><i class="icon ph-bold ph-user-square"></i> 自画像小贴士</h3><ul><li><strong>风格探索：</strong> 尝试“迪士尼卡通风格”、“像素风”、“超级英雄漫画”或“黏土动画”。</li><li><strong>清晰照片：</strong> 使用面部清晰、光线明亮的照片，AI更容易识别特征。</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 风格示例</h3><div class="example-images"><img src="img/Starry-Night.jpg" alt="自画像1"><img src="img/Starry-Night.jpg" alt="自画像2"></div>` },
                'art-fusion': { tips: `<h3><i class="icon ph-bold ph-paint-roller"></i> 融合小贴士</h3><ul><li><strong>内容为王：</strong> “内容图片”决定了画面的主体结构（如人物、建筑）。</li><li><strong>风格至上：</strong> “风格图片”决定了颜色和笔触（如《星空》或一张火焰图片）。</li><li><strong>大胆尝试：</strong> 试试用一张电路板的图片作为“风格”来融合你的宠物照片！</li></ul>`, examples: `<h3><i class="icon ph-bold ph-image"></i> 融合示例</h3><div class="example-images"><img src="img/Starry-Night.jpg" alt="融合1"><img src="img/Starry-Night.jpg" alt="融合2"></div>` },
                'art-qa': { tips: `<h3><i class="icon ph-bold ph-question"></i> 提问小贴士</h3><ul><li><strong>保持好奇：</strong> 你可以问任何关于艺术的问题，比如“什么是印象派？”</li><li><strong>艺术家：</strong> “文森特·梵高是谁？”</li><li><strong>技巧：</strong> “怎么画透视？”</li></ul>`, examples: `` },
                'idea-generator': { tips: `<h3><i class="icon ph-bold ph-lightbulb"></i> 灵感小贴士</h3><ul><li><strong>激发创意：</strong> 当你不知道画什么时，这是最好的起点。</li><li><strong>主题词：</strong> 尝试输入“节日”、“动物”、“太空”或“梦想”等主题。</li><li><strong>再创作：</strong> AI生成的示例图只是参考，鼓励学生在此基础上进行自己的创作！</li></ul>`, examples: `` }
            },
        };
    },
    computed: {
        bodyClass() {
            return {
                'showing-home': this.activeView === 'home-view',
                'showing-tools': this.activeView !== 'home-view'
            };
        },
        sidebarContentHTML() {
            const contentKey = this.sidebarContentData[this.activeView] ? this.activeView : 'default';
            const content = this.sidebarContentData[contentKey];
            let html = '';
            if (content.tips) html += `<div class="sidebar-widget">${content.tips}</div>`;
            if (content.examples) html += `<div class="sidebar-widget">${content.examples}</div>`;
            return html;
        }
    },
    methods: {
        // --- 核心：认证与导航 ---
        async checkTokenValidity() {
            const token = localStorage.getItem(AUTH_TOKEN_KEY);
            if (!token) return false;
            try {
                const response = await fetch(`${this.BACKEND_URL}/api/check_key?token=${encodeURIComponent(token)}`);
                if (response.ok) return true;
                localStorage.removeItem(AUTH_TOKEN_KEY);
                return false;
            } catch (error) {
                console.error("Error during token validity check:", error);
                return false;
            }
        },
        async saveApiKey() {
            if (!this.apiKeyInput.trim()) {
                this.apiKeyError = 'API KEY 不能为空';
                return;
            }
            this.isVerifyingApiKey = true;
            this.apiKeyError = '';
            try {
                const response = await fetch(`${this.BACKEND_URL}/api/set_key`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: this.apiKeyInput.trim() }),
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.error || '设置Key失败');
                if (result.token) {
                    localStorage.setItem(AUTH_TOKEN_KEY, result.token);
                    this.isLoggedIn = true;
                    this.apiKeyError = '';
                    this.navigateTo('home-view');
                } else {
                    throw new Error('未能从服务器获取 Token');
                }
            } catch (error) {
                this.apiKeyError = `错误: ${error.message}`;
            } finally {
                this.isVerifyingApiKey = false;
            }
        },
        showApiKeyModal(reason = 'initial') {
            if (reason === 'expired' || reason === 'invalid') {
                this.apiKeyModal.title = 'API Key 已失效';
                this.apiKeyModal.description = '您的API Key已过期或无效。请重新输入以继续使用。';
            } else {
                this.apiKeyModal.title = '欢迎来到 艺启智AI';
                this.apiKeyModal.description = '请输入您的ModelScope API KEY以激活助教功能。';
            }
            this.isLoggedIn = false;
            localStorage.removeItem(AUTH_TOKEN_KEY);
        },
        navigateTo(targetId) {
            this.activeView = targetId;
            window.scrollTo(0, 0);
        },

        // --- 首页幻灯片 ---
        startSlideShow() {
            this.showHeroSlide(0);
            clearInterval(this.slideInterval);
            this.slideInterval = setInterval(this.nextHeroSlide, 5000);
        },
        showHeroSlide(index) {
            this.currentHeroSlide = index;
        },
        nextHeroSlide() {
            this.currentHeroSlide = (this.currentHeroSlide + 1) % this.heroSlides.length;
        },

        // --- 表单与文件处理 ---
        handleFileChange(event, key) {
            const file = event.target.files[0];
            if (!file) {
                this.files[key] = null;
                this.previews[key] = null;
                return;
            }
            this.files[key] = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                this.previews[key] = e.target.result;
            };
            reader.readAsDataURL(file);
        },
        fileToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => resolve(reader.result);
                reader.onerror = error => reject(error);
            });
        },

        // --- 结果渲染辅助函数 ---
        getDownloadButtonHTML(imageUrl, filename) {
            const downloadUrl = `${this.BACKEND_URL}/api/proxy-download?url=${encodeURIComponent(imageUrl)}`;
            return `<a href="${downloadUrl}" class="download-btn" download="${filename || 'art-ai-image.png'}" target="_blank" rel="noopener noreferrer"><i class="icon ph-bold ph-download-simple"></i> 下载图片</a>`;
        },
        getSingleImageResultHTML(imageUrl, altText, filename) {
            const img = `<img src="${imageUrl}" alt="${altText}">`;
            const btn = this.getDownloadButtonHTML(imageUrl, filename);
            return img + btn;
        },

        // --- 工具方法 ---
        async generateColoring() {
            if (!this.files.coloring) { this.coloring.error = '请上传一张线稿图片'; return; }
            if (!this.coloring.prompt) { this.coloring.error = '请输入上色风格'; return; }
            this.coloring.isLoading = true; this.coloring.error = ''; this.coloring.resultUrl = null;
            try {
                const base64_image = await this.fileToBase64(this.files.coloring);
                const result = await this.fetchFromBackend('/api/colorize-lineart', { base64_image, prompt: this.coloring.prompt });
                this.coloring.resultUrl = result.imageUrl;
            } catch (error) {
                this.coloring.error = `生成失败: ${error.message}`;
            } finally {
                this.coloring.isLoading = false;
            }
        },
        async generateStyle() {
            if (!this.styleWorkshop.content && !this.files.styleWorkshop) { this.styleWorkshop.error = '请输入绘制内容或上传一张草图'; return; }
            this.styleWorkshop.isLoading = true; this.styleWorkshop.error = ''; this.styleWorkshop.result = { imageUrl: null, styleDescription: '' };
            try {
                let base64_image = null;
                if (this.files.styleWorkshop) {
                    base64_image = await this.fileToBase64(this.files.styleWorkshop);
                }
                const result = await this.fetchFromBackend('/api/generate-style', { content: this.styleWorkshop.content, style: this.styleWorkshop.style, base64_image });
                this.styleWorkshop.result = result;
            } catch (error) {
                this.styleWorkshop.error = `生成失败: ${error.message}`;
            } finally {
                this.styleWorkshop.isLoading = false;
            }
        },
        async generatePortrait() {
            if (!this.files.selfPortrait) { this.selfPortrait.error = '请上传一张你的照片'; return; }
            if (!this.selfPortrait.style) { this.selfPortrait.error = '请输入你想要的风格'; return; }
            this.selfPortrait.isLoading = true; this.selfPortrait.error = ''; this.selfPortrait.resultUrl = null;
            try {
                const base64_image = await this.fileToBase64(this.files.selfPortrait);
                const result = await this.fetchFromBackend('/api/self-portrait', { base64_image, style_prompt: this.selfPortrait.style });
                this.selfPortrait.resultUrl = result.imageUrl;
            } catch (error) {
                this.selfPortrait.error = `生成失败: ${error.message}`;
            } finally {
                this.selfPortrait.isLoading = false;
            }
        },
        async generateFusion() {
            if (!this.files.artFusionContent) { this.artFusion.error = '请上传内容图片'; return; }
            if (!this.files.artFusionStyle) { this.artFusion.error = '请上传风格图片'; return; }
            this.artFusion.isLoading = true; this.artFusion.error = ''; this.artFusion.resultUrl = null;
            try {
                const content_image = await this.fileToBase64(this.files.artFusionContent);
                const style_image = await this.fileToBase64(this.files.artFusionStyle);
                const result = await this.fetchFromBackend('/api/art-fusion', { content_image, style_image });
                this.artFusion.resultUrl = result.imageUrl;
            } catch (error) {
                this.artFusion.error = `生成失败: ${error.message}`;
            } finally {
                this.artFusion.isLoading = false;
            }
        },
        async askQuestion() {
            if (!this.artQA.question) { this.artQA.error = '请输入你的问题'; return; }
            this.artQA.isLoading = true; this.artQA.error = ''; this.artQA.answer = '';
            try {
                const result = await this.fetchFromBackend('/api/ask-question', { question: this.artQA.question });
                if (result.choices && result.choices[0] && result.choices[0].message) {
                    this.artQA.answer = result.choices[0].message.content;
                } else if (result.message) {
                    throw new Error(result.message);
                } else {
                    throw new Error("未能获取回答。");
                }
            } catch (error) {
                this.artQA.error = `回答失败: ${error.message}`;
            } finally {
                this.artQA.isLoading = false;
            }
        },
        async generateIdeas() {
            if (!this.ideaGenerator.theme) { this.ideaGenerator.error = '请输入灵感主题'; return; }
            this.ideaGenerator.isLoading = true; this.ideaGenerator.error = ''; this.ideaGenerator.results = [];
            try {
                const ideas = await this.fetchFromBackend('/api/generate-ideas', { theme: this.ideaGenerator.theme });
                this.ideaGenerator.results = ideas;
            } catch (error) {
                this.ideaGenerator.error = `生成失败: ${error.message}`;
            } finally {
                this.ideaGenerator.isLoading = false;
            }
        },

        // --- 画廊方法 ---
        async loadGalleryDepartments() {
            try {
                const response = await fetch(`${this.BACKEND_URL}/api/gallery/departments`);
                if (!response.ok) throw new Error('Failed to load departments');
                const data = await response.json();
                this.gallery.departments = data.departments;
            } catch (error) {
                console.error("Error loading gallery departments:", error);
            }
        },
        toggleGalleryTag(tag) {
            const currentActiveTag = this.gallery.filters.activeTags[tag.type];
            if (currentActiveTag && currentActiveTag.label === tag.label) {
                // If clicking the same tag, deactivate it
                delete this.gallery.filters.activeTags[tag.type];
            } else {
                // Otherwise, activate the new tag
                this.gallery.filters.activeTags[tag.type] = tag;
            }
        },
        isTagActive(tag) {
            const activeTag = this.gallery.filters.activeTags[tag.type];
            return activeTag && activeTag.label === tag.label;
        },
        async searchGallery() {
            this.gallery.isLoading = true; this.gallery.error = ''; this.gallery.results = [];
            try {
                const filters = {
                    q: this.gallery.filters.q || '*',
                    departmentId: this.gallery.filters.departmentId
                };
                Object.values(this.gallery.filters.activeTags).forEach(tag => {
                    if (tag.type === 'dateRange') {
                        filters.dateBegin = tag.begin;
                        filters.dateEnd = tag.end;
                    } else {
                        filters[tag.type] = tag.value;
                    }
                });

                const requestUrl = `${this.BACKEND_URL}/api/gallery/search`;
                const response = await fetch(requestUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(filters),
                });
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.error || `请求失败: ${response.status}`);
                }
                const result = await response.json();
                this.gallery.results = result.artworks;
                if (result.artworks.length === 0) {
                    this.gallery.error = '没有找到符合条件的作品。';
                }
            } catch (error) {
                this.gallery.error = `搜索失败: ${error.message}`;
            } finally {
                this.gallery.isLoading = false;
            }
        },

        // --- 后端通信 ---
        async fetchFromBackend(endpoint, body) {
            const token = localStorage.getItem(AUTH_TOKEN_KEY);
            if (!token) {
                this.showApiKeyModal('expired');
                throw new Error("您尚未登录。");
            }

            let requestUrl = `${this.BACKEND_URL}${endpoint}?token=${encodeURIComponent(token)}`;

            const fullBody = {
                ...body,
                config_chat_model: this.aiSettings.chat_model,
                config_vl_model: this.aiSettings.vl_model,
                config_image_model: this.aiSettings.image_model,
                config_age_range: this.aiSettings.age_range,
            };

            const response = await fetch(requestUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fullBody),
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.showApiKeyModal('expired');
                    const err = await response.json();
                    throw new Error(err.error || "API 密钥已失效，请重新输入");
                }
                const err = await response.json();
                throw new Error(err.error || `请求失败: ${response.status}`);
            }
            return response.json();
        }
    },
    created() {
        this.BACKEND_URL = this.isLocalDev ? 'http://localhost:7860' : '';
        console.log(`[App] 运行在 ${this.isLocalDev ? '本地开发' : '生产'} 模式. API URL: '${this.BACKEND_URL || "(相对路径)"}'`);
    },
    async mounted() {
        const hasValidToken = await this.checkTokenValidity();
        if (hasValidToken) {
            this.isLoggedIn = true;
            this.navigateTo('home-view');
        } else {
            this.showApiKeyModal('initial');
        }
        this.startSlideShow();
        this.loadGalleryDepartments();
    }
});

app.mount('#app');

