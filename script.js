/**
 * 1. REVEAL EFFECT (FADE-IN & SLIDE-UP)
 */
const initReveal = () => {
    const reveals = document.querySelectorAll('.reveal');
    const observerOptions = { root: null, threshold: 0.15 };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, observerOptions);

    reveals.forEach(reveal => revealObserver.observe(reveal));
};

/**
 * 2. TYPING EFFECT (HERO SECTION)
 */
const textArray = ["Financial Data.", "Quant Analysis.", "Algorithmic Tools.", "Risk Modeling."];
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
        if (cursorSpan && !cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
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
        if (cursorSpan && !cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
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
 * 3. SCROLL LOGIC (PROGRESS BAR, SCROLLSPY, VIDEO)
 */
const video = document.getElementById("scrollVideo");
const scrollProgress = document.querySelector('.scroll-progress');
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

const handleScrollEffects = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollFraction = docHeight > 0 ? scrollTop / docHeight : 0;

    if (scrollProgress) scrollProgress.style.width = `${scrollFraction * 100}%`;

    let currentSectionId = "";
    sections.forEach(section => {
        if (scrollTop >= section.offsetTop - section.clientHeight / 3) {
            currentSectionId = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').includes(currentSectionId)) link.classList.add('active');
    });

    if (video && !isNaN(video.duration)) {
        requestAnimationFrame(() => { video.currentTime = video.duration * scrollFraction; });
    }
};

/**
 * 4. KHỞI TẠO CHUNG
 */
document.addEventListener('DOMContentLoaded', () => {
    initReveal();

    if (typedTextSpan) setTimeout(type, 1000);

    if (video) {
        const setupVideo = () => {
            video.play().then(() => {
                setTimeout(() => { video.pause(); handleScrollEffects(); }, 150);
            }).catch(e => console.log("Video playback error:", e));
        };
        if (video.readyState >= 1) setupVideo();
        else video.addEventListener('loadedmetadata', setupVideo);
    }

    window.addEventListener('scroll', handleScrollEffects, { passive: true });
});

/**
 * 5. SIRI-STYLE AI CHATBOT LOGIC
 */
const chatToggleBtn = document.getElementById('chat-toggle-btn');
const chatWindow    = document.getElementById('chat-window');
const closeChatBtn  = document.getElementById('close-chat-btn');
const chatMessages  = document.getElementById('chat-messages');
const chatInput     = document.getElementById('chat-input');
const sendChatBtn   = document.getElementById('send-chat-btn');
const siriSphere    = document.querySelector('.siri-sphere');

// FIX: Lưu lịch sử hội thoại để gửi kèm theo schema backend mới
let conversationHistory = [];

const API_URL = 'https://dnt-portfolio-backend.onrender.com/chat';

let siriAnimation;

// Khởi tạo các vòng sóng Siri
if (siriSphere) {
    for (let i = 0; i < 4; i++) {
        const ring = document.createElement('div');
        ring.className = 'siri-ring';
        ring.style.cssText = 'position:absolute;width:100%;height:100%;border-radius:50%;border:1px solid var(--accent);opacity:0;filter:blur(1px);';
        siriSphere.appendChild(ring);
    }
}

function startSiriAnimation() {
    if (typeof anime === 'undefined') return;
    siriAnimation = anime.timeline({ loop: true, autoplay: true })
        .add({ targets: '.siri-sphere', scale: [1, 1.05], opacity: [0.8, 1], easing: 'linear', duration: 200 })
        .add({ targets: '.siri-ring', scale: [1, 2.5], opacity: [0.6, 0], easing: 'linear', duration: anime.random(1200, 1800), delay: anime.stagger(200) });
}

function stopSiriAnimation() {
    if (siriAnimation) {
        siriAnimation.pause();
        anime({ targets: '.siri-sphere', scale: 1, opacity: 0.8, duration: 300 });
        anime({ targets: '.siri-ring', scale: 1, opacity: 0, duration: 300 });
    }
}

chatToggleBtn.addEventListener('click', () => {
    chatWindow.classList.toggle('hidden');
    siriSphere.classList.toggle('hidden');
    chatToggleBtn.classList.toggle('active');
    chatToggleBtn.classList.contains('active') ? startSiriAnimation() : stopSiriAnimation();
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

// FIX: Gửi history cùng message, cập nhật history sau mỗi lượt
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    chatInput.value = '';

    // Hiển thị trạng thái "đang suy nghĩ"
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot', 'typing-indicator');
    typingDiv.textContent = "Siri đang suy nghĩ...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: conversationHistory  // FIX: Gửi kèm lịch sử
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        typingDiv.remove();
        const reply = data.reply || "Xin lỗi, mình không nhận được phản hồi.";
        addMessage(reply, 'bot');

        // FIX: Cập nhật history sau mỗi lượt hội thoại (giữ tối đa 10 lượt = 20 entries)
        conversationHistory.push({ role: "user",      text: message });
        conversationHistory.push({ role: "assistant", text: reply   });
        if (conversationHistory.length > 20) conversationHistory = conversationHistory.slice(-20);

    } catch (error) {
        console.error("Chat error:", error);
        typingDiv.remove();
        addMessage("Server đang bảo trì, vui lòng thử lại sau!", 'bot');
    }
}

sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

/**
 * 6. AI AGENT CTA (ABOUT ME)
 */
const aboutAiCtaBtn = document.getElementById('about-ai-cta-btn');
if (aboutAiCtaBtn) {
    aboutAiCtaBtn.addEventListener('click', () => {
        // Mở chat nếu đang đóng
        if (chatWindow?.classList.contains('hidden')) {
            chatWindow.classList.remove('hidden');
            siriSphere?.classList.remove('hidden');
            chatToggleBtn?.classList.add('active');
            startSiriAnimation();
        }
        // Scroll đến chatbot và focus input
        chatInput?.focus();
    });
}
