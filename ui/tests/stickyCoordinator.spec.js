import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { updateStickyOffsets, initStickyCoordinator } from '../src/js/stickyCoordinator.js';

describe('Sticky Header Coordinator', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    document.documentElement.style.removeProperty('--toolbar-sticky-top');
    document.documentElement.style.removeProperty('--table-sticky-top');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('sets CSS variables to 0px when elements are not in DOM', () => {
    updateStickyOffsets();
    expect(document.documentElement.style.getPropertyValue('--toolbar-sticky-top')).toBe('0px');
    expect(document.documentElement.style.getPropertyValue('--table-sticky-top')).toBe('0px');
  });

  it('calculates Tier 2 and Tier 3 sticky offsets dynamically from element heights', () => {
    const market = document.createElement('div');
    market.id = 'market-status-container';
    Object.defineProperty(market, 'offsetHeight', { value: 50, configurable: true });
    document.body.appendChild(market);

    const toolbar = document.createElement('div');
    toolbar.className = 'portfolio-toolbar';
    Object.defineProperty(toolbar, 'offsetHeight', { value: 42, configurable: true });
    document.body.appendChild(toolbar);

    updateStickyOffsets();

    expect(document.documentElement.style.getPropertyValue('--toolbar-sticky-top')).toBe('50px');
    expect(document.documentElement.style.getPropertyValue('--table-sticky-top')).toBe('92px');
  });

  it('adjusts offsets on mobile dimensions with text and button wrapping', () => {
    const market = document.createElement('div');
    market.id = 'market-status-container';
    Object.defineProperty(market, 'offsetHeight', { value: 72, configurable: true });
    document.body.appendChild(market);

    const toolbar = document.createElement('div');
    toolbar.className = 'portfolio-toolbar';
    Object.defineProperty(toolbar, 'offsetHeight', { value: 84, configurable: true });
    document.body.appendChild(toolbar);

    updateStickyOffsets();

    expect(document.documentElement.style.getPropertyValue('--toolbar-sticky-top')).toBe('72px');
    expect(document.documentElement.style.getPropertyValue('--table-sticky-top')).toBe('156px');
  });

  it('supports .fixed-table-toolbar selector for backwards compatibility', () => {
    const market = document.createElement('div');
    market.id = 'market-status-container';
    Object.defineProperty(market, 'offsetHeight', { value: 48, configurable: true });
    document.body.appendChild(market);

    const toolbar = document.createElement('div');
    toolbar.className = 'fixed-table-toolbar';
    Object.defineProperty(toolbar, 'offsetHeight', { value: 40, configurable: true });
    document.body.appendChild(toolbar);

    updateStickyOffsets();

    expect(document.documentElement.style.getPropertyValue('--toolbar-sticky-top')).toBe('48px');
    expect(document.documentElement.style.getPropertyValue('--table-sticky-top')).toBe('88px');
  });

  it('initializes ResizeObserver and event listeners, then cleans up correctly', () => {
    const market = document.createElement('div');
    market.id = 'market-status-container';
    Object.defineProperty(market, 'offsetHeight', { value: 48, configurable: true });
    document.body.appendChild(market);

    const toolbar = document.createElement('div');
    toolbar.className = 'portfolio-toolbar';
    Object.defineProperty(toolbar, 'offsetHeight', { value: 44, configurable: true });
    document.body.appendChild(toolbar);

    const observedElements = [];
    const unobservedElements = [];
    let disconnected = false;

    class MockResizeObserver {
      constructor(callback) {
        this.callback = callback;
      }
      observe(el) {
        observedElements.push(el);
      }
      unobserve(el) {
        unobservedElements.push(el);
      }
      disconnect() {
        disconnected = true;
      }
    }

    vi.stubGlobal('ResizeObserver', MockResizeObserver);

    const addEventListenerSpy = vi.spyOn(window, 'addEventListener');
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

    const cleanup = initStickyCoordinator();

    expect(observedElements).toContain(market);
    expect(observedElements).toContain(toolbar);
    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
    expect(addEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function));

    cleanup();

    expect(disconnected).toBe(true);
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function));
  });
});
