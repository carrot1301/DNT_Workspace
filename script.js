/**
 * 1. REVEAL EFFECT (FADE-IN & SLIDE-UP)
 */
const initReveal = () => {
    const reveals = document.querySelectorAll('.reveal');
    const observerOptions = {
        root: null,
        threshold: 0.15
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    reveals.forEach(reveal => revealObserver.observe(reveal));
};

/**
 * 2. TYPING EFFECT (HERO SECTION) - BILINGUAL
 */
const typingTexts = {
    en: ["Financial Data.", "Quant Analysis.", "Algorithmic Tools.", "Risk Modeling."],
    vi: ["Dữ liệu Tài chính.", "Phân tích Định lượng.", "Công cụ Thuật toán.", "Mô hình Rủi ro."]
};

let currentLang = localStorage.getItem('dnt_lang') || 'en';
let textArray = typingTexts[currentLang];

const typingDelay = 100;
const erasingDelay = 50;
const newTextDelay = 2000;
let textArrayIndex = 0;
let charIndex = 0;

const typedTextSpan = document.querySelector(".typed-text");
const cursorSpan = document.querySelector(".cursor");

const type = () => {
    if (!typedTextSpan) return;

    if (charIndex < textArray[textArrayIndex].length) {
        if (cursorSpan && !cursorSpan.classList.contains("typing")) {
            cursorSpan.classList.add("typing");
        }
        typedTextSpan.textContent += textArray[textArrayIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else {
        if (cursorSpan) cursorSpan.classList.remove("typing");
        setTimeout(erase, newTextDelay);
    }
};

const erase = () => {
    if (charIndex > 0) {
        if (cursorSpan && !cursorSpan.classList.contains("typing")) {
            cursorSpan.classList.add("typing");
        }
        typedTextSpan.textContent = textArray[textArrayIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else {
        if (cursorSpan) cursorSpan.classList.remove("typing");
        textArrayIndex = (textArrayIndex + 1) % textArray.length;
        setTimeout(type, typingDelay + 500);
    }
};

/**
 * 3. SCROLL LOGIC (PROGRESS BAR, SCROLLSPY, VIDEO CONTROL)
 */
const video = document.getElementById("scrollVideo");
const scrollProgress = document.querySelector('.scroll-progress');
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

const handleScrollEffects = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    
    const scrollFraction = docHeight > 0 ? scrollTop / docHeight : 0;

    if (scrollProgress) {
        scrollProgress.style.width = `${scrollFraction * 100}%`;
    }

    let currentSectionId = "";
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollTop >= (sectionTop - sectionHeight / 3)) {
            currentSectionId = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').includes(currentSectionId)) {
            link.classList.add('active');
        }
    });

    if (video && !isNaN(video.duration)) {
        requestAnimationFrame(() => {
            video.currentTime = video.duration * scrollFraction;
        });
    }
};

/**
 * 4. KHỞI TẠO CHUNG (INITIALIZATION)
 */
document.addEventListener('DOMContentLoaded', () => {
    initReveal();

    if (typedTextSpan) {
        setTimeout(type, 1000);
    }

    if (video) {
        const setupVideo = () => {
            video.play().then(() => {
                setTimeout(() => {
                    video.pause();
                    handleScrollEffects();
                }, 150);
            }).catch(e => console.log("Video playback error:", e));
        };

        if (video.readyState >= 1) {
            setupVideo();
        } else {
            video.addEventListener('loadedmetadata', setupVideo);
        }
    }

    window.addEventListener('scroll', handleScrollEffects, { passive: true });
});

/**
 * 5. SIRI-STYLE AI CHATBOT LOGIC
 */
const chatToggleBtn = document.getElementById('chat-toggle-btn');
const chatWindow = document.getElementById('chat-window');
const closeChatBtn = document.getElementById('close-chat-btn');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendChatBtn = document.getElementById('send-chat-btn');
const siriSphere = document.querySelector('.siri-sphere');

let chatHistory = []; 
let siriAnimation;

if (siriSphere) {
    for (let i = 0; i < 4; i++) {
        const ring = document.createElement('div');
        ring.className = 'siri-ring';
        ring.style.position = 'absolute';
        ring.style.width = '100%';
        ring.style.height = '100%';
        ring.style.borderRadius = '50%';
        ring.style.border = '1px solid var(--accent)';
        ring.style.opacity = '0';
        ring.style.filter = 'blur(1px)';
        siriSphere.appendChild(ring);
    }
}

function startSiriAnimation() {
    if (typeof anime === 'undefined') return;
    siriAnimation = anime.timeline({
        targets: '.siri-sphere',
        easing: 'easeInOutSine',
        duration: 300,
        loop: true,
        autoplay: true,
    })
    .add({
        targets: '.siri-sphere',
        scale: [1, 1.05],
        opacity: [0.8, 1],
        easing: 'linear',
        duration: 200,
    })
    .add({
        targets: '.siri-ring',
        scale: [1, 2.5],
        opacity: [0.6, 0],
        easing: 'linear',
        duration: anime.random(1200, 1800),
        delay: anime.stagger(200),
    });
}

function stopSiriAnimation() {
    if (siriAnimation) {
        siriAnimation.pause();
        anime({
            targets: '.siri-sphere',
            scale: 1,
            opacity: 0.8,
            duration: 300
        });
        anime({
            targets: '.siri-ring',
            scale: 1,
            opacity: 0,
            duration: 300
        });
    }
}

chatToggleBtn.addEventListener('click', () => {
    chatWindow.classList.toggle('hidden');
    siriSphere.classList.toggle('hidden');
    chatToggleBtn.classList.toggle('active');

    if (chatToggleBtn.classList.contains('active')) {
        startSiriAnimation();
    } else {
        stopSiriAnimation();
    }
});

closeChatBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
    siriSphere.classList.add('hidden');
    chatToggleBtn.classList.remove('active');
    stopSiriAnimation();
});

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    chatInput.value = '';

    const typingId = "typing-" + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot');
    typingDiv.id = typingId;
    typingDiv.textContent = currentLang === 'en' ? "Just a sec, I'm thinking..." : "Đợi xíu, mình đang suy nghĩ...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('https://dnt-portfolio-backend.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                history: chatHistory 
            })
        });

        const data = await response.json();
        document.getElementById(typingId).remove();

        if (!response.ok) {
            addMessage(data.detail || (currentLang === 'en' ? "An error occurred, please try again!" : "Có lỗi xảy ra, thử lại nhé!"), 'bot');
            return;
        }

        addMessage(data.reply, 'bot');

        chatHistory.push({ role: "user", text: message });
        chatHistory.push({ role: "assistant", text: data.reply });
        
        if (chatHistory.length > 6) {
            chatHistory = chatHistory.slice(-6);
        }

    } catch (error) {
        document.getElementById(typingId).remove();
        addMessage(currentLang === 'en' ? "Oops, server is under maintenance!" : "Opss, có lỗi xảy ra! Vui lòng thử lại sau.", 'bot');
    }
}

sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

/**
 * 6. AI AGENT CTA LOGIC (ABOUT ME)
 */
const aboutAiCtaBtn = document.getElementById('about-ai-cta-btn');

if (aboutAiCtaBtn) {
    aboutAiCtaBtn.addEventListener('click', () => {
        if (chatWindow && chatWindow.classList.contains('hidden')) {
            chatWindow.classList.remove('hidden');
            siriSphere.classList.remove('hidden');
            chatToggleBtn.classList.add('active');
            startSiriAnimation();
        }
        
        if (chatInput) {
            chatInput.focus();
        }
    });
}

/**
 * 7. HỆ THỐNG ĐA NGÔN NGỮ (i18n)
 */
const translations = {
    en: {
        nav_home: "Home",
        nav_about: "About",
        nav_live: "Live App",
        nav_research: "Research",
        nav_contact: "Contact",
        nav_cv: "Download CV",
        hero_greeting: "Hi, I'm <span class='accent'>Doan Nguyen Tri</span> 👋",
        hero_desc: "I specialize in the complete data lifecycle—from scraping and wrangling messy datasets to conducting rigorous exploratory data analysis (EDA). I build data-driven financial models and algorithmic tools that bridge the gap between complex quantitative research and actionable investment strategies.",
        hero_btn_live: "Try live dashboard",
        hero_btn_cv: "Download CV",
        scroll_down: "Scroll Down",
        about_title: "About Me",
        about_desc: "I am a final-year Data Science student at the <strong>University of Economics and Finance (UEF)</strong>, where I've developed a deep-rooted passion for <strong>Financial Data Analysis</strong>. My journey is driven by an insatiable curiosity for how data intersects with global markets.<br><br>Beyond the numbers, I love exploring the 'creative' side of tech. I’ve taught myself <strong>Web Programming and Design</strong> to ensure my analytical models aren't just accurate, but also beautifully presented and user-friendly. I'm a firm believer in being a lifelong learner, always eager to pick up new tools—from complex algorithmic trading strategies to the latest web animations—bridging the gap between rigorous finance and modern technology.",
        ai_cta_text: "Curious about my other secret skills or want to chat with my virtual self?",
        ai_cta_btn: "<i class='ph ph-robot'></i> More about me with my AI Agent",
        featured_title: "Featured: VN30 Stock Analyzer",
        featured_sub: "An interactive quantitative research tool comparing VN30 equities against the market benchmark.",
        iframe_title: "Live Trading Environment",
        projects_title: "Other Analytical Projects",
        proj_1_desc: "A portfolio optimization tool using the Capital Asset Pricing Model (CAPM) and Monte Carlo simulation to identify the efficient frontier.",
        proj_2_desc: "An empirical analysis project examining the macro-economic relationship and exchange rate dynamics between the USD and VND.",
        proj_3_desc: "Developed a detailed credit scoring model involving synthetic data generation, rigorous feature engineering, and policy simulation.",
        view_code: "<i class='ph ph-github-logo'></i> View Code",
        github_cta_text: "Hungry for more? Explore all my repositories and experimental scripts.",
        github_cta_btn: "<i class='ph ph-github-logo'></i> View more on GitHub",
        contact_title: "Get In Touch",
        contact_sub: "Currently seeking Quantitative Analyst / Data Analyst internship opportunities.",
        footer_rights: "© 2026 <strong>DOAN NGUYEN TRI</strong>. All Rights Reserved.",
        footer_sub: "Designed & Developed by Tri Doan | Built for Quantitative Finance"
    },
    vi: {
        nav_home: "Trang chủ",
        nav_about: "Về tôi",
        nav_live: "Ứng dụng Live",
        nav_research: "Nghiên cứu",
        nav_contact: "Liên hệ",
        nav_cv: "Tải CV",
        hero_greeting: "Xin chào, mình là <span class='accent'>Đoàn Nguyên Trí</span> 👋",
        hero_desc: "Mình chuyên xử lý toàn bộ vòng đời của dữ liệu—từ thu thập, làm sạch các tập dữ liệu thô cho đến phân tích dữ liệu khám phá (EDA) chuyên sâu. Mình xây dựng các mô hình tài chính và công cụ thuật toán dựa trên dữ liệu, nhằm thu hẹp khoảng cách giữa nghiên cứu định lượng phức tạp và các chiến lược đầu tư thực tiễn.",
        hero_btn_live: "Trải nghiệm Dashboard",
        hero_btn_cv: "Tải CV",
        scroll_down: "Cuộn xuống",
        about_title: "Về Bản Thân",
        about_desc: "Mình là sinh viên năm cuối chuyên ngành Khoa học Dữ liệu tại <strong>Đại học Kinh tế Tài chính TP.HCM (UEF)</strong>, nơi mình nuôi dưỡng niềm đam mê mãnh liệt với <strong>Phân tích Dữ liệu Tài chính</strong>. Hành trình của mình được dẫn dắt bởi sự tò mò không ngừng về cách dữ liệu vận hành và tác động đến thị trường toàn cầu.<br><br>Bên cạnh những con số, mình thích khám phá khía cạnh 'sáng tạo' của công nghệ. Mình đã tự học <strong>Lập trình và Thiết kế Web</strong> để đảm bảo các mô hình phân tích của mình không chỉ chính xác mà còn được trình bày đẹp mắt và thân thiện với người dùng. Mình luôn tin vào việc học tập suốt đời, luôn sẵn sàng tiếp thu các công cụ mới—từ các chiến lược giao dịch thuật toán phức tạp đến các hiệu ứng web hiện đại nhất—để kết nối giữa tài chính chuyên sâu và công nghệ.",
        ai_cta_text: "Tò mò về những kỹ năng bí mật khác của mình hay muốn trò chuyện với bản sao ảo của mình?",
        ai_cta_btn: "<i class='ph ph-robot'></i> Trò chuyện với AI Trợ lý",
        featured_title: "Dự án nổi bật: VN30 Stock Analyzer",
        featured_sub: "Công cụ nghiên cứu định lượng tương tác, so sánh các cổ phiếu VN30 với chỉ số thị trường.",
        iframe_title: "Môi trường Giao dịch Trực tiếp",
        projects_title: "Các Dự án Phân tích Khác",
        proj_1_desc: "Công cụ tối ưu hóa danh mục đầu tư sử dụng Mô hình Định giá Tài sản Vốn (CAPM) và mô phỏng Monte Carlo để xác định đường biên hiệu quả.",
        proj_2_desc: "Dự án phân tích thực nghiệm đánh giá mối quan hệ kinh tế vĩ mô và động lực tỷ giá hối đoái giữa USD và VND.",
        proj_3_desc: "Phát triển mô hình chấm điểm tín dụng chi tiết bao gồm tạo dữ liệu tổng hợp, tinh chỉnh đặc trưng chuyên sâu và mô phỏng chính sách.",
        view_code: "<i class='ph ph-github-logo'></i> Xem Mã Nguồn",
        github_cta_text: "Bạn muốn xem thêm? Khám phá toàn bộ kho lưu trữ và các kịch bản thử nghiệm của mình.",
        github_cta_btn: "<i class='ph ph-github-logo'></i> Xem thêm trên GitHub",
        contact_title: "Liên Hệ Với Mình",
        contact_sub: "Hiện mình đang tìm kiếm cơ hội thực tập vị trí Quantitative Analyst / Data Analyst.",
        footer_rights: "© 2026 <strong>ĐOÀN NGUYÊN TRÍ</strong>. Đã đăng ký Bản quyền.",
        footer_sub: "Thiết kế & Phát triển bởi Trí Đoàn | Dành cho Tài chính Định lượng"
    }
};

const langCheckbox = document.getElementById('lang-toggle');

function updateLanguage(lang) {
    // 1. Cập nhật trạng thái của nút gạt
    if (langCheckbox) {
        langCheckbox.checked = (lang === 'en');
    }
    
    // 2. Cập nhật text trên giao diện
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.innerHTML = translations[lang][key]; 
        }
    });

    // 3. Cập nhật mảng gõ chữ (Typing Effect)
    textArray = typingTexts[lang];
    textArrayIndex = 0;
    charIndex = 0;
    if (typedTextSpan) {
        typedTextSpan.textContent = ""; 
    }

    localStorage.setItem('dnt_lang', lang);
}

// Lắng nghe sự kiện GẠT NÚT
if (langCheckbox) {
    langCheckbox.addEventListener('change', () => {
        const newLang = langCheckbox.checked ? 'en' : 'vi';
        updateLanguage(newLang);
    });
}

// Chạy dịch thuật ngay khi web load xong
document.addEventListener('DOMContentLoaded', () => {
    updateLanguage(currentLang);
});