/*!
 * Color mode toggler — refactored for Vue 3 reactivity.
 * Original: Bootstrap docs (https://getbootstrap.com/)
 * Copyright 2011-2023 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

import { ref } from 'vue';

/** Reactive theme value: 'light' | 'dark' | 'auto' */
export const theme = ref(localStorage.getItem('theme') ?? 'auto');

/** Return the system-preferred or stored theme. */
export function getPreferredTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/** Apply theme to the document root and update reactive state. */
export function setTheme(newTheme) {
    theme.value = newTheme;
    const resolved =
        newTheme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : newTheme;
    document.documentElement.setAttribute('data-bs-theme', resolved);
}

/** Update active-state UI for the theme switcher buttons (if present). */
export function showActiveTheme(selectedTheme, focus = false) {
    const themeSwitcher = document.querySelector('#bd-theme');
    if (!themeSwitcher) return;

    const themeSwitcherText = document.querySelector('#bd-theme-text');
    const activeThemeIcon = document.querySelector('.theme-icon-active use');
    const btnToActive = document.querySelector(`[data-bs-theme-value="${selectedTheme}"]`);
    if (!btnToActive) return;
    const svgOfActiveBtn = btnToActive.querySelector('svg use')?.getAttribute('href');

    document.querySelectorAll('[data-bs-theme-value]').forEach((el) => {
        el.classList.remove('active');
        el.setAttribute('aria-pressed', 'false');
    });

    btnToActive.classList.add('active');
    btnToActive.setAttribute('aria-pressed', 'true');
    if (activeThemeIcon && svgOfActiveBtn) activeThemeIcon.setAttribute('href', svgOfActiveBtn);
    if (themeSwitcherText) {
        themeSwitcher.setAttribute(
            'aria-label',
            `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`
        );
    }
    if (focus) themeSwitcher.focus();
}

// Initialise on import: apply stored/preferred theme immediately.
setTheme(getPreferredTheme());

// React to OS-level colour scheme changes.
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const stored = localStorage.getItem('theme');
    if (stored !== 'light' && stored !== 'dark') {
        setTheme(getPreferredTheme());
    }
});

// Wire up any [data-bs-theme-value] toggle buttons once DOM is ready.
window.addEventListener('DOMContentLoaded', () => {
    showActiveTheme(getPreferredTheme());
    document.querySelectorAll('[data-bs-theme-value]').forEach((toggle) => {
        toggle.addEventListener('click', () => {
            const selected = toggle.getAttribute('data-bs-theme-value');
            setTheme(selected);
            showActiveTheme(selected, true);
        });
    });
});
