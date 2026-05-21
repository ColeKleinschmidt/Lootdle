/**
 * Responsibility: centralize viewport breakpoints and keep responsive CSS state in sync.
 * Public API: window.LootdleBreakpoints.{ values, getViewport(), onChange(listener) }.
 */
(function initializeBreakpoints() {
    const values = Object.freeze({
        mobile: 480,
        tablet: 768
    });
    const root = document.documentElement;
    const listeners = new Set();
    let viewport = '';

    root.style.setProperty('--bp-mobile', `${values.mobile}px`);
    root.style.setProperty('--bp-tablet', `${values.tablet}px`);

    const updateViewportMetrics = () => {
        root.style.setProperty('--viewport-height', `${window.innerHeight}px`);
    };

    const getViewport = () => {
        const width = window.innerWidth;
        if (width <= values.mobile) {
            return 'mobile';
        }

        if (width <= values.tablet) {
            return 'tablet';
        }

        return 'desktop';
    };

    const notify = () => {
        const nextViewport = getViewport();
        if (nextViewport === viewport) {
            return;
        }

        viewport = nextViewport;
        root.dataset.viewport = viewport;
        listeners.forEach(listener => listener(viewport));
    };

    const refresh = () => {
        updateViewportMetrics();
        notify();
    };

    window.addEventListener('resize', refresh, { passive: true });
    window.addEventListener('orientationchange', refresh, { passive: true });

    refresh();

    window.LootdleBreakpoints = {
        values,
        getViewport: () => viewport,
        onChange(listener) {
            listeners.add(listener);
            listener(viewport);
            return () => listeners.delete(listener);
        }
    };
})();
