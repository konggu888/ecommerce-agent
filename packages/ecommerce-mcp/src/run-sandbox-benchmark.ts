import { runBenchmarkReport } from './benchmark-report';
import { SimShop } from './backtest-engine';

export function createDefaultSandboxShop(): SimShop {
  return {
    id: 'SANDBOX-SHOP',
    products: [{
      id: 'PRODUCT-001',
      price: 89,
      marginPerOrder: 28.5,
      stock: 600,
      replenishmentDays: 7,
      safetyStockDays: 5
    }],
    campaigns: [{
      id: 'CAMPAIGN-001',
      productId: 'PRODUCT-001',
      budget: 120,
      bid: 2,
    }],
    cash: 42600
  };
}

export function runDefaultSandboxBenchmark(rounds = 30) {
  return runBenchmarkReport(createDefaultSandboxShop(), rounds);
}
