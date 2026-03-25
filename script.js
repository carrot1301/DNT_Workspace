/**
 * 1. REVEAL EFFECT (FADE-IN & SLIDE-UP)
 * Hiệu ứng xuất hiện mượt mà khi cuộn đến các section
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
 * Hiệu ứng gõ chữ Neon Glow
 */
const textArray = ["Financial Data.", "Quant Analysis.", "Algorithmic Tools.", "Risk Modeling."];
const typingDelay = 100;
const erasingDelay = 50;
const newTextDelay = 2000;
let textArrayIndex = 0;
let charIndex = 0;

// Lưu trữ các phần tử để tối ưu hiệu suất
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
    
    // Tránh lỗi chia cho 0
    const scrollFraction = docHeight > 0 ? scrollTop / docHeight : 0;

    // A. Cập nhật thanh tiến trình (Progress Bar)
    if (scrollProgress) {
        scrollProgress.style.width = `${scrollFraction * 100}%`;
    }

    // B. Scrollspy (Làm sáng Menu tương ứng với vị trí cuộn)
    let currentSectionId = "";
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        // Kích hoạt khi cuộn được 1/3 section
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

    // C. Điều khiển Video theo hướng cuộn
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
    // Chạy hiệu ứng Reveal
    initReveal();

    // Chạy hiệu ứng Gõ chữ sau 1 giây
    if (typedTextSpan) {
        setTimeout(type, 1000);
    }

    // Thiết lập Video Background
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

    // Lắng nghe sự kiện cuộn chuột
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

// Hàm bắt đầu animation Siri
function startSiriAnimation() {
    if (typeof anime === 'undefined') return; // Đề phòng thư viện chưa tải xong
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

// Hàm dừng animation Siri
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

// GỘP CHUNG: Xử lý sự kiện bật/tắt chatbox và Siri
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

// Nút tắt Chatbox
closeChatBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
    siriSphere.classList.add('hidden');
    chatToggleBtn.classList.remove('active');
    stopSiriAnimation();
});

// Hàm thêm tin nhắn vào màn hình
function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Cuộn xuống cuối
}

// Hàm xử lý gửi tin nhắn lên API
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Hiện tin nhắn của user
    addMessage(message, 'user');
    chatInput.value = '';

    // Hiện "Siri đang suy nghĩ..."
    const typingId = "typing-" + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot');
    typingDiv.id = typingId;
    typingDiv.textContent = "Siri đang suy nghĩ...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        // Gọi lên trạm Backend Render
        const response = await fetch('https://dnt-portfolio-backend.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        // Xóa chữ "Siri đang suy nghĩ..." và in câu trả lời
        document.getElementById(typingId).remove();
        addMessage(data.reply, 'bot');

    } catch (error) {
        document.getElementById(typingId).remove();
        addMessage("Server đang bảo trì, Trí ơi!", 'bot');
    }
}

// Lắng nghe sự kiện gửi tin nhắn
sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});