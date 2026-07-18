import { Suspense } from 'react';
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import { AppRoutes } from './AppRoutes';
import { PageLoader } from '@/components/ui/PageLoader';

const withSuspense = (routes: RouteObject[]): RouteObject[] =>
  routes.map((route) => ({
    ...route,
    element: route.element ? (
      <Suspense fallback={<PageLoader />}>{route.element}</Suspense>
    ) : undefined,
  }));

export const router = createBrowserRouter(withSuspense(AppRoutes));
