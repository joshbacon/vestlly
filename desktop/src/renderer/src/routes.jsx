import { Home, Search, Logs, Newspaper, CalendarRange, Brain, ServerCog, NotebookText } from 'lucide-react';
// https://lucide.dev/icons/
import HomePage from './pages/Home';
import SearchPage from './pages/Search';
import WatchlistPage from './pages/Watchlist';
import NewsPage from './pages/News';
import CalendarPage from './pages/Calendar';
import AnalysisPage from './pages/Analysis';
import AutomationPage from './pages/Automation';

export const navRoutes = [
    { path: '/', label: 'Home', icon: Home, element: <HomePage />, end: true },
    { path: '/search', label: 'Search', icon: Search, element: <SearchPage /> },
    { path: '/watchlists', label: 'Watchlists', icon: Logs, element: <WatchlistPage /> },
    { path: '/news', label: 'News', icon: Newspaper, element: <NewsPage /> },
    { path: '/calendar', label: 'Calendar', icon: CalendarRange, element: <CalendarPage /> },
    { path: '/analysis', label: 'Analysis', icon: Brain, element: <AnalysisPage /> },
    { path: '/automation', label: 'Automation', icon: ServerCog, element: <AutomationPage /> },
];