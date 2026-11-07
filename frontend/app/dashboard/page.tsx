'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Users, TrendingUp, CheckCircle, Clock, AlertTriangle,
  ChevronRight, RefreshCw, Filter, Search, Award, Activity, BarChart2,
  DollarSign, Shield, Zap, ArrowUpRight, ArrowDownRight, PhoneCall, Building
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area
} from 'recharts';
import { analytics, leads } from '@/lib/api';

const COLORS = ['#e32636', '#2563eb', '#16a34a', '#d97706', '#9333ea', '#0891b2'];

const DEFAULT_OVERVIEW = {
  total_leads: 5000,
  activated: 368,
  lead_to_activation_pct: 7.36,
  avg_activation_days: 17.6,
  avg_cac_inr: 15000,
  avg_monthly_bundle_inr: 6900,
  churn_count: 62,
  churn_rate_pct: 16.8,
  avg_nps: 42.5,
  note: "Derived from Q2 2026 SMB acquisition dataset (5,000 leads)",
};

const DEFAULT_FUNNEL = [
  { stage: "Leads", count: 5000, pct_of_previous: null },
  { stage: "Contacted", count: 3406, pct_of_previous: 68.1 },
  { stage: "Needs Assessed", count: 1974, pct_of_previous: 58.0 },
  { stage: "Quote Accepted", count: 861, pct_of_previous: 43.6 },
  { stage: "KYC Complete", count: 588, pct_of_previous: 68.3 },
  { stage: "Activated", count: 368, pct_of_previous: 62.6 },
];

const DEFAULT_SEGMENTS = [
  { segment: "Micro retail & services", total: 2750, activated: 132, conversion_pct: 4.8, avg_bundle_value_inr: 2499 },
  { segment: "Professional offices", total: 1250, activated: 142, conversion_pct: 11.4, avg_bundle_value_inr: 4999 },
  { segment: "Small multi-site", total: 750, activated: 111, conversion_pct: 14.8, avg_bundle_value_inr: 12800 },
  { segment: "Small manufacturers", total: 250, activated: 21, conversion_pct: 8.2, avg_bundle_value_inr: 18500 },
];

const DEFAULT_DROP_REASONS = [
  { reason: "Competitor chosen", count: 482 },
  { reason: "Quote price mismatch", count: 395 },
  { reason: "Unbundled purchase desire", count: 286 },
  { reason: "KYC documentation delays", count: 273 },
  { reason: "Unreachable / Deferred", count: 210 },
  { reason: "No GSTIN for required product", count: 165 },
  { reason: "Coverage / Serviceability issue", count: 102 },
];

const DEFAULT_SOURCES = [
  { source: "Field sales", total: 1720, activated: 138, conversion_pct: 8.0, avg_cac_inr: 16200 },
  { source: "Channel partner", total: 1010, activated: 82, conversion_pct: 8.1, avg_cac_inr: 12500 },
  { source: "Website form", total: 995, activated: 89, conversion_pct: 8.9, avg_cac_inr: 8400 },
  { source: "Inbound call", total: 504, activated: 35, conversion_pct: 6.9, avg_cac_inr: 11200 },
  { source: "Referral", total: 413, activated: 34, conversion_pct: 8.2, avg_cac_inr: 7800 },
  { source: "WhatsApp campaign", total: 358, activated: 22, conversion_pct: 6.1, avg_cac_inr: 6500 },
];

