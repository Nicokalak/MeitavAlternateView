import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import PortfolioTable from '../src/components/PortfolioTable.vue';

const mockPortfolio = [
  {
    symbol: 'AAPL',
    type: 'e',
    quantity: 10,
    last_price: 150,
    cost: 130,
    change: 5,
    percent_change: 3.45,
    day_val: 50,
    total_val: 1500,
    total_change: 200,
    api_data: { shortName: 'Apple Inc.', longName: 'Apple Inc.' }
  },
  {
    symbol: 'MSFT',
    type: 'e',
    quantity: 20,
    last_price: 300,
    cost: 275,
    change: -10,
    percent_change: -3.23,
    day_val: -200,
    total_val: 6000,
    total_change: 500,
    api_data: { shortName: 'Microsoft Corporation', longName: 'Microsoft Corporation' }
  },
  {
    symbol: 'GOOG',
    type: 'w',
    quantity: 0,
    last_price: 180,
    cost: 0,
    change: 2,
    percent_change: 1.12,
    day_val: 0,
    total_val: 0,
    total_change: 0,
    api_data: { shortName: 'Alphabet Inc.', longName: 'Alphabet Inc.' }
  }
];

describe('PortfolioTable tfoot updating with search', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => JSON.parse(JSON.stringify(mockPortfolio)),
    }));
  });

  it('updates tfoot calculations when search query is applied and restored', async () => {
    const wrapper = mount(PortfolioTable);
    await flushPromises();

    // Helper to get all non-empty footer cell text contents
    const getFooterTexts = () =>
      wrapper.findAll('tfoot tr td')
        .map(td => td.text().trim())
        .filter(text => text.length > 0);

    // Initial state: both AAPL & MSFT are aggregated in portfolio totals (GOOG is watchlist)
    // Day's Value: 50 + (-200) = -150
    // Profit/Loss: 200 + 500 = 700
    // Total Value: 1500 + 6000 = 7,500
    const initialFooters = getFooterTexts();
    expect(initialFooters).toContain('-150');
    expect(initialFooters).toContain('700');
    expect(initialFooters).toContain('7,500');

    // 1. Search for AAPL only
    const searchInput = wrapper.find('#customSearch');
    await searchInput.setValue('AAPL');
    await flushPromises();

    // Verify tbody shows only AAPL
    const rows = wrapper.findAll('tbody tr');
    expect(rows.length).toBe(1);
    expect(rows[0].text()).toContain('AAPL');

    // tfoot should now ONLY reflect AAPL
    // Day's Value: 50
    // Profit/Loss: 200
    // Value: 1,500
    const aaplFooters = getFooterTexts();
    expect(aaplFooters).toContain('50');
    expect(aaplFooters).toContain('200');
    expect(aaplFooters).toContain('1,500');
    expect(aaplFooters).not.toContain('7,500');
    expect(aaplFooters).not.toContain('-150');

    // 2. Search for MSFT only
    await searchInput.setValue('MSFT');
    await flushPromises();

    const msftFooters = getFooterTexts();
    expect(msftFooters).toContain('-200');
    expect(msftFooters).toContain('500');
    expect(msftFooters).toContain('6,000');
    expect(msftFooters).not.toContain('1,500');

    // 3. Search for watchlist item GOOG (type 'w')
    // Watchlist items must not contribute to portfolio sums
    await searchInput.setValue('GOOG');
    await flushPromises();

    const googFooters = getFooterTexts();
    expect(googFooters).toContain('0');
    expect(googFooters).toContain('0%');

    // 4. Clear search query - restores full aggregates
    await searchInput.setValue('');
    await flushPromises();

    const restoredFooters = getFooterTexts();
    expect(restoredFooters).toContain('-150');
    expect(restoredFooters).toContain('700');
    expect(restoredFooters).toContain('7,500');
  });

  it('filters by shortName and updates tfoot accordingly', async () => {
    const wrapper = mount(PortfolioTable);
    await flushPromises();

    const searchInput = wrapper.find('#customSearch');
    await searchInput.setValue('Microsoft');
    await flushPromises();

    const footerTexts = wrapper.findAll('tfoot tr td')
      .map(td => td.text().trim())
      .filter(text => text.length > 0);

    expect(footerTexts).toContain('-200');
    expect(footerTexts).toContain('500');
    expect(footerTexts).toContain('6,000');
  });
});
