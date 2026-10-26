/**
 * Sticky Header Coordinator for synchronized 3-tier sticky layout.
 * Calculates dynamic offsets for Tier 2 (.portfolio-toolbar) and Tier 3 (.portfolio-thead).
 */

/**
 * Synchronizes sticky stacking coordinates across all viewport breakpoints.
 */
export function updateStickyOffsets() {
    if (typeof document === 'undefined') return;

    const marketEl = document.getElementById('market-status-container');
    const toolbarEl = document.querySelector('.fixed-table-toolbar') ||
                      document.querySelector('.portfolio-toolbar');

    const marketH = marketEl ? marketEl.offsetHeight : 0;
    const toolbarH = toolbarEl ? toolbarEl.offsetHeight : 0;
    const totalOffset = marketH + toolbarH;

    // Expose CSS variables for pure CSS sticky positioning
    document.documentElement.style.setProperty('--toolbar-sticky-top', `${marketH}px`);
    document.documentElement.style.setProperty('--table-sticky-top', `${totalOffset}px`);

    // Coordinate with bootstrap-table sticky-header extension if present
    if (typeof window !== 'undefined' && window.$) {
        window.$('.sticky-header-container').css('top', `${totalOffset}px`);
        const table = window.$('#table').data('bootstrap.table');
        if (table) {
            table.options.stickyHeaderOffsetY = totalOffset;
        }
    }
}

/**
 * Initializes observers and event listeners. Returns a cleanup function.
 */
export function initStickyCoordinator() {
    let observer = null;
    let observedMarket = null;
    let observedToolbar = null;

    const setupObserver = () => {
        if (typeof ResizeObserver === 'undefined') return;
        if (!observer) {
            observer = new ResizeObserver(() => updateStickyOffsets());
        }

        const marketEl = document.getElementById('market-status-container');
        const toolbarEl = document.querySelector('.fixed-table-toolbar') ||
                          document.querySelector('.portfolio-toolbar');

        if (marketEl && marketEl !== observedMarket) {
            if (observedMarket) observer.unobserve(observedMarket);
            observer.observe(marketEl);
            observedMarket = marketEl;
        }
        if (toolbarEl && toolbarEl !== observedToolbar) {
            if (observedToolbar) observer.unobserve(observedToolbar);
            observer.observe(toolbarEl);
            observedToolbar = toolbarEl;
        }
    };

    const onResizeOrScroll = () => {
        setupObserver();
        updateStickyOffsets();
    };

    if (typeof window !== 'undefined') {
        window.addEventListener('resize', onResizeOrScroll);
        window.addEventListener('scroll', onResizeOrScroll);
    }

    setupObserver();
    updateStickyOffsets();

    return () => {
        if (observer) observer.disconnect();
        if (typeof window !== 'undefined') {
            window.removeEventListener('resize', onResizeOrScroll);
            window.removeEventListener('scroll', onResizeOrScroll);
        }
    };
}
