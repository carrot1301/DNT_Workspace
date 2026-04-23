document.addEventListener("DOMContentLoaded", (event) => {
  gsap.registerPlugin(ScrollTrigger);

  // --- 1. CINEMATIC TIMELINE (SCENE 1 -> SCENE 2) ---
  // Tạo một Timeline gắn liền với thẻ #cinematic-container
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: "#cinematic-container",
      start: "top top",      
      end: "+=200%",         // Pin container trong suốt khoảng cuộn gấp 2 lần màn hình
      pin: true,
      scrub: 1               // Nối tiếp hiệu ứng mượt mà khi cuộn chuột
    }
  });

  // PHẦN 1: Chuyển cảnh - "Lao vào" (Dive In)
  tl.to(".scene-1", {
    scale: 5,                  
    opacity: 0,                
    filter: "blur(20px)",      
    duration: 1.2,
    ease: "power3.in"          
  })

  // Bắn chớp sáng màu tím để che giấu sự biến đổi
  .to(".flash-overlay", {
    opacity: 1,
    duration: 0.3
  }, "-=0.3") 

  // PHẦN 2: Lộ diện cảnh mới (Reveal Scene 2)
  .set(".scene-1", { visibility: "hidden" }) 
  .set(".scene-2", { visibility: "visible" }) 

  // Khối AI trung tâm zoom ngược từ xa lại
  .fromTo(".scene-2", 
    { scale: 0.5, opacity: 0 }, 
    { scale: 1, opacity: 1, duration: 1, ease: "power2.out" }
  )

  // Tắt chớp
  .to(".flash-overlay", { opacity: 0, duration: 0.5 }, "<") 

  // PHẦN 3: Các bảng biểu Pop-up lên
  .fromTo(".panel", 
    { y: 100, opacity: 0, scale: 0.8 }, 
    { 
      y: 0, 
      opacity: 1, 
      scale: 1, 
      duration: 1, 
      stagger: 0.15,         
      ease: "back.out(1.2)"  
    }, 
    "-=0.5" 
  );

  // Sau khi user cuộn xong chuỗi timeline, mới thả cho panel Float
  let isFloating = false;
  ScrollTrigger.create({
    trigger: "#cinematic-container",
    start: "top top",
    end: "+=200%",
    onLeave: () => {
       if(!isFloating) {
          gsap.to(".panel", {
            y: -15,               
            duration: 2, 
            yoyo: true,           
            repeat: -1,           
            ease: "sine.inOut",   
            stagger: 0.2          
          });
          isFloating = true;
       }
    }
  });


  // --- 1.5. HIỆU ỨNG TRỒI LÊN CỦA TERMINAL SHOWCASE ---
  gsap.from(".showcase-mockup-wrapper", {
    opacity: 0,
    y: 100,
    scale: 0.95,
    duration: 1.2,
    ease: "power3.out",
    scrollTrigger: {
      trigger: ".product-showcase",
      start: "top 80%"
    }
  });

  // --- 2. CÁC HIỆU ỨNG CÒN LẠI (STATS & PRICING) ---
  
  gsap.from(".pricing-card", {
    opacity: 0,
    y: 50,
    duration: 0.8,
    stagger: 0.15,
    ease: "back.out(1.7)",
    scrollTrigger: {
      trigger: ".pricing-grid",
      start: "top 80%",
    }
  });

  // --- (Khu vực Video Background Đã Chuyển Sang Chế Độ AutoPlay ở index.html) ---
});
