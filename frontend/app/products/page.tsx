'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Search, Filter, ExternalLink, Wifi, Smartphone, Shield, Cloud, Globe, MessageCircle } from 'lucide-react';
import { products as productsApi } from '@/lib/api';

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  'Connectivity': Wifi,
  'Mobile': Smartphone,
  'Security': Shield,
  'Cloud & Productivity': Cloud,
  'IoT & Physical': Globe,
  'Communication': MessageCircle,
};

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'Connectivity': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-100' },
  'Mobile': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-100' },
  'Security': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-100' },
  'Cloud & Productivity': { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-100' },
  'IoT & Physical': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-100' },
  'Communication': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-100' },
};

interface Product {
  id: string; category: string; product_name: string; description: string;
  unit: string; price_display: string; price_min_inr: number; price_max_inr: number;
  one_time_setup_inr: number; min_contract_months: number; requires_gstin: boolean;
  typical_install_days: number; target_segments: string; available_city_tiers: string;
  min_employees: number; min_sites: number;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCat, setSelectedCat] = useState('All');
  const [selectedSegment, setSelectedSegment] = useState('All');

  useEffect(() => {
    productsApi.list().then(data => {
      setProducts(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const categories = ['All', ...Array.from(new Set(products.map(p => p.category)))];
  const segments = ['All', 'micro', 'prof', 'multi', 'mfg'];

  const filtered = products.filter(p => {
    const matchCat = selectedCat === 'All' || p.category === selectedCat;
    const matchSeg = selectedSegment === 'All' || p.target_segments?.includes(selectedSegment);
    const matchSearch = !search || p.product_name.toLowerCase().includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSeg && matchSearch;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="section flex items-center justify-between h-16 gap-3">
          <div className="flex items-center gap-3">
            <Link href="/" className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></Link>
            <h1 className="font-bold text-slate-900">Product Catalogue</h1>
            <span className="badge-gray text-xs">{products.length} products</span>
          </div>
          <Link href="/advisor" className="btn-primary text-sm py-2.5">
            Get My Bundle →
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-slate-100">
        <div className="section py-4 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-48 max-w-xs">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input className="input py-2 pl-9 text-sm" placeholder="Search products..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map(cat => (
              <button key={cat} onClick={() => setSelectedCat(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${selectedCat === cat ? 'bg-red-600 text-white border-red-600' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'}`}>
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="section py-8">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl p-5 border border-slate-100">
                <div className="shimmer h-4 w-24 rounded mb-3" />
                <div className="shimmer h-5 w-48 rounded mb-2" />
                <div className="shimmer h-3 w-full rounded mb-1" />
                <div className="shimmer h-3 w-3/4 rounded" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-400">No products match your filters.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map(product => {
              const catStyle = CATEGORY_COLORS[product.category] || { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-100' };
              const CatIcon = CATEGORY_ICONS[product.category] || Wifi;
              return (
                <div key={product.id} className="card p-5 flex flex-col gap-3">
                  {/* Category Badge */}
                  <div className="flex items-start justify-between gap-2">
                    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${catStyle.bg} ${catStyle.text} ${catStyle.border}`}>
                      <CatIcon className="w-3.5 h-3.5" />
                      {product.category}
                    </div>
                    <span className="text-xs text-slate-400 font-mono">{product.id}</span>
                  </div>

                  {/* Name & Price */}
                  <div>
                    <h3 className="font-bold text-slate-900 mb-0.5">{product.product_name}</h3>
                    <div className="text-lg font-bold text-red-600">{product.price_display}</div>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-500 leading-relaxed flex-1">{product.description}</p>

                  {/* Attributes */}
                  <div className="grid grid-cols-2 gap-y-1.5 text-xs text-slate-500 bg-slate-50 rounded-xl p-3">
                    <div><span className="text-slate-400">Unit: </span><span className="font-medium text-slate-700">{product.unit}</span></div>
                    <div><span className="text-slate-400">Setup: </span><span className="font-medium text-slate-700">₹{product.one_time_setup_inr.toLocaleString('en-IN')}</span></div>
                    <div><span className="text-slate-400">Contract: </span><span className="font-medium text-slate-700">{product.min_contract_months}mo min</span></div>
                    <div><span className="text-slate-400">Install: </span><span className="font-medium text-slate-700">{product.typical_install_days}d</span></div>
                    {product.requires_gstin && (
                      <div className="col-span-2"><span className="badge-yellow text-xs">Requires GSTIN</span></div>
                    )}
                    <div className="col-span-2 text-slate-400 text-xs">Tiers: {product.available_city_tiers}</div>
                  </div>

                  {/* CTA */}
                  <Link href={`/advisor`} className="btn-primary text-xs py-2.5 text-center">
                    Get a Bundle Quote →
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
