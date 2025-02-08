function activateButton(button, link) {
    document.querySelectorAll('.user-button').forEach(btn => {
        btn.classList.remove('active');
    });

    button.classList.add('active');

    setTimeout(() => {
        window.location.href = link;
    }, 500);
}
