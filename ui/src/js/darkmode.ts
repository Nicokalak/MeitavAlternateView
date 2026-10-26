/**
 * Color mode manager — Vue 3 reactive theme state and Bootstrap 5 data-bs-theme synchronisation.
 */

import { ref, type Ref } from 'vue';

/** Theme preference selectable by the user. */
export type Theme = 'light' | 'dark' | 'auto';

/** Theme actually applied to the document after resolving 'auto'. */
export type ResolvedTheme = 'light' | 'dark';

const THEMES: readonly Theme[] = ['light', 'dark', 'auto'];

function isTheme(value: string | null): value is Theme {
    return value !== null && (THEMES as readonly string[]).includes(value);
}

const storedTheme = localStorage.getItem('theme');

/** Reactive theme value: 'light' | 'dark' | 'auto' */
export const theme: Ref<Theme> = ref<Theme>(isTheme(storedTheme) ? storedTheme : 'auto');

/** Resolve 'auto' to the current OS color scheme */
export function resolveTheme(targetTheme: Theme): ResolvedTheme {
    if (targetTheme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return targetTheme;
}

/** Apply theme to the document root and update reactive state. */
export function setTheme(newTheme: Theme, persist = false): void {
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
export function getPreferredTheme(): Theme {
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