const DEFAULT_LEADS = [
  { id: "L00142", business_name: "Mehta Eye Clinic & Optics", segment: "Professional offices", city: "Pune", lead_source: "Website form", stage_reached: "Quote accepted", outcome: "Dropped", monthly_telecom_spend_inr: 4800, propensity_score: 86, has_gstin: true, drop_reason: "KYC document friction" },
  { id: "L00289", business_name: "Kalyan Textiles & Silks", segment: "Small multi-site", city: "Bengaluru", lead_source: "Channel partner", stage_reached: "Quote accepted", outcome: "Dropped", monthly_telecom_spend_inr: 11500, propensity_score: 92, has_gstin: true, drop_reason: "Competitor offer matched" },
  { id: "L00311", business_name: "Sharma Agro Tools & Spares", segment: "Small manufacturers", city: "Coimbatore", lead_source: "Field sales", stage_reached: "Needs assessed", outcome: "Dropped", monthly_telecom_spend_inr: 14000, propensity_score: 79, has_gstin: true, drop_reason: "Quote delayed 4 days" },
  { id: "L00488", business_name: "Gupta Departmental Store", segment: "Micro retail & services", city: "Jaipur", lead_source: "WhatsApp campaign", stage_reached: "Contacted", outcome: "Dropped", monthly_telecom_spend_inr: 1200, propensity_score: 64, has_gstin: false, drop_reason: "Price sensitive" },
  { id: "L00523", business_name: "Zenith Digital & Accounting", segment: "Professional offices", city: "Delhi", lead_source: "Referral", stage_reached: "KYC complete", outcome: "Activated", monthly_telecom_spend_inr: 6200, propensity_score: 95, has_gstin: true },
  { id: "L00612", business_name: "Balaji Sweets & Bakery", segment: "Micro retail & services", city: "Chennai", lead_source: "Field sales", stage_reached: "Quote accepted", outcome: "Dropped", monthly_telecom_spend_inr: 2800, propensity_score: 74, has_gstin: true, drop_reason: "Owner unavailable" },
  { id: "L00741", business_name: "Star Diagnostics Centre", segment: "Professional offices", city: "Hyderabad", lead_source: "Inbound call", stage_reached: "Activated", outcome: "Activated", monthly_telecom_spend_inr: 8900, propensity_score: 88, has_gstin: true },
  { id: "L00892", business_name: "Prabhat Engineering Works", segment: "Small manufacturers", city: "Ahmedabad", lead_source: "Channel partner", stage_reached: "KYC complete", outcome: "Activated", monthly_telecom_spend_inr: 16500, propensity_score: 91, has_gstin: true },
];

function StatCard({ label, value, sub, icon: Icon, color }: {
  label: string; value: string | number; sub?: string; icon: any; color: string;
}) {
  return (
    <div className="card-premium p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-400 font-medium uppercase tracking-wide mb-1">{label}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className={`w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${color}`} />
        </div>
      </div>
    </div>
  );
}

interface Lead {
  id: string; business_name: string; segment: string; city: string;
  lead_source: string; stage_reached: string; outcome: string;
  monthly_telecom_spend_inr: number; propensity_score: number; has_gstin: boolean;
  drop_reason?: string;
}

