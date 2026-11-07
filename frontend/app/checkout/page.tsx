'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle, CreditCard, Building, FileText, Loader2, Shield, Tag } from 'lucide-react';
import { quotes, orders } from '@/lib/api';

export default function CheckoutPage() {
  const router = useRouter();
  const [step, setStep] = useState<'details' | 'review' | 'processing' | 'confirmed'>('details');
  const [bundleItems, setBundleItems] = useState<Record<string, unknown>[]>([]);
  const [totals, setTotals] = useState({ monthly: 0, setup: 0 });
  const [form, setForm] = useState({
    customer_name: '', customer_email: '', customer_phone: '',
    billing_address: '', gstin_for_invoice: '', contract_months: 12,
  });
  const [quote, setQuote] = useState<Record<string, unknown> | null>(null);
  const [orderId, setOrderId] = useState<string | null>(null);
  const [recId, setRecId] = useState<string | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const items = JSON.parse(localStorage.getItem('bundle_items') || '[]');
    const t = JSON.parse(localStorage.getItem('bundle_totals') || '{"monthly":0,"setup":0}');
    const rec = localStorage.getItem('last_recommendation');
    if (rec) {
      const r = JSON.parse(rec);
      setRecId(r.recommendation_id || null);
    }
    setBundleItems(items);
    setTotals(t);
  }, []);

  const lineItems = bundleItems.map(i => ({
    product_id: i.product_id,
    quantity: i.quantity,
  }));

  const handleSubmitDetails = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.customer_name || !form.customer_email || !form.customer_phone || !form.billing_address) {
      setError('Please fill in all required fields.');
      return;
    }
    setError('');
    setStep('review');
  };

  const handlePlaceOrder = async () => {
    setStep('processing');
    try {
      const q = await quotes.create({
        ...form,
        line_items: lineItems,
        recommendation_id: recId,
        business_profile_id: profileId,
      });
      setQuote(q);
      const o = await orders.create({ quote_id: q.id });
      setOrderId(o.id);
      localStorage.setItem('last_order_id', o.id);
      setStep('confirmed');
    } catch (e) {
      setError((e as Error).message);
      setStep('review');
    }
  };

  const gstAmount = Math.round(totals.monthly * 0.18);
  const totalWithGst = totals.monthly + gstAmount;

  if (step === 'confirmed' && orderId) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-white rounded-3xl border border-slate-100 shadow-xl p-8 text-center">
        <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-emerald-600" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Order Confirmed! 🎉</h1>
        <p className="text-slate-500 mb-2">Your order has been placed successfully.</p>
        <div className="bg-slate-50 rounded-xl p-4 mb-6 text-sm">
          <div className="flex justify-between mb-1"><span className="text-slate-500">Order Number</span><span className="font-bold text-slate-900">{(quote as Record<string, unknown>)?.quote_number as string || 'QT-DEMO'}</span></div>
          <div className="flex justify-between mb-1"><span className="text-slate-500">Monthly Subscription</span><span className="font-semibold">₹{totals.monthly.toLocaleString('en-IN')}/mo</span></div>
          <div className="flex justify-between mb-1"><span className="text-slate-500">Setup Fee</span><span className="font-semibold">₹{totals.setup.toLocaleString('en-IN')}</span></div>
          <div className="flex justify-between text-emerald-600 border-t border-slate-100 pt-2 mt-2"><span className="font-semibold">Payment Status</span><span className="font-bold">✅ Simulated Complete</span></div>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <Link href={`/kyc?order_id=${orderId}`} className="btn-primary flex-1">
            Complete KYC →
          </Link>
          <Link href={`/track?order_id=${orderId}`} className="btn-secondary flex-1">
            Track Order
          </Link>
        </div>
        <p className="text-xs text-slate-400 mt-4">⚠️ This is a simulated payment for the hackathon demo. No real charges occur.</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="section flex items-center h-16 gap-3">
          <button onClick={() => step === 'review' ? setStep('details') : router.back()} className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></button>
          <h1 className="font-bold text-slate-900">Checkout</h1>
          <div className="ml-auto flex items-center gap-2 text-xs text-slate-400">
            {['details', 'review', 'processing'].map((s, i) => (
              <div key={s} className="flex items-center gap-1">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step === s ? 'bg-red-600 text-white' : step === 'confirmed' || i < ['details','review','processing'].indexOf(step) ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-400'}`}>
                  {i + 1}
                </div>
                <span className="capitalize hidden sm:inline">{s}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="section py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {step === 'details' && (
            <form onSubmit={handleSubmitDetails} className="card-premium p-6 space-y-5">
              <h2 className="font-bold text-slate-900 text-lg">Customer Details</h2>
              {error && <div className="bg-red-50 border border-red-100 text-red-700 text-sm px-4 py-3 rounded-xl">{error}</div>}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div><label className="label">Full Name *</label><input className="input" required value={form.customer_name} onChange={e => setForm(f => ({...f, customer_name: e.target.value}))} placeholder="Rajesh Kumar" /></div>
                <div><label className="label">Email Address *</label><input className="input" type="email" required value={form.customer_email} onChange={e => setForm(f => ({...f, customer_email: e.target.value}))} placeholder="rajesh@business.com" /></div>
                <div><label className="label">Phone Number *</label><input className="input" required value={form.customer_phone} onChange={e => setForm(f => ({...f, customer_phone: e.target.value}))} placeholder="+91 98765 43210" /></div>
                <div><label className="label">GSTIN (for invoice)</label><input className="input" value={form.gstin_for_invoice} onChange={e => setForm(f => ({...f, gstin_for_invoice: e.target.value}))} placeholder="Optional — for GST invoice" /></div>
              </div>
              <div><label className="label">Billing Address *</label><textarea className="input resize-none" rows={3} required value={form.billing_address} onChange={e => setForm(f => ({...f, billing_address: e.target.value}))} placeholder="Shop No. 12, Market Yard, Pune, Maharashtra 411037" /></div>
              <div>
                <label className="label">Preferred Contract Duration</label>
                <div className="flex gap-3">
                  {[12, 24].map(m => (
                    <button type="button" key={m} onClick={() => setForm(f => ({...f, contract_months: m}))}
                      className={`flex-1 py-3 rounded-xl border-2 font-semibold text-sm transition-all ${form.contract_months === m ? 'border-red-500 bg-red-50 text-red-700' : 'border-slate-200 text-slate-600 hover:border-slate-300'}`}>
                      {m} Months {m === 12 ? '(Standard)' : '(Save more)'}
                    </button>
                  ))}
                </div>
              </div>
              <div className="bg-amber-50 border border-amber-100 rounded-xl px-4 py-3 flex items-start gap-2">
                <Shield className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-amber-800">Your information is protected. KYC documents will be processed with your explicit consent in the next step.</p>
              </div>
              <button type="submit" className="btn-primary w-full">Continue to Review</button>
            </form>
          )}

          {step === 'review' && (
            <div className="space-y-4">
              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 text-lg mb-4">Order Review</h2>
                <div className="space-y-3 mb-4">
                  {bundleItems.map((item) => (
                    <div key={item.product_id as string} className="flex justify-between text-sm py-2 border-b border-slate-50 last:border-0">
                      <div>
                        <div className="font-medium text-slate-800">{item.product_name as string} ×{item.quantity as number}</div>
                        <div className="text-xs text-slate-400">{item.unit as string}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-slate-900">₹{(item.monthly_cost_inr as number).toLocaleString('en-IN')}/mo</div>
                        {(item.setup_cost_inr as number) > 0 && <div className="text-xs text-slate-400">+₹{(item.setup_cost_inr as number).toLocaleString('en-IN')} setup</div>}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="border-t border-slate-100 pt-4 space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-slate-500">Subtotal</span><span>₹{totals.monthly.toLocaleString('en-IN')}/mo</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">GST @18%</span><span>₹{gstAmount.toLocaleString('en-IN')}/mo</span></div>
                  <div className="flex justify-between font-bold text-base pt-1 border-t border-slate-100"><span>Total Monthly</span><span className="text-red-600">₹{totalWithGst.toLocaleString('en-IN')}/mo</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">One-time Setup</span><span className="font-semibold">₹{totals.setup.toLocaleString('en-IN')}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Contract</span><span>{form.contract_months} months</span></div>
                </div>
              </div>
              <div className="card-premium p-4">
                <h3 className="font-semibold text-slate-900 mb-3 text-sm">Billing Details</h3>
                <div className="text-sm text-slate-600 space-y-1">
                  <div>{form.customer_name} · {form.customer_email}</div>
                  <div>{form.customer_phone}</div>
                  <div className="text-xs text-slate-400">{form.billing_address}</div>
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-blue-500" />
                <div className="text-sm text-blue-700"><strong>Simulated Payment</strong> — No real transaction will occur. This is a hackathon demo.</div>
              </div>
              {error && <div className="bg-red-50 border border-red-100 text-red-700 text-sm px-4 py-3 rounded-xl">{error}</div>}
              <button onClick={handlePlaceOrder} className="btn-primary w-full text-base py-4">
                ✓ Confirm & Place Order
              </button>
            </div>
          )}

          {step === 'processing' && (
            <div className="card-premium p-12 text-center">
              <Loader2 className="w-12 h-12 animate-spin text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-slate-900 mb-2">Processing Your Order...</h2>
              <p className="text-slate-500">Creating your quote and placing the order.</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="card-premium p-5 h-fit sticky top-20">
          <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2"><Tag className="w-4 h-4 text-red-500" /> Quick Summary</h3>
          <div className="space-y-2 text-sm mb-4">
            <div className="flex justify-between"><span className="text-slate-500">Products</span><span className="font-semibold">{bundleItems.length}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Monthly (incl. GST)</span><span className="font-bold text-red-600">₹{totalWithGst.toLocaleString('en-IN')}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Setup Fee</span><span className="font-semibold">₹{totals.setup.toLocaleString('en-IN')}</span></div>
          </div>
          <div className="space-y-2 pt-3 border-t border-slate-100">
            {[
              { icon: Shield, text: 'Secure checkout' },
              { icon: FileText, text: 'Digital KYC included' },
              { icon: Building, text: 'GSTIN invoice available' },
            ].map(f => (
              <div key={f.text} className="flex items-center gap-2 text-xs text-slate-500">
                <f.icon className="w-3.5 h-3.5 text-emerald-500" />{f.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
