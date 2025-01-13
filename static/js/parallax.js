document.addEventListener('DOMContentLoaded', function() {
    const parallaxContainer = document.querySelector('.parallax-container');
    if (!parallaxContainer) return;

    const parallaxImage = document.querySelector('.parallax-image');
    
    // Handle mouse movement for parallax effect
    parallaxContainer.addEventListener('mousemove', function(e) {
        const rect = parallaxContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Calculate movement percentage (-5% to 5%)
        const moveX = (x / rect.width - 0.5) * 10;
        const moveY = (y / rect.height - 0.5) * 10;
        
        // Apply transform with smooth transition
        parallaxImage.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.1)`;
    });
    
    // Reset position when mouse leaves
    parallaxContainer.addEventListener('mouseleave', function() {
        parallaxImage.style.transform = 'translate(0, 0) scale(1)';
    });

    // Handle scroll-based parallax
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * 0.3;
        
        if (parallaxContainer.getBoundingClientRect().top < window.innerHeight && 
            parallaxContainer.getBoundingClientRect().bottom > 0) {
            parallaxImage.style.transform = `translate3d(0, ${rate}px, 0)`;
        }
    });
});
