'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Plus, Minus, X, CheckCircle, Info, ArrowRight, Package, Zap, Loader2, ShoppingCart, AlertTriangle } from 'lucide-react';
import { recommendations, products as productsApi } from '@/lib/api';

const CATEGORY_COLORS: Record<string, string> = {
  'Connectivity': 'bg-blue-50 text-blue-700 border-blue-100',
  'Communication': 'bg-green-50 text-green-700 border-green-100',
  'Cloud & Productivity': 'bg-cyan-50 text-cyan-700 border-cyan-100',
  'Security': 'bg-orange-50 text-orange-700 border-orange-100',
  'IoT & Physical': 'bg-purple-50 text-purple-700 border-purple-100',
};

interface BundleItem {
  product_id: string; product_name: string; category: string; description: string;
  unit: string; quantity: number; unit_price_inr: number; monthly_cost_inr: number;
  setup_cost_inr: number; is_mandatory: boolean; reason: string; install_days: number;
}

interface AltBundle {
  name: string; description: string; items: BundleItem[];
  total_monthly_inr: number; total_setup_inr: number;
}

export default function BundlePage() {
  const router = useRouter();
  const [rec, setRec] = useState<Record<string, unknown> | null>(null);
  const [items, setItems] = useState<BundleItem[]>([]);
  const [allProducts, setAllProducts] = useState<Record<string, unknown>[]>([]);
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('last_recommendation');
    if (stored) {
      const parsed = JSON.parse(stored);
      setRec(parsed);
      setItems(parsed.primary_bundle || []);
    }
    productsApi.list().then(setAllProducts).catch(() => {});
    setLoading(false);
  }, []);

  const totalMonthly = items.reduce((s, i) => s + i.monthly_cost_inr, 0);
  const totalSetup = items.reduce((s, i) => s + i.setup_cost_inr, 0);
  const maxInstall = items.reduce((m, i) => Math.max(m, i.install_days), 0);

  const selectedIds = new Set(items.map(i => i.product_id));

  const updateQty = (pid: string, delta: number) => {
    setItems(prev => prev.map(i => {
      if (i.product_id !== pid) return i;
      const newQty = Math.max(1, i.quantity + delta);
      return { ...i, quantity: newQty, monthly_cost_inr: +(i.unit_price_inr * newQty).toFixed(2), setup_cost_inr: +(i.setup_cost_inr / i.quantity * newQty).toFixed(2) };
    }));
  };

  const removeItem = (pid: string) => {
    setItems(prev => prev.filter(i => i.product_id !== pid || i.is_mandatory));
  };

  const addProduct = (product: Record<string, unknown>) => {
    if (selectedIds.has(product.id as string)) return;
    const unitPrice = ((product.price_min_inr as number) + (product.price_max_inr as number)) / 2;
    setItems(prev => [...prev, {
      product_id: product.id as string,
      product_name: product.product_name as string,
      category: product.category as string,
      description: product.description as string,
      unit: product.unit as string,
      quantity: 1,
      unit_price_inr: unitPrice,
      monthly_cost_inr: unitPrice,
      setup_cost_inr: product.one_time_setup_inr as number,
      is_mandatory: false,
      reason: 'Added manually',
      install_days: product.typical_install_days as number,
    }]);
  };

  const loadAlternative = (alt: AltBundle) => {
    const mapped: BundleItem[] = (alt.items as any[]).map((i: any) => ({
      product_id: i.product_id as string,
      product_name: i.product_name as string,
      category: '',
      description: '',
      unit: '',
      quantity: i.quantity as number,
      unit_price_inr: i.monthly_cost_inr as number,
      monthly_cost_inr: i.monthly_cost_inr as number,
      setup_cost_inr: i.setup_cost_inr as number,
      is_mandatory: true,
      reason: i.reason as string,
      install_days: 5,
    }));
    setItems(mapped);
    setShowAlternatives(false);
  };

  const proceedToCheckout = () => {
    localStorage.setItem('bundle_items', JSON.stringify(items));
    localStorage.setItem('bundle_totals', JSON.stringify({ monthly: totalMonthly, setup: totalSetup }));
    router.push('/checkout');
  };

  if (loading || !rec) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      {loading ? <Loader2 className="w-8 h-8 animate-spin text-red-500" /> : (
        <div className="text-center">
          <Package className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-700 mb-2">No Bundle Yet</h2>
          <p className="text-slate-500 mb-6">Talk to the AI advisor first to get your personalised recommendation.</p>
          <Link href="/advisor" className="btn-primary">Go to Advisor</Link>
        </div>
      )}
    </div>
  );

  const alternatives = (rec.alternative_bundles as AltBundle[]) || [];
  const ineligible = (rec.eligibility_checks as Record<string, Record<string, string>>)?.ineligible || {};
  const availableToAdd = allProducts.filter(p => !selectedIds.has(p.id as string) && !ineligible[p.id as string]);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="section flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link href="/advisor" className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></Link>
            <h1 className="font-bold text-slate-900">Bundle Builder</h1>
          </div>
          <div className="flex items-center gap-3">
            {alternatives.length > 0 && (
              <button onClick={() => setShowAlternatives(!showAlternatives)} className="btn-ghost text-sm">
                {showAlternatives ? 'Hide' : 'View'} Alternatives ({alternatives.length})
              </button>
            )}
            <button onClick={proceedToCheckout} className="btn-primary text-sm py-2.5">
              Proceed to Checkout <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="section py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bundle Items */}
        <div className="lg:col-span-2 space-y-4">
          {/* Explanation */}
          <div className="bg-white rounded-2xl border border-slate-100 p-5">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-slate-600 leading-relaxed">{rec.explanation as string}</p>
            </div>
          </div>

          {/* Selected Products */}
          <div className="space-y-3">
            <h2 className="font-semibold text-slate-900">Your Selected Products ({items.length})</h2>
            {items.map(item => (
              <div key={item.product_id} className="bg-white rounded-2xl border border-slate-100 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center flex-wrap gap-2 mb-1">
                      <h3 className="font-semibold text-slate-900 text-sm">{item.product_name}</h3>
                      <span className={`badge text-xs border ${CATEGORY_COLORS[item.category] || 'bg-slate-50 text-slate-600 border-slate-100'}`}>{item.category}</span>
                      {item.is_mandatory && <span className="badge-red text-xs">Required</span>}
                    </div>
                    {item.description && <p className="text-xs text-slate-500 mb-2 line-clamp-1">{item.description}</p>}
                    <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-lg inline-block">{item.reason}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="font-bold text-slate-900 text-sm">₹{item.monthly_cost_inr.toLocaleString('en-IN')}/mo</div>
                    {item.setup_cost_inr > 0 && <div className="text-xs text-slate-400">+₹{item.setup_cost_inr.toLocaleString('en-IN')} setup</div>}
                    <div className="text-xs text-slate-400 mt-0.5">{item.unit}</div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-50">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Qty:</span>
                    <div className="flex items-center gap-1">
                      <button onClick={() => updateQty(item.product_id, -1)} className="w-6 h-6 rounded-md bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors">
                        <Minus className="w-3 h-3" />
                      </button>
                      <span className="w-6 text-center text-sm font-semibold">{item.quantity}</span>
                      <button onClick={() => updateQty(item.product_id, 1)} className="w-6 h-6 rounded-md bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors">
                        <Plus className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                  {!item.is_mandatory && (
                    <button onClick={() => removeItem(item.product_id)} className="text-xs text-slate-400 hover:text-red-500 flex items-center gap-1 transition-colors">
                      <X className="w-3.5 h-3.5" /> Remove
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Add Optional Products */}
          {availableToAdd.length > 0 && (
            <div>
              <h2 className="font-semibold text-slate-900 mb-3">Add Optional Products</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {availableToAdd.slice(0, 6).map(p => (
                  <div key={p.id as string} className="bg-white rounded-xl border border-slate-100 border-dashed p-4 hover:border-red-300 hover:bg-red-50/30 transition-all cursor-pointer group" onClick={() => addProduct(p)}>
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="font-medium text-sm text-slate-800 group-hover:text-red-700">{p.product_name as string}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{p.price_display as string}</div>
                      </div>
                      <div className="w-7 h-7 rounded-lg bg-slate-100 group-hover:bg-red-100 flex items-center justify-center transition-colors flex-shrink-0">
                        <Plus className="w-4 h-4 text-slate-500 group-hover:text-red-600" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ineligible */}
          {Object.keys(ineligible).length > 0 && (
            <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span className="text-sm font-semibold text-amber-800">Products Not Available for Your Profile</span>
              </div>
              <div className="space-y-1">
                {Object.entries(ineligible).map(([pid, reason]) => (
                  <div key={pid} className="text-xs text-amber-700"><span className="font-medium">{pid}:</span> {reason as string}</div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Summary Panel */}
        <div className="space-y-4">
          <div className="card-premium p-6 sticky top-20">
            <h2 className="font-bold text-slate-900 mb-4">Bundle Summary</h2>
            <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
              {items.map(i => (
                <div key={i.product_id} className="flex justify-between text-sm">
                  <span className="text-slate-600 truncate flex-1">{i.product_name} ×{i.quantity}</span>
                  <span className="font-medium text-slate-900 ml-2 flex-shrink-0">₹{i.monthly_cost_inr.toLocaleString('en-IN')}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-slate-100 pt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Monthly Subscription</span>
                <span className="font-semibold text-slate-900">₹{totalMonthly.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">One-time Setup</span>
                <span className="font-semibold text-slate-900">₹{totalSetup.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">GST (18%)</span>
                <span className="font-semibold text-slate-900">₹{Math.round(totalMonthly * 0.18).toLocaleString('en-IN')}/mo</span>
              </div>
              <div className="border-t border-slate-100 pt-2 flex justify-between">
                <span className="font-bold text-slate-900">Total (with GST)</span>
                <span className="font-bold text-red-600 text-lg">₹{Math.round(totalMonthly * 1.18).toLocaleString('en-IN')}/mo</span>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-slate-400 bg-slate-50 rounded-lg px-3 py-2">
              <Zap className="w-3.5 h-3.5 text-orange-400" />
              Est. {maxInstall} days to activation
            </div>
            <button onClick={proceedToCheckout} className="btn-primary w-full mt-4">
              Proceed to Checkout <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Alternatives */}
          {showAlternatives && alternatives.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-slate-900">Alternative Bundles</h3>
              {alternatives.map((alt) => (
                <div key={alt.name} className="bg-white border border-slate-200 rounded-2xl p-4">
                  <div className="font-semibold text-slate-900 text-sm mb-1">{alt.name}</div>
                  <p className="text-xs text-slate-500 mb-3">{alt.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-red-600 font-bold">₹{alt.total_monthly_inr.toLocaleString('en-IN')}/mo</span>
                    <button onClick={() => loadAlternative(alt)} className="text-xs btn-ghost py-1.5 px-3">Use This Bundle</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
