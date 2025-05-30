import React from 'react';
import {
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider
} from 'react-router-dom';
import NotFoundPage from './components/pages/NotFoundPage';
import OrthologuePage from './components/pages/OrthologuePage';
import OrthologueETEPage from './components/pages/OrthologueETEPage';
import ETETreeSearch from './components/phylo/ETETreeSearch';
import App from './App';

// Define the application routes
export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/*" element={<App />}>
      <Route index element={<OrthologuePage />} />
      <Route path="orthologues" element={<OrthologuePage />} />
      <Route path="orthologues-ete" element={<OrthologueETEPage />} />
      <Route path="ete-search" element={<ETETreeSearch />} />
      <Route path="*" element={<NotFoundPage />} />
    </Route>
  )
);

const Router = () => {
  return <RouterProvider router={router} />;
};

export default Router;