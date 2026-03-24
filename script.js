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
 * Tối ưu: Chỉ truy vấn DOM một lần duy nhất bên ngoài hàm scroll
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

    // C. Điều khiển Video theo hướng cuộn (Sử dụng requestAnimationFrame)
    if (video && !isNaN(video.duration)) {
        requestAnimationFrame(() => {
            video.currentTime = video.duration * scrollFraction;
        });
    }
};

/**
 * 4. KHỞI TẠO (INITIALIZATION)
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
            // "Làm nóng" video bằng cách chạy một chút rồi dừng
            video.play().then(() => {
                setTimeout(() => {
                    video.pause();
                    handleScrollEffects(); // Đồng bộ vị trí video với vị trí cuộn hiện tại
                }, 150);
            }).catch(e => console.log("Video playback error:", e));
        };

        // Nếu video đã sẵn sàng metadata
        if (video.readyState >= 1) {
            setupVideo();
        } else {
            video.addEventListener('loadedmetadata', setupVideo);
        }
    }

    // Lắng nghe sự kiện cuộn chuột với tùy chọn passive để mượt hơn
    window.addEventListener('scroll', handleScrollEffects, { passive: true });
});