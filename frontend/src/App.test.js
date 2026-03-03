import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app title', async () => {
  render(<App />);
  const title = await screen.findByText(/Commodity Forecasting Lab/i);
  expect(title).toBeInTheDocument();
});
