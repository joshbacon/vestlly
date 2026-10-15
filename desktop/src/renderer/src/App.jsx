import { Outlet } from 'react-router-dom';
import { WatchlistProvider } from './reducers/WatchlistContext';
import NavBar from './components/Nav';
import LoadingPage from './pages/Loading';
import ErrorPage from './pages/Error';
import { useState, useEffect } from 'react';

function App() {
  const [status, setStatus] = useState('loading'); // 'loading' | 'ready' | 'error'
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [marketData, setMarketData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.electronAPI.onLoadProgress((p) => setProgress(p));

    window.electronAPI.onLoadComplete((result) => {
      if (result.success) {
        setMarketData(result.data);
        setStatus('ready');
      } else {
        setError(result.error);
        setStatus('error');
      }
    });

    return () => window.electronAPI.removeLoadListeners();
  }, []);

  if (status === 'loading') return <LoadingPage progress={progress} />;
  if (status === 'error') return <ErrorPage message={error} />;
  return <MainApp data={marketData} />;
}

function MainApp({ data }) {
  return <div className="flex h-screen">
    <NavBar />
    <main className="flex-1 overflow-auto bg-mist-950">
      <WatchlistProvider>
        <Outlet context={{ marketData: data }} />
      </WatchlistProvider>
    </main>
  </div>
}

export default App;