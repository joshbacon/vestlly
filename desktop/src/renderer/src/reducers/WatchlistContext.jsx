import { createContext, useContext, useReducer, useEffect, useState } from 'react';

const WatchlistContext = createContext(null);

function watchlistReducer(state, action) {
  switch (action.type) {
    case 'CREATE_LIST':
      return [...state, {
        id: crypto.randomUUID(),
        name: action.name,
        tickers: [],
        createdAt: new Date().toISOString(),
      }];

    case 'DELETE_LIST':
      return state.filter(list => list.id !== action.listId);

    case 'RENAME_LIST':
      return state.map(list =>
        list.id === action.listId ? { ...list, name: action.name } : list
      );

    case 'ADD_TICKER':
      return state.map(list =>
        list.id === action.listId && !list.tickers.includes(action.ticker)
          ? { ...list, tickers: [...list.tickers, action.ticker] }
          : list
      );

    case 'REMOVE_TICKER':
      return state.map(list =>
        list.id === action.listId
          ? { ...list, tickers: list.tickers.filter(t => t !== action.ticker) }
          : list
      );

    case 'LOAD':
      return action.watchlists;

    default:
      return state;
  }
}

export function WatchlistProvider({ children }) {
  const [watchlists, dispatch] = useReducer(watchlistReducer, []);
  const [hasLoaded, setHasLoaded] = useState(false);

  // load from persistence on mount
  useEffect(() => {
    window.electronAPI.loadWatchlists().then((saved) => {
      if (saved) dispatch({ type: 'LOAD', watchlists: saved });
      setHasLoaded(true);
    });
  }, []);

  // persist on every change
  useEffect(() => {
    if (!hasLoaded) return;
    window.electronAPI.saveWatchlists(watchlists);
  }, [watchlists, hasLoaded]);

  return (
    <WatchlistContext.Provider value={{ watchlists, dispatch }}>
      {children}
    </WatchlistContext.Provider>
  );
}

export function useWatchlists() {
  const ctx = useContext(WatchlistContext);
  if (!ctx) throw new Error('useWatchlists must be used within WatchlistProvider');
  return ctx;
}