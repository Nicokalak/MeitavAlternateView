import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils';
import App from '../src/App.vue';
import { unauthorized } from '../src/js/api';

function stubFetch(status: number): void {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: async () => [],
    }),
  );
}

describe('unauthorized error path', () => {
  let wrapper: VueWrapper | null = null;

  beforeEach(() => {
    unauthorized.value = false;
  });

  afterEach(() => {
    wrapper?.unmount();
    wrapper = null;
  });

  it('renders the 401 error page when the API rejects the user', async () => {
    stubFetch(401);
    wrapper = mount(App);
    await flushPromises();

    expect(unauthorized.value).toBe(true);
    expect(wrapper!.find('[role="alert"]').text()).toContain('Error 401 - Unauthorized');
    expect(wrapper!.find('.container-fluid').exists()).toBe(false);
  });

  it('keeps the app visible when requests succeed', async () => {
    stubFetch(200);
    wrapper = mount(App);
    await flushPromises();

    expect(unauthorized.value).toBe(false);
    expect(wrapper!.find('[role="alert"]').exists()).toBe(false);
    expect(wrapper!.find('.container-fluid').exists()).toBe(true);
  });
});
