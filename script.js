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

// --- THÊM BIẾN LƯU TRỮ TRÍ NHỚ CHO AI ---
let chatHistory = []; 

let siriAnimation;

// Khởi tạo các vòng sóng Siri ẩn
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

// Xử lý gửi tin nhắn có kèm "Trí nhớ"
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    chatInput.value = '';

    const typingId = "typing-" + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot');
    typingDiv.id = typingId;
    typingDiv.textContent = "Just a sec, im thinking...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('https://dnt-portfolio-backend.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                history: chatHistory // GỬI KÈM LỊCH SỬ CHO BACKEND
            })
        });

        const data = await response.json();
        
        document.getElementById(typingId).remove();

        // Xử lý nếu Backend báo lỗi Validate (ví dụ nhập quá 500 ký tự)
        if (!response.ok) {
            addMessage(data.detail || "Có lỗi xảy ra, thử lại nhé!", 'bot');
            return;
        }

        addMessage(data.reply, 'bot');

        // LƯU LẠI LỊCH SỬ SAU KHI CÓ PHẢN HỒI
        chatHistory.push({ role: "user", text: message });
        chatHistory.push({ role: "assistant", text: data.reply });
        
        // Giữ tối đa 6 tin nhắn gần nhất để không làm nặng payload
        if (chatHistory.length > 6) {
            chatHistory = chatHistory.slice(-6);
        }

    } catch (error) {
        document.getElementById(typingId).remove();
        addMessage("Opss, có lỗi xảy ra! Vui lòng thử lại sau.", 'bot');
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