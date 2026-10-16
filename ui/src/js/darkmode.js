/**
 * Color mode manager — Vue 3 reactive theme state and Bootstrap 5 data-bs-theme synchronisation.
 */

import { ref } from 'vue';

const storedTheme = localStorage.getItem('theme');

/** Reactive theme value: 'light' | 'dark' | 'auto' */
export const theme = ref(
    storedTheme && ['light', 'dark', 'auto'].includes(storedTheme) ? storedTheme : 'auto'
);

/** Resolve 'auto' to the current OS color scheme */
export function resolveTheme(targetTheme) {
    if (targetTheme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return targetTheme;
}

/** Apply theme to the document root and update reactive state. */
export function setTheme(newTheme, persist = false) {
    theme.value = newTheme;
    if (persist) {
        if (newTheme === 'auto') {
            localStorage.removeItem('theme');
        } else {
            localStorage.setItem('theme', newTheme);
        }
    }
    document.documentElement.setAttribute('data-bs-theme', resolveTheme(newTheme));
}

/** Return the current preferred theme. */
export function getPreferredTheme() {
    return theme.value;
}

// Initialise theme immediately on module load
setTheme(theme.value, false);

// React to OS-level colour scheme changes when in 'auto' mode
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === 'auto') {
        document.documentElement.setAttribute('data-bs-theme', resolveTheme('auto'));
    }
});
