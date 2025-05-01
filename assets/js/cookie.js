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

// Function to handle user data (e.g., username)
function handleUserData(userDisplay, userInput, userSubmit) {
    // Check if a username is already stored in the cookie
    const storedName = getCookie('username');
    if (storedName) {
        userDisplay.textContent = `Welcome, ${storedName}!`;
    } else {
        userInput.style.display = 'inline-block';
        userSubmit.style.display = 'inline-block';

        // Handle user name submission
        userSubmit.addEventListener('click', () => {
            const name = userInput.value.trim();
            if (name) {
                setCookie('username', name, 365); // Store the name in a cookie for 1 year
                userDisplay.textContent = `Welcome, ${name}!`;
                userInput.style.display = 'none';
                userSubmit.style.display = 'none';
            }
        });
    }
}

window.setCookie = setCookie;
window.getCookie = getCookie;
window.handleUserData = handleUserData;