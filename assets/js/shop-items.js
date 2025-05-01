// Select all shop items
const shopItems = document.querySelectorAll('.shop-item');

shopItems.forEach(item => {
    const randomDelay = Math.random() * 5; // Random delay between 0 and 5 seconds
    item.style.animationDelay = `${randomDelay}s`;
});

// Throttle function to limit hover events
function throttle(func, delay) {
    let isThrottled = false;
    return function (...args) {
        if (isThrottled) return;
        isThrottled = true;
        func.apply(this, args);
        setTimeout(() => {
            isThrottled = false;
        }, delay);
    };
}

shopItems.forEach(item => {
    const handleMouseEnter = throttle(() => {
        item.classList.add('hover-active'); // Apply hover effect
    }, 200); // 0.2s throttle

    const handleMouseLeave = () => {
        item.classList.remove('hover-active'); // Remove hover effect
    };

    item.addEventListener('mouseenter', handleMouseEnter);
    item.addEventListener('mouseleave', handleMouseLeave);
});

// Add click event to each shop item
shopItems.forEach(item => {
    item.addEventListener('click', () => {
        const contentUrl = item.getAttribute('data-content'); // Get the content URL
        openModal(contentUrl); // Call the openModal function from modal.js
    });
});