export default function DashboardPage() {
  const [overview, setOverview] = useState<Record<string, unknown>>(DEFAULT_OVERVIEW);
  const [funnel, setFunnel] = useState<Record<string, unknown>[]>(DEFAULT_FUNNEL);
  const [segments, setSegments] = useState<Record<string, unknown>[]>(DEFAULT_SEGMENTS);
  const [sources, setSources] = useState<Record<string, unknown>[]>(DEFAULT_SOURCES);
  const [dropReasons, setDropReasons] = useState<Record<string, unknown>[]>(DEFAULT_DROP_REASONS);
  const [highIntent, setHighIntent] = useState<Lead[]>(DEFAULT_LEADS.filter(l => l.outcome === 'Dropped'));
  const [allLeads, setAllLeads] = useState<Lead[]>(DEFAULT_LEADS);
  const [activeTab, setActiveTab] = useState<'overview'|'leads'|'analytics'|'kyc'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLiveConnected, setIsLiveConnected] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        // Attempt live API fetch
        const res = await fetch('http://localhost:8000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'username=sales%40demo.udyam&password=Demo1234%21',
        }).catch(() => null);

        if (res && res.ok) {
          const data = await res.json();
          if (data.access_token) localStorage.setItem('token', data.access_token);
          setIsLiveConnected(true);

          const [ov, fn, seg, src, dr, hi, al] = await Promise.allSettled([
            analytics.overview(),
            leads.funnel(),
            leads.segments(),
            leads.sources(),
            leads.dropReasons(),
            leads.highIntent(),
            leads.list({ limit: '100' }),
          ]);

          if (ov.status === 'fulfilled' && ov.value) setOverview(ov.value);
          if (fn.status === 'fulfilled' && fn.value?.funnel) setFunnel(fn.value.funnel);
          if (seg.status === 'fulfilled' && Array.isArray(seg.value)) setSegments(seg.value);
          if (src.status === 'fulfilled' && Array.isArray(src.value)) setSources(src.value);
          if (dr.status === 'fulfilled' && Array.isArray(dr.value)) setDropReasons(dr.value);
          if (hi.status === 'fulfilled' && Array.isArray(hi.value)) setHighIntent(hi.value);
          if (al.status === 'fulfilled' && al.value?.leads) setAllLeads(al.value.leads);
        }
      } catch (e) {
        // Fallback to pre-computed benchmark dataset
      }
    };
    init();
  }, []);

  const filteredLeads = allLeads.filter(l =>
    !searchQuery || l.business_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.city?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.segment?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Header */}
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center font-bold text-white text-lg shadow-sm">
            ⚡
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight flex items-center gap-2">
              Accel Business <span className="text-xs text-slate-400 font-normal">· Sales Intelligence Portal</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            <span className={`w-2 h-2 rounded-full ${isLiveConnected ? 'bg-emerald-400 animate-pulse' : 'bg-blue-400'}`} />
            <span>{isLiveConnected ? 'Live API Connected' : 'Dataset Ingested: 5,000 Leads'}</span>
          </div>
          <span className="text-slate-400 hidden sm:inline">Reference: 2026-07-15</span>
          <Link href="/" className="btn-ghost text-xs text-slate-300 hover:text-white py-1">
            ← Customer Portal
          </Link>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-slate-200 px-6">
        <div className="flex gap-2">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart2 },
            { id: 'leads', label: 'Lead Management', icon: Users },
            { id: 'analytics', label: 'Analytics', icon: TrendingUp },
            { id: 'kyc', label: 'KYC & Orders', icon: CheckCircle },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-all cursor-pointer ${
                activeTab === tab.id
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-slate-500 hover:text-slate-900'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* ── OVERVIEW TAB ── */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Top Stat KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Total Leads" value={Number(overview?.total_leads || 5000).toLocaleString()} sub="Q2 2026 Dataset" icon={Users} color="text-red-600" />
              <StatCard label="Activated" value={Number(overview?.activated || 368).toLocaleString()} sub={`${overview?.lead_to_activation_pct || 7.36}% conversion`} icon={CheckCircle} color="text-emerald-600" />
              <StatCard label="Avg. Activation" value={`${overview?.avg_activation_days || 17.6}d`} sub="lead to activation" icon={Clock} color="text-blue-600" />
              <StatCard label="Blended CAC" value={`₹${Number(overview?.avg_cac_inr || 15000).toLocaleString()}`} sub="per activated customer" icon={DollarSign} color="text-purple-600" />
              <StatCard label="Avg Monthly Bundle" value={`₹${Number(overview?.avg_monthly_bundle_inr || 6900).toLocaleString()}`} sub="activated customers" icon={Zap} color="text-amber-600" />
              <StatCard label="Churn Rate (6mo)" value={`${overview?.churn_rate_pct || 16.8}%`} sub={`${overview?.churn_count || 62} customers`} icon={AlertTriangle} color="text-rose-600" />
              <StatCard label="NPS Score" value={String(overview?.avg_nps || 42.5)} sub="net promoter score" icon={Activity} color="text-teal-600" />
              <StatCard label="High-Intent Leads" value={String(highIntent.length || 273)} sub="dropped at quote/KYC" icon={Award} color="text-indigo-600" />
            </div>

            {/* Funnel & Drop Reasons Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-1">Sales Funnel (5,000 Leads)</h2>
                <p className="text-xs text-slate-400 mb-4">Historical progression from lead to activation</p>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={funnel} layout="vertical">
                    <XAxis type="number" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="stage" type="category" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v: any) => [Number(v || 0).toLocaleString('en-IN'), 'Leads']} />
                    <Bar dataKey="count" fill="#e32636" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-1">Drop-off Reasons</h2>
                <p className="text-xs text-slate-400 mb-4">Where prospects stall in the legacy process</p>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={dropReasons.slice(0, 7)}>
                    <XAxis dataKey="reason" tick={{ fontSize: 9 }} angle={-25} textAnchor="end" height={55} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Segment & Lead Source */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-4">Segment Conversion Performance</h2>
                <div className="space-y-3">
                  {segments.map((seg: any) => (
                    <div key={seg.segment}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium text-slate-700">{seg.segment}</span>
                        <span className="text-slate-500">{seg.activated} / {seg.total} ({seg.conversion_pct}%)</span>
                      </div>
                      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-red-500 rounded-full transition-all" style={{ width: `${Math.min(100, seg.conversion_pct * 4)}%` }} />
                      </div>
                      {seg.avg_bundle_value_inr && (
                        <div className="text-xs text-slate-400 mt-0.5">Avg bundle: ₹{Number(seg.avg_bundle_value_inr).toLocaleString('en-IN')}/mo</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-4">Acquisition Channel Efficiency</h2>
                <div className="space-y-3">
                  {sources.map((src: any) => (
                    <div key={src.source}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium text-slate-700">{src.source}</span>
                        <span className="text-slate-500">CAC: ₹{Number(src.avg_cac_inr || 15000).toLocaleString()} ({src.conversion_pct}%)</span>
                      </div>
                      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${Math.min(100, src.conversion_pct * 7)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── LEADS MANAGEMENT TAB ── */}
        {activeTab === 'leads' && (
          <div className="space-y-6">
            <div className="card-premium p-4 flex flex-col sm:flex-row gap-3 items-center justify-between">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Search businesses, city, segment..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-red-500"
                />
              </div>
              <div className="text-xs text-slate-500 font-medium">
                Showing {filteredLeads.length} prioritized leads from dataset
              </div>
            </div>

            <div className="card-premium overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold border-b border-slate-100">
                    <tr>
                      <th className="px-5 py-3.5">Lead / Business</th>
                      <th className="px-4 py-3.5">Segment</th>
                      <th className="px-4 py-3.5">City</th>
                      <th className="px-4 py-3.5">Stage</th>
                      <th className="px-4 py-3.5">Propensity Score</th>
                      <th className="px-4 py-3.5">Est. Spend</th>
                      <th className="px-4 py-3.5">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredLeads.map(l => (
                      <tr key={l.id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="px-5 py-3.5 font-medium text-slate-900">
                          <div>{l.business_name}</div>
                          <div className="text-xs text-slate-400">{l.id} · {l.lead_source}</div>
                        </td>
                        <td className="px-4 py-3.5 text-xs text-slate-600">{l.segment}</td>
                        <td className="px-4 py-3.5 text-xs text-slate-600">{l.city}</td>
                        <td className="px-4 py-3.5">
                          <span className={`badge text-xs ${
                            l.outcome === 'Activated' ? 'badge-green' :
                            l.stage_reached === 'Quote accepted' ? 'badge-yellow' : 'badge-gray'
                          }`}>
                            {l.stage_reached}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="flex items-center gap-2">
                            <span className={`font-bold text-xs ${
                              l.propensity_score >= 80 ? 'text-emerald-600' :
                              l.propensity_score >= 60 ? 'text-blue-600' : 'text-slate-500'
                            }`}>
                              {l.propensity_score}/100
                            </span>
                            <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className={`h-full rounded-full ${
                                l.propensity_score >= 80 ? 'bg-emerald-500' : 'bg-blue-500'
                              }`} style={{ width: `${l.propensity_score}%` }} />
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3.5 text-xs font-semibold text-slate-700">
                          ₹{Number(l.monthly_telecom_spend_inr || 0).toLocaleString()}/mo
                        </td>
                        <td className="px-4 py-3.5">
                          <button
                            onClick={() => alert(`Follow-up recommendation generated for ${l.business_name}: Call contact to review quote discount and assist digital KYC upload.`)}
                            className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1"
                          >
                            <PhoneCall className="w-3 h-3" /> Intervene
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ── ANALYTICS TAB ── */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-4">Activation Share by Segment</h2>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={segments} dataKey="activated" nameKey="segment" cx="50%" cy="50%" outerRadius={85} label={(entry: any) => `${(entry?.segment||'').slice(0,10)} (${entry?.conversion_pct}%)`} labelLine={false}>
                      {segments.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v: any) => [v, 'Activated']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="card-premium p-6">
                <h2 className="font-bold text-slate-900 mb-4">The GSTIN Conversion Dividend</h2>
                <div className="grid grid-cols-2 gap-4 text-center my-6">
                  <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-xl">
                    <div className="text-3xl font-extrabold text-emerald-600">9.6%</div>
                    <div className="text-xs font-bold text-slate-700 mt-1">With GSTIN</div>
                    <div className="text-xs text-slate-400">Higher bundle adoption</div>
                  </div>
                  <div className="p-4 bg-rose-50 border border-rose-100 rounded-xl">
                    <div className="text-3xl font-extrabold text-rose-500">2.0%</div>
                    <div className="text-xs font-bold text-slate-700 mt-1">Without GSTIN</div>
                    <div className="text-xs text-slate-400">4.8× conversion gap</div>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Historical analysis proves that GST-registered businesses convert at nearly 5× the rate of unregistered enterprises. Udyam Digital actively prompts unregistered businesses to file for GSTIN or recommends zero-GST bundles (5G AirFiber + POS).
                </p>
              </div>
            </div>

            {/* Business Targets */}
            <div className="card-premium p-6">
              <h2 className="font-bold text-slate-900 mb-1">Proposed Improvement Targets</h2>
              <p className="text-xs text-slate-400 mb-4">Based on Q2 2026 baseline · Clearly marked as proposals</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { label: 'Lead-to-Activation', current: '7.4%', target: '20.0%', reason: 'Instant quote & zero-touch KYC' },
                  { label: 'Activation Cycle', current: '17.6 days', target: '<4.0 days', reason: 'Digital verification & auto dispatch' },
                  { label: 'Blended CAC', current: '₹15,000', target: '<₹5,500', reason: 'Automated digital onboarding' },
                  { label: 'Quote Acceptance', current: '44%', target: '65%', reason: 'Personalized bundles reduce mismatch' },
                  { label: '6-Mo Churn Rate', current: '16.8%', target: '<7.0%', reason: 'Multi-product bundles increase stickiness' },
                  { label: 'Follow-up Calls', current: '3.0 calls', target: '<0.5 calls', reason: '7-stage real-time tracking stepper' },
                ].map(t => (
                  <div key={t.label} className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
                    <div className="text-xs font-bold text-slate-500 uppercase">{t.label}</div>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-lg text-slate-400 line-through">{t.current}</span>
                      <span className="text-xl font-bold text-emerald-600">{t.target}</span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{t.reason}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── KYC & ORDERS TAB ── */}
        {activeTab === 'kyc' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="card-premium p-5 flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center"><CheckCircle className="w-6 h-6 text-blue-600" /></div>
                <div><div className="text-2xl font-bold text-slate-900">588</div><div className="text-sm text-slate-500">KYC Completed</div><div className="text-xs text-slate-400">68% of quote-accepted</div></div>
              </div>
              <div className="card-premium p-5 flex items-center gap-4">
                <div className="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center"><AlertTriangle className="w-6 h-6 text-amber-600" /></div>
                <div><div className="text-2xl font-bold text-slate-900">273</div><div className="text-sm text-slate-500">KYC Abandoned</div><div className="text-xs text-slate-400">32% drop-off at KYC stage</div></div>
              </div>
              <div className="card-premium p-5 flex items-center gap-4">
                <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center"><Activity className="w-6 h-6 text-emerald-600" /></div>
                <div><div className="text-2xl font-bold text-slate-900">368</div><div className="text-sm text-slate-500">Activated Orders</div><div className="text-xs text-slate-400">63% of KYC-complete</div></div>
              </div>
            </div>

            <div className="card-premium p-6">
              <h2 className="font-bold text-slate-900 mb-4">KYC Drop-off Root Cause Analysis</h2>
              <div className="space-y-4">
                {[
                  { reason: 'Missing Documents (e.g. Udyam cert missing)', count: 89, pct: 32.6 },
                  { reason: 'Address Proof Expiration (>90 days old)', count: 67, pct: 24.5 },
                  { reason: 'GSTIN Legal Name vs Trade Name Mismatch', count: 54, pct: 19.8 },
                  { reason: 'Unreadable Document / Poor Camera Quality', count: 38, pct: 13.9 },
                  { reason: 'Customer Abandoned Before Completion', count: 25, pct: 9.2 },
                ].map(item => (
                  <div key={item.reason}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-slate-700">{item.reason}</span>
                      <span className="text-slate-500">{item.count} cases ({item.pct}%)</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-400 rounded-full" style={{ width: `${item.pct}%` }} />
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-4">Analysis based on the 273 dropped KYC records in the Q2 2026 dataset.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
