// Function to set a cookie
function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
}

// Function to get a cookie
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(`${name}=`)) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

// Select elements
const exclamationPoint = document.getElementById('exclamation-point');
const textBubble = document.getElementById('text-bubble');
const userInput = document.getElementById('user-input');
const userSubmit = document.getElementById('user-submit');
const userDisplay = document.getElementById('user-display');

// Check if a username is already stored in the cookie
const storedName = getCookie('username');
if (storedName) {
    // If a username exists, display the welcome message and hide the exclamation point
    userDisplay.textContent = `Welcome, ${storedName}!`;
    textBubble.style.display = 'block'; // Ensure the text bubble is visible
    userInput.style.display = 'none'; // Hide the input field
    userSubmit.style.display = 'none'; // Hide the submit button
    exclamationPoint.style.display = 'none'; // Hide the exclamation point
} else {
    // If no username exists, show the exclamation point and allow user input
    exclamationPoint.style.display = 'block';

    // Toggle text bubble visibility when the exclamation point is clicked
    exclamationPoint.addEventListener('click', () => {
        if (textBubble.style.display === 'none') {
            textBubble.style.display = 'block'; // Show the text bubble
        } else {
            textBubble.style.display = 'none'; // Hide the text bubble
        }
    });

    // Handle user name submission
    userSubmit.addEventListener('click', () => {
        const name = userInput.value.trim();
        if (name) {
            setCookie('username', name, 365); // Store the name in a cookie for 1 year
            userDisplay.textContent = `Welcome, ${name}!`;
            userInput.style.display = 'none'; // Hide the input field
            userSubmit.style.display = 'none'; // Hide the submit button
            exclamationPoint.style.display = 'none'; // Hide the exclamation point
        }
    });
}