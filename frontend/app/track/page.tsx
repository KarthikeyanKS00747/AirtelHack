'use client';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Package, CheckCircle, Clock, Loader2, Phone, MessageSquare } from 'lucide-react';
import { orders as ordersApi } from '@/lib/api';

const STAGE_ICONS: Record<string, React.ReactNode> = {
  placed: <Package className="w-5 h-5" />,
  kyc_pending: <Clock className="w-5 h-5" />,
  kyc_review: <Clock className="w-5 h-5" />,
  kyc_complete: <CheckCircle className="w-5 h-5" />,
  serviceability_check: <Clock className="w-5 h-5" />,
  scheduled: <Clock className="w-5 h-5" />,
  in_progress: <Loader2 className="w-5 h-5" />,
  activated: <CheckCircle className="w-5 h-5" />,
};

function TrackContent() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get('order_id') || localStorage.getItem('last_order_id') || '';
  const [orderData, setOrderData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderId) { setLoading(false); return; }
    const load = async () => {
      try {
        const { token } = { token: localStorage.getItem('token') };
        if (!token) {
          const { auth } = await import('@/lib/api');
          const res = await auth.demoLogin();
          localStorage.setItem('token', res.access_token);
        }
        const data = await ordersApi.get(orderId);
        setOrderData(data);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, [orderId]);

  if (loading) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <Loader2 className="w-8 h-8 animate-spin text-red-500" />
    </div>
  );

  if (!orderId || error) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="text-center">
        <Package className="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-slate-700 mb-2">No Order Found</h2>
        <p className="text-slate-500 mb-6">{error || 'Please complete checkout to start tracking.'}</p>
        <Link href="/advisor" className="btn-primary">Start a New Order</Link>
      </div>
    </div>
  );

  const order = (orderData?.order || {}) as Record<string, unknown>;
  const quote = (orderData?.quote || {}) as Record<string, unknown>;
  const lifecycle = (orderData?.lifecycle || []) as Record<string, unknown>[];
  const milestones = (orderData?.milestones || []) as Record<string, unknown>[];
  const nextAction = (orderData?.next_action || {}) as Record<string, string>;
  const currentIndex = lifecycle.findIndex(l => l.is_current);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="section flex items-center h-16 gap-3">
          <Link href="/" className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></Link>
          <div>
            <h1 className="font-bold text-slate-900">Order Tracking</h1>
            <p className="text-xs text-slate-400">Order {order.order_number as string}</p>
          </div>
          <div className="ml-auto">
            <span className={`badge ${order.status === 'activated' ? 'badge-green' : order.status === 'cancelled' ? 'badge-red' : 'badge-blue'}`}>
              {(order.status as string)?.replace(/_/g, ' ').toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="section py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="lg:col-span-2 space-y-4">
          {/* Next Action Card */}
          {nextAction.label && (
            <div className={`rounded-2xl p-5 border ${order.status === 'activated' ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-100'}`}>
              <div className="font-semibold text-slate-900 mb-1">Next Action</div>
              <p className="text-sm text-slate-600">{nextAction.label}</p>
              {nextAction.action === 'kyc' && (
                <Link href={`/kyc?order_id=${orderId}`} className="btn-primary mt-3 text-sm inline-flex">
                  Upload KYC Documents →
                </Link>
              )}
            </div>
          )}

          {/* Lifecycle Steps */}
          <div className="card-premium p-6">
            <h2 className="font-bold text-slate-900 mb-6">Activation Progress</h2>
            <div className="space-y-6">
              {lifecycle.map((stage: Record<string, unknown>, i: number) => {
                const completed = stage.completed as boolean;
                const isCurrent = stage.is_current as boolean;
                const isPending = !completed && !isCurrent;
                return (
                  <div key={stage.stage as string} className="flex gap-4">
                    {/* Icon */}
                    <div className="flex flex-col items-center">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${completed ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-red-600 text-white ring-4 ring-red-100' : 'bg-slate-100 text-slate-300'}`}>
                        {completed ? <CheckCircle className="w-5 h-5" /> : STAGE_ICONS[stage.stage as string] || <Clock className="w-5 h-5" />}
                      </div>
                      {i < lifecycle.length - 1 && (
                        <div className={`w-0.5 h-8 mt-2 ${completed ? 'bg-emerald-300' : 'bg-slate-100'}`} />
                      )}
                    </div>
                    {/* Content */}
                    <div className="flex-1 pb-4">
                      <div className={`font-semibold text-sm ${isPending ? 'text-slate-300' : 'text-slate-900'}`}>{stage.label as string}</div>
                      <p className={`text-xs mt-0.5 leading-relaxed ${isPending ? 'text-slate-300' : 'text-slate-500'}`}>{stage.description as string}</p>
                      {isCurrent && <div className="inline-flex items-center gap-1.5 mt-2 text-xs text-red-600 font-medium bg-red-50 px-2 py-1 rounded-full"><div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />Current Stage</div>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Activity Log */}
          {milestones.length > 0 && (
            <div className="card-premium p-5">
              <h3 className="font-bold text-slate-900 mb-4">Activity Log</h3>
              <div className="space-y-3">
                {milestones.map((m: Record<string, unknown>, i: number) => (
                  <div key={i} className="flex gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0 mt-1.5" />
                    <div>
                      <div className="font-medium text-slate-800">{m.label as string}</div>
                      <div className="text-xs text-slate-400">{new Date(m.occurred_at as string).toLocaleString('en-IN')} · {m.description as string}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="card-premium p-5">
            <h3 className="font-bold text-slate-900 mb-4">Order Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Order No.</span><span className="font-semibold text-xs">{order.order_number as string}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Monthly</span><span className="font-bold text-red-600">₹{((order.total_monthly_inr as number) || 0).toLocaleString('en-IN')}/mo</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Setup</span><span>₹{((order.total_setup_inr as number) || 0).toLocaleString('en-IN')}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Contract</span><span>{order.contract_months as number} months</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Payment</span><span className="badge-green text-xs">{(order.payment_status as string)?.toUpperCase()}</span></div>
              {Boolean(order.expected_activation_date) && (
                <div className="flex justify-between"><span className="text-slate-500">Est. Activation</span><span>{order.expected_activation_date as string}</span></div>
              )}
            </div>
          </div>

          {/* Products in order */}
          {Boolean(quote?.line_items) && (
            <div className="card-premium p-5">
              <h3 className="font-bold text-slate-900 mb-3">Products</h3>
              <div className="space-y-2">
                {(quote.line_items as Record<string, unknown>[]).map((li) => (
                  <div key={li.product_id as string} className="text-sm flex justify-between items-start">
                    <div className="flex-1 mr-2">
                      <div className="font-medium text-slate-800 text-xs">{li.product_name as string}</div>
                      <div className="text-xs text-slate-400">×{li.quantity as number}</div>
                    </div>
                    <div className="text-xs font-semibold text-slate-700 flex-shrink-0">₹{((li.monthly_cost_inr as number) || 0).toLocaleString('en-IN')}/mo</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Support */}
          <div className="card-premium p-5">
            <h3 className="font-bold text-slate-900 mb-3">Need Help?</h3>
            <div className="space-y-2">
              <a href="tel:1800-103-11" className="flex items-center gap-3 text-sm text-slate-600 hover:text-red-600 transition-colors">
                <Phone className="w-4 h-4" /> 1800-103-11 (Toll-Free)
              </a>
              <a href="#" className="flex items-center gap-3 text-sm text-slate-600 hover:text-red-600 transition-colors">
                <MessageSquare className="w-4 h-4" /> Chat with Support
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TrackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-red-500" /></div>}>
      <TrackContent />
    </Suspense>
  );
}
