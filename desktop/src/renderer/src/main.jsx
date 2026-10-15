import './assets/main.css'
import '@fontsource/open-sans/400.css'; // regular
import '@fontsource/open-sans/500.css'; // medium
import '@fontsource/open-sans/700.css'; // bold

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Search from './pages/Search';
import { navRoutes } from './routes';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <Routes>
        <Route path="/" element={<App />}>
          {navRoutes.map(({ path, element, end }) => (
            <Route
              key={path}
              index={end}
              path={end ? undefined : path.replace(/^\//, '')}
              element={element}
            />
          ))}
        </Route>
      </Routes>
    </HashRouter>
  </StrictMode>
)
