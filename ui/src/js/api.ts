import { ref } from 'vue';

/** True once the backend has rejected the current user. */
export const unauthorized = ref(false);

/** `fetch` wrapper that records authorization failures so the app can show an error page. */
export async function apiFetch(input: string, init?: RequestInit): Promise<Response> {
    const res = await fetch(input, init);
    if (res.status === 401) {
        unauthorized.value = true;
    }
    return res;
}
