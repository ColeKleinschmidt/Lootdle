/**
 * Responsibility: preload/toggle the landing-page background media in one place.
 * Public API: window.LootdleBackgroundMediaLoader.init(options).
 */
(function initializeBackgroundMediaLoader() {
    function preloadImage(source, onError) {
        const image = new Image();
        image.decoding = 'async';
        image.src = source;

        if (onError) {
            image.onerror = onError;
        }
    }

    function init({
        toggleButtonId = 'toggle-background',
        targetSelector = 'body',
        daySource = 'assets/backgrounds/Day_Mode.gif',
        nightSource = 'assets/backgrounds/Night_Mode.gif',
        fallbackColor = '#424242'
    } = {}) {
        const toggleButton = document.getElementById(toggleButtonId);
        const target = document.querySelector(targetSelector);

        if (!toggleButton || !target) {
            return null;
        }

        let mode = 'day';
        const reducedMotionQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;

        const applyBackground = () => {
            if (reducedMotionQuery && reducedMotionQuery.matches) {
                target.style.backgroundImage = 'none';
                target.style.backgroundColor = fallbackColor;
                return;
            }

            target.style.backgroundColor = '';
            target.style.backgroundImage = mode === 'day'
                ? `url('${daySource}')`
                : `url('${nightSource}')`;
        };

        preloadImage(daySource, () => {
            if (mode === 'day') {
                target.style.backgroundImage = 'none';
                target.style.backgroundColor = fallbackColor;
            }
        });
        preloadImage(nightSource);

        toggleButton.addEventListener('click', () => {
            mode = mode === 'day' ? 'night' : 'day';
            applyBackground();
        });

        if (reducedMotionQuery) {
            const syncReducedMotion = () => applyBackground();
            if (typeof reducedMotionQuery.addEventListener === 'function') {
                reducedMotionQuery.addEventListener('change', syncReducedMotion);
            } else if (typeof reducedMotionQuery.addListener === 'function') {
                reducedMotionQuery.addListener(syncReducedMotion);
            }
        }

        applyBackground();

        return {
            getMode: () => mode,
            toggle() {
                mode = mode === 'day' ? 'night' : 'day';
                applyBackground();
            }
        };
    }

    window.LootdleBackgroundMediaLoader = {
        init
    };

    init();
})();
