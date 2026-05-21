/**
 * Responsibility: initialize/toggle CRT overlay while keeping it viewport-safe.
 * Public API: window.LootdleCrtFilter.init({ buttonId, overlayId }).
 */
(function initializeCrtFilter() {
    function init({
        buttonId = 'toggle-crt',
        overlayId = 'crt-overlay'
    } = {}) {
        const button = document.getElementById(buttonId);
        const overlay = document.getElementById(overlayId);

        if (!button || !overlay) {
            return null;
        }

        const setEnabled = (enabled) => {
            overlay.style.display = enabled ? 'block' : 'none';
        };

        const isEnabled = () => overlay.style.display !== 'none';

        button.addEventListener('click', () => {
            setEnabled(!isEnabled());
        });

        return {
            setEnabled,
            isEnabled
        };
    }

    window.LootdleCrtFilter = {
        init
    };

    init();
})();
