import React from 'react';
import {
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider
} from 'react-router-dom';
import NotFoundPage from './components/pages/NotFoundPage';
import OrthologuePage from './components/pages/OrthologuePage';
import ETETreeSearch from './components/phylo/ETETreeSearch';
import App from './App';

// Router configuration options with recommended future flags
const routerOptions = {
  basename: '/',
  future: {
    v7_normalizeFormMethod: true,
    v7_startTransition: true,
    v7_relativeSplatPath: true
  },
};

// Define the application routes - removed Home, Orthologues is now the default
export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/*" element={<App />}>
      <Route index element={<OrthologuePage />} />
      <Route path="orthologues" element={<OrthologuePage />} />
      <Route path="ete-search" element={<ETETreeSearch />} />
      <Route path="*" element={<NotFoundPage />} />
    </Route>
  ),
  routerOptions
);

const Router = () => {
  return <RouterProvider router={router} />;
};

export default Router;