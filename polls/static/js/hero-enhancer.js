class HeroPageEnhancer {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.addInteractiveElements();
            this.setupAnimations();
            this.addParticleEffect();
            this.setupCardHoverEffects();
        });
    }

    // addInteractiveElements() {
    //     // Add subtle mouse tracking for cards
    //     const cards = document.querySelectorAll('.card');
    //     cards.forEach(card => {
    //         card.addEventListener('mousemove', (e) => {
    //             const rect = card.getBoundingClientRect();
    //             const x = e.clientX - rect.left;
    //             const y = e.clientY - rect.top;
                
    //             const centerX = rect.width / 2;
    //             const centerY = rect.height / 2;
                
    //             const rotateX = (y - centerY) / 10;
    //             const rotateY = (centerX - x) / 10;
                
    //             card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`;
    //         });

    //         card.addEventListener('mouseleave', () => {
    //             card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
    //         });
    //     });
    // }

    setupAnimations() {
        // Animate elements on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        const animatedElements = document.querySelectorAll('.card, .prediction-card, .preferred-learning-style');
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }

    addParticleEffect() {
        // Create floating particles
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particle-container';
        particleContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        `;

        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: radial-gradient(circle, #3182ce 0%, transparent 70%);
                border-radius: 50%;
                opacity: 0.3;
                animation: float-particle ${10 + Math.random() * 10}s linear infinite;
                left: ${Math.random() * 100}%;
                animation-delay: ${Math.random() * 10}s;
            `;
            particleContainer.appendChild(particle);
        }

        document.body.appendChild(particleContainer);

        // Add CSS for particle animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes float-particle {
                0% {
                    transform: translateY(100vh) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 0.3;
                }
                90% {
                    opacity: 0.3;
                }
                100% {
                    transform: translateY(-100px) rotate(360deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupCardHoverEffects() {
        // Add ripple effect on button clicks
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;
                
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Add CSS for ripple effect
        const rippleStyle = document.createElement('style');
        rippleStyle.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(rippleStyle);
    }
}

// Initialize the hero page enhancer
new HeroPageEnhancer();
