import { onMounted, onUnmounted, nextTick } from 'vue';
import { initStickyCoordinator, updateStickyOffsets } from '../js/stickyCoordinator.js';

/**
 * Vue composable to manage synchronized sticky header offsets and lifecycle.
 */
export function useStickyHeaders() {
    let cleanup = null;

    onMounted(() => {
        nextTick(() => {
            cleanup = initStickyCoordinator();
        });
    });

    onUnmounted(() => {
        if (cleanup) cleanup();
    });

    return {
        updateStickyOffsets,
    };
}
