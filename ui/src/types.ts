/**
 * Shared domain types for the portfolio UI.
 */

/** Market data attached to a portfolio row. Dynamic `<state>Market*` keys are numeric. */
export interface ApiData {
    shortName?: string;
    longName?: string;
    earningsTimestamp?: number;
    dividendDate?: number;
    trailingAnnualDividendRate?: number;
    regularMarketVolume?: number;
    regularMarketDayLow?: number;
    regularMarketDayHigh?: number;
    regularMarketPreviousClose?: number;
    averageDailyVolume10Day?: number;
    averageDailyVolume3Month?: number;
    fiftyTwoWeekLow?: number;
    fiftyTwoWeekHigh?: number;
    fiftyDayAverage?: number;
    averageAnalystRating?: string;
    [key: string]: number | string | undefined;
}

/** A single portfolio or watchlist row returned by `/portfolio`. */
export interface PortfolioRow {
    symbol: string;
    type: string;
    quantity: number;
    last_price: number;
    cost: number;
    change: number;
    percent_change: number;
    day_val: number;
    total_val: number;
    total_change: number;
    total_cost?: number;
    principle_change?: number;
    gain?: number;
    weight?: number;
    p_or_c?: string;
    strike?: number | string;
    expiration?: string;
    api_data?: ApiData;
}

/** Response of `/ticker/<symbol>`. */
export interface TickerResponse {
    'market-state-4calc'?: string;
    stock: { api_data: ApiData };
}

/** Editable watchlist entry used by the modal. */
export interface WatchlistEntry {
    _key: number;
    symbol: string;
    qty: number | string;
    cost: number | string;
}

/** Watchlist entry as persisted by the backend. */
export interface WatchlistPayload {
    symbol: string;
    quantity: number;
    cost: number;
}

/** A symbol reference inside the `/marketState` response. */
export interface SymbolRef {
    symbol: string;
}

/** Response of `/marketState`. */
export interface MarketState {
    marketState: string;
    trend: number;
    yahoo_trend: number;
    watchlist_trend: number;
    'top-gainer': SymbolRef;
    'top-gainer%': SymbolRef;
    'top-mover': SymbolRef;
    'top-loser': SymbolRef;
    'top-loser%': SymbolRef;
    'up-down': { up: number; down: number };
    trending: SymbolRef;
}

/** Chart.js time-series point map: timestamp string to value. */
export type TrendSeries = Record<string, number>;

/** Response of `/trends`. */
export interface TrendsResponse {
    PRE_histo: TrendSeries;
    REGULAR_histo: TrendSeries;
    POST_histo: TrendSeries;
}
