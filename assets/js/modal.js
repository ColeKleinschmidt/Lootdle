// Select modal elements
const modal = document.getElementById('modal');
const modalContent = document.querySelector('.modal-content');
const modalIframe = document.getElementById('modal-iframe');
const closeButton = document.querySelector('.modal-close');

// Function to open the modal and load external HTML content
function openModal(htmlFilePath) {
    modal.style.display = 'flex'; // Show the modal
    modalContent.classList.remove('show'); // Reset animation state
    modalIframe.src = ''; // Clear any previous iframe content
    modalIframe.classList.remove('fade-in'); // Reset fade-in animation

    setTimeout(() => {
        modalContent.classList.add('show'); // Trigger the grow animation
    }, 50); // Slight delay to ensure the transition works

    // Load the entire HTML file into the iframe
    setTimeout(() => {
        modalIframe.src = htmlFilePath; // Set the iframe source to the HTML file path
        modalIframe.classList.add('fade-in'); // Trigger the fade-in animation
    }, 500); // Delay loading until the modal has fully expanded
}

// Function to close the modal
function closeModal() {
    modalContent.classList.remove('show'); // Shrink the modal
    setTimeout(() => {
        modal.style.display = 'none'; // Hide the modal after animation
        modalIframe.src = ''; // Clear the iframe content after closing
        modalIframe.classList.remove('fade-in'); // Reset fade-in animation
    }, 500); // Match the transition duration
}

// Add event listeners
closeButton.addEventListener('click', closeModal);

// Example: Open the modal when clicking a shop item
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        closeModal();
    }
});

// Expose openModal globally
window.openModal = openModal;