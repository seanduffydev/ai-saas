// Mock for Jest so tests don't require react-router-dom to resolve (e.g. in CI).
import React from 'react';

export const BrowserRouter = ({ children }) => children;
export const Routes = ({ children }) => children;
export const Route = ({ element }) => element;
export const Navigate = () => null;
export const useNavigate = () => () => {};
export const useLocation = () => ({ pathname: '/', state: null });
export const Link = ({ to, children, ...rest }) =>
  React.createElement('a', { href: to, ...rest }, children);
