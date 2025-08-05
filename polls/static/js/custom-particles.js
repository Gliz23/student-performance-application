document.addEventListener("DOMContentLoaded", function() {
    const canvas = document.getElementById("particles-canvas");
    const ctx = canvas.getContext("2d");
    
    // Oval shape settings
    const settings = {
        ovalWidth: 1.0,  // Horizontal scale (1.0 = full width)
        ovalHeight: 0.6  // Vertical squish (0.6 = 60% height)
    };

    // Set canvas to full container size
    function resizeCanvas() {
        const container = canvas.parentElement;
        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle system
    const particles = [];
    const particleCount = Math.floor(canvas.width * canvas.height / 1000);
    
    // Create particles in oval pattern
    for (let i = 0; i < particleCount; i++) {
        const angle = Math.random() * Math.PI; // Only bottom half
        const distance = 0.7 + Math.random() * 0.3; // 70-100% of radius
        
        particles.push({
            x: canvas.width/2 + Math.cos(angle) * (canvas.width/2) * distance,
            y: Math.sin(angle) * (canvas.height * settings.ovalHeight) * distance,
            size: Math.random() * 3 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            color: `rgba(255, 215, 0, ${Math.random() * 0.5 + 0.5})`
        });
    }

    // Constrain to oval shape
    function constrainToOval(particle) {
        const centerX = canvas.width / 2;
        const radiusX = canvas.width / 2 * settings.ovalWidth;
        const radiusY = canvas.height * settings.ovalHeight;
        
        // Convert to oval coordinates
        const dx = (particle.x - centerX) / radiusX;
        const dy = particle.y / radiusY;
        const distance = dx * dx + dy * dy; // Squared distance
        
        // If outside oval or in top half
        if (distance > 1 || dy < 0) {
            const angle = Math.atan2(dy, dx);
            particle.x = centerX + Math.cos(angle) * radiusX * 0.95;
            particle.y = Math.sin(angle) * radiusY * 0.95;
            
            // Bounce effect
            particle.speedX *= -0.5;
            particle.speedY *= -0.5;
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(p => {
            // Update position
            p.x += p.speedX;
            p.y += p.speedY;
            
            // Apply oval constraint instead of rectangular bounds
            constrainToOval(p);
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            
            // Add glow
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 10;
            ctx.fill();
            
            // Reset shadow
            ctx.shadowBlur = 0;
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
});