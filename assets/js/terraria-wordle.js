document.addEventListener("DOMContentLoaded", () => {
    const items = [
        { name: "Wooden Sword", damage: 5, speed: 10 },
        { name: "Iron Sword", damage: 10, speed: 8 },
        { name: "Gold Sword", damage: 15, speed: 7 },
        { name: "Diamond Sword", damage: 20, speed: 6 },
        { name: "Terraria Sword", damage: 25, speed: 5 }
    ];

    let targetItem = items[Math.floor(Math.random() * items.length)];
    let attempts = 0;

    const input = document.getElementById("guess-input");
    const submitBtn = document.getElementById("submit-btn");
    const feedback = document.getElementById("feedback");
    const attemptsDiv = document.getElementById("attempts");

    submitBtn.addEventListener("click", () => {
        const guess = input.value.trim();
        const guessedItem = items.find(item => item.name.toLowerCase() === guess.toLowerCase());

        if (!guessedItem) {
            feedback.textContent = "Item not found. Try again!";
            return;
        }

        attempts++;
        attemptsDiv.textContent = `Attempts: ${attempts}`;

        if (guessedItem.name === targetItem.name) {
            feedback.textContent = `Correct! The item is ${targetItem.name}.`;
            input.disabled = true;
            submitBtn.disabled = true;
            return;
        }

        let feedbackText = `Not correct! Here’s how your guess compares: `;
        if (guessedItem.damage > targetItem.damage) {
            feedbackText += `Damage: Lower. `;
        } else if (guessedItem.damage < targetItem.damage) {
            feedbackText += `Damage: Higher. `;
        } else {
            feedbackText += `Damage: Correct. `;
        }

        if (guessedItem.speed > targetItem.speed) {
            feedbackText += `Speed: Lower. `;
        } else if (guessedItem.speed < targetItem.speed) {
            feedbackText += `Speed: Higher. `;
        } else {
            feedbackText += `Speed: Correct. `;
        }

        feedback.textContent = feedbackText;
        input.value = ""; // Clear input
    });
});
