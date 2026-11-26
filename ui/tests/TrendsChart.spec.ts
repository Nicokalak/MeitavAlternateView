import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils';
import App from '../src/App.vue';
import TrendsChart from '../src/components/TrendsChart.vue';
import { unauthorized } from '../src/js/api';

const mockMarketState = {
  marketState: 'REGULAR',
  trend: 100,
  yahoo_trend: 100,
  watchlist_trend: 1.5,
  'top-gainer': { symbol: 'AAPL' },
  'top-gainer%': { symbol: 'AAPL' },
  'top-loser': { symbol: 'MSFT' },
  'top-loser%': { symbol: 'MSFT' },
  'top-mover': { symbol: 'AAPL' },
  trending: { symbol: 'AAPL' },
  'up-down': { up: 1, down: 1 },
};

const mockTrends = {
  PRE_histo: {},
  REGULAR_histo: { '20261125T17:07:41': -3200.87 },
  POST_histo: {},
};

describe('TrendsChart fetch ordering', () => {
  let wrapper: VueWrapper | null = null;

  beforeEach(() => {
    unauthorized.value = false;
  });

  afterEach(() => {
    wrapper?.unmount();
    wrapper = null;
  });

  it('does not fetch marketState or trends on TrendsChart mount alone', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    wrapper = mount(TrendsChart);
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('fetches marketState and trends only after portfolio finishes loading', async () => {
    let resolvePortfolio!: (value: Response) => void;
    const portfolioPromise = new Promise<Response>((resolve) => {
      resolvePortfolio = resolve;
    });

    const callOrder: string[] = [];
    const fetchMock = vi.fn((url: string) => {
      callOrder.push(url);
      if (url === 'portfolio') {
        return portfolioPromise;
      }
      if (url === 'marketState') {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => mockMarketState,
        } as Response);
      }
      if (url === 'trends') {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => mockTrends,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => [],
      } as Response);
    });
    vi.stubGlobal('fetch', fetchMock);

    wrapper = mount(App);
    await flushPromises();

    // Before portfolio resolves, marketState and trends must NOT have been called
    expect(callOrder).toContain('portfolio');
    expect(callOrder).not.toContain('marketState');
    expect(callOrder).not.toContain('trends');

    // Now resolve portfolio
    resolvePortfolio({
      ok: true,
      status: 200,
      json: async () => [],
    } as Response);
    await flushPromises();

    // marketState and trends must be called after portfolio, in order
    expect(callOrder.filter((u) => u === 'marketState')).toHaveLength(1);
    expect(callOrder.filter((u) => u === 'trends')).toHaveLength(1);
    expect(callOrder.indexOf('portfolio')).toBeLessThan(callOrder.indexOf('marketState'));
    expect(callOrder.indexOf('marketState')).toBeLessThan(callOrder.indexOf('trends'));
  });
});
