// Select all shop items
const shopItems = document.querySelectorAll('.shop-item');

// Add hover effect for title and description
shopItems.forEach(item => {
    const title = item.getAttribute('data-title');
    const description = item.getAttribute('data-description');

    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.innerHTML = `<strong>${title}</strong><br>${description}`;

    // Append tooltip to the shop item
    item.appendChild(tooltip);
});

// Assign a random delay to each shop item
shopItems.forEach(item => {
    const randomDelay = Math.random() * 3; // Random delay between 0 and 3 seconds
    item.style.setProperty('--random-delay', randomDelay.toFixed(2)); // Set the CSS variable
});

