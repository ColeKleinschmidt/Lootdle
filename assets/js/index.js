const gameDescription = document.getElementById('game-description');
const letters = gameDescription.querySelectorAll('span');

// Assign a unique --index value to each letter
letters.forEach((letter, index) => {
    letter.style.setProperty('--index', index);
});