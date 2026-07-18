import { lazy } from 'react';

// Lazy load pages
const LandingPage = lazy(() => import('../pages/landing/LandingPage'));
const Upload = lazy(() => import('../pages/reports/UploadPage'));
const Viewer = lazy(() => import('../pages/reports/ViewerPage'));
const NotFound = lazy(() => import('../pages/NotFoundPage'));

export const AppRoutes = [
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/upload',
    element: <Upload />,
  },
  {
    path: '/viewer',
    element: <Viewer />,
  },
  {
    path: '/report',
    element: <Viewer />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
];