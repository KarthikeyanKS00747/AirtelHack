'use client';
import Link from 'next/link';
import { useState } from 'react';
import {
  Wifi, Smartphone, Shield, Cloud, BarChart3, CheckCircle, ArrowRight,
  Zap, Clock, TrendingUp, Users, Globe, Lock, ChevronRight, Star,
  Building2, Stethoscope, ShoppingBag, Factory, MessageCircle
} from 'lucide-react';

const STATS = [
  { value: '17.6 days', label: 'Avg. Activation Time', sub: 'vs industry 30+ days' },
  { value: '₹15,000', label: 'Blended CAC', sub: 'competitive acquisition cost' },
  { value: '5,000+', label: 'MSMEs Served', sub: 'across 2 quarters' },
  { value: '3.0', label: 'Avg. Follow-ups', sub: 'reduced from 8+ manual calls' },
];

const CATEGORIES = [
  { icon: Wifi, name: 'Connectivity', desc: 'Fibre, 5G AirFiber, Leased Lines', color: 'text-blue-600', bg: 'bg-blue-50' },
  { icon: Smartphone, name: 'Business Mobile', desc: 'Postpaid plans for your team', color: 'text-purple-600', bg: 'bg-purple-50' },
  { icon: MessageCircle, name: 'Communication', desc: 'Cloud telephony, WhatsApp, SMS', color: 'text-green-600', bg: 'bg-green-50' },
  { icon: Cloud, name: 'Cloud & Productivity', desc: 'Email, backup, POS, website', color: 'text-cyan-600', bg: 'bg-cyan-50' },
  { icon: Shield, name: 'Security', desc: 'Firewall, Wi-Fi, endpoint protection', color: 'text-orange-600', bg: 'bg-orange-50' },
  { icon: Globe, name: 'IoT & Physical', desc: 'CCTV, fleet tracker, machine IoT', color: 'text-red-600', bg: 'bg-red-50' },
];

const STEPS = [
  { num: '01', title: 'Describe Your Business', desc: 'Chat with our AI advisor. Tell us about your business type, size, location and needs in plain language.' },
  { num: '02', title: 'Get Personalised Bundle', desc: 'We match you with the right products from our catalogue — transparent pricing, no hidden costs.' },
  { num: '03', title: 'Customise & Quote', desc: 'Add or remove products, adjust quantities. Generate a formal quote in seconds.' },
  { num: '04', title: 'Go Digital Today', desc: 'Complete KYC digitally, confirm your order and track installation in real time.' },
];

const SEGMENTS = [
  { icon: ShoppingBag, name: 'Kirana & Retail', desc: 'Fast internet, UPI-ready POS and CCTV for your shop', color: 'text-orange-600', bg: 'bg-orange-50' },
  { icon: Stethoscope, name: 'Clinics & Professionals', desc: 'Reliable connectivity, email and toll-free for your practice', color: 'text-blue-600', bg: 'bg-blue-50' },
  { icon: Building2, name: 'Multi-site Businesses', desc: 'SD-WAN, unified billing and central management across all locations', color: 'text-purple-600', bg: 'bg-purple-50' },
  { icon: Factory, name: 'Manufacturers', desc: 'Leased lines, machine IoT monitoring and fleet tracking', color: 'text-green-600', bg: 'bg-green-50' },
];

export default function Home() {
  const [isMenuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {/* NAVBAR */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur border-b border-slate-100">
        <div className="section flex items-center justify-between h-16">
          <div className="flex items-center gap-1">
            <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-900 ml-1">Accel <span className="text-red-600">Business</span></span>
          </div>
          <div className="hidden md:flex items-center gap-6">
            <Link href="/products" className="text-sm text-slate-600 hover:text-red-600 transition-colors font-medium">Products</Link>
            <Link href="/advisor" className="text-sm text-slate-600 hover:text-red-600 transition-colors font-medium">Get a Quote</Link>
            <Link href="/dashboard" className="text-sm text-slate-600 hover:text-red-600 transition-colors font-medium">Partner Portal</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="hidden md:block btn-ghost text-sm">Sign In</Link>
            <Link href="/advisor" className="btn-primary text-sm py-2.5 px-5">
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero-gradient pt-28 pb-20 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 right-20 w-96 h-96 rounded-full opacity-5" style={{ background: '#e32636', filter: 'blur(80px)' }} />
          <div className="absolute bottom-0 left-20 w-64 h-64 rounded-full opacity-5" style={{ background: '#4f46e5', filter: 'blur(60px)' }} />
        </div>

        <div className="section relative">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-2 mb-6">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-white/80 text-sm font-medium">Airtel SYNC Hackathon 2026 — Track A</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Make Your Business<br />
              <span className="gradient-text">Go Digital</span><br />
              in One Sitting.
            </h1>

            <p className="text-white/70 text-lg sm:text-xl leading-relaxed mb-8 max-w-2xl">
              Get personalised connectivity, cloud and security bundles for your MSME — with AI advice, digital KYC and same-day activation. No more 3–5 day quotes or marathon phone calls.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Link href="/advisor" className="btn-primary text-base px-8 py-4">
                Talk to AI Advisor <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/products" className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl border border-white/20 transition-all duration-200">
                View Products
              </Link>
            </div>

            {/* Quick persona buttons */}
            <div className="flex flex-wrap gap-2">
              <span className="text-white/50 text-sm self-center">Quick start:</span>
              {[
                { key: 'kirana', label: '🛒 Kirana Store', href: '/advisor?persona=kirana' },
                { key: 'clinic', label: '🏥 Clinic / Office', href: '/advisor?persona=clinic' },
                { key: 'multi_retail', label: '🏪 Multi-location', href: '/advisor?persona=multi_retail' },
              ].map(p => (
                <Link key={p.key} href={p.href}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white text-sm rounded-full transition-all duration-200 font-medium">
                  {p.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* STATS BAND */}
      <section className="bg-slate-900 py-10">
        <div className="section grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map(s => (
            <div key={s.label} className="text-center">
              <div className="text-2xl sm:text-3xl font-bold text-white mb-1">{s.value}</div>
              <div className="text-sm font-medium text-white/80">{s.label}</div>
              <div className="text-xs text-white/40 mt-0.5">{s.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* PRODUCT CATEGORIES */}
      <section className="py-20 bg-white">
        <div className="section">
          <div className="text-center mb-12">
            <div className="accent-line mx-auto mb-4" />
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Everything Your Business Needs</h2>
            <p className="text-slate-500 max-w-2xl mx-auto">25 products across 5 categories, bundled intelligently for your business type and size.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {CATEGORIES.map(cat => (
              <div key={cat.name} className="card p-6 group cursor-pointer">
                <div className={`w-12 h-12 ${cat.bg} rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform`}>
                  <cat.icon className={`w-6 h-6 ${cat.color}`} />
                </div>
                <h3 className="font-semibold text-slate-900 mb-1.5">{cat.name}</h3>
                <p className="text-sm text-slate-500">{cat.desc}</p>
                <div className="flex items-center gap-1 mt-3 text-red-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  Explore <ChevronRight className="w-3 h-3" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-20 bg-slate-50">
        <div className="section">
          <div className="text-center mb-14">
            <div className="accent-line mx-auto mb-4" />
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">From Curious to Connected in Minutes</h2>
            <p className="text-slate-500 max-w-xl mx-auto">A completely digital onboarding — no paperwork, no waiting, no confusion.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map((step, i) => (
              <div key={step.num} className="relative">
                {i < STEPS.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-full w-full h-px bg-slate-200 z-0" style={{ width: 'calc(100% - 48px)', left: '48px' }} />
                )}
                <div className="relative z-10">
                  <div className="text-3xl font-black text-red-100 mb-3">{step.num}</div>
                  <h3 className="font-bold text-slate-900 mb-2">{step.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link href="/advisor" className="btn-primary">
              Start Your Journey <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* SEGMENTS */}
      <section className="py-20 bg-white">
        <div className="section">
          <div className="text-center mb-12">
            <div className="accent-line mx-auto mb-4" />
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Built for Every Kind of Business</h2>
            <p className="text-slate-500">From neighbourhood kirana to multi-city chains — we have the right bundle.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {SEGMENTS.map(seg => (
              <Link key={seg.name} href="/advisor" className="card p-6 group text-left">
                <div className={`w-12 h-12 ${seg.bg} rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform`}>
                  <seg.icon className={`w-6 h-6 ${seg.color}`} />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">{seg.name}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{seg.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* TRUST & SECURITY */}
      <section className="py-16 bg-slate-900">
        <div className="section">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="accent-line mb-4" />
              <h2 className="text-3xl font-bold text-white mb-4">Enterprise-Grade Security.<br />MSME-Friendly Pricing.</h2>
              <p className="text-white/60 mb-6 leading-relaxed">Your data is protected at every step. We follow DPDP Act, 2023 principles — explicit consent, purpose limitation and secure document processing.</p>
              <div className="space-y-3">
                {[
                  'Digital KYC with mock government registry verification',
                  'Role-based access control for your team',
                  'Consent-first document processing',
                  'Masked identifiers in all interfaces',
                  'Audit trail for every verification action',
                ].map(f => (
                  <div key={f} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span className="text-white/80 text-sm">{f}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: Lock, title: 'DPDP Act 2023', desc: 'Compliant data processing' },
                { icon: Shield, title: 'Secure KYC', desc: 'End-to-end document safety' },
                { icon: BarChart3, title: 'Transparent Pricing', desc: 'No hidden costs ever' },
                { icon: Clock, title: 'Fast Activation', desc: 'From days to hours' },
              ].map(item => (
                <div key={item.title} className="bg-white/5 border border-white/10 rounded-2xl p-5">
                  <item.icon className="w-8 h-8 text-red-400 mb-3" />
                  <div className="font-semibold text-white text-sm mb-1">{item.title}</div>
                  <div className="text-white/50 text-xs">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-white">
        <div className="section text-center">
          <div className="max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-red-50 border border-red-100 rounded-full px-4 py-2 mb-6">
              <Star className="w-4 h-4 text-red-600 fill-red-600" />
              <span className="text-red-700 text-sm font-medium">AI-powered, always available</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Ready to Go Digital?</h2>
            <p className="text-slate-500 mb-8">Our AI advisor is available 24/7. Get a personalised bundle recommendation in under 5 minutes — no commitment required.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/advisor" className="btn-primary text-base px-8 py-4">
                Talk to AI Advisor <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/dashboard" className="btn-secondary text-base px-8 py-4">
                Partner / Sales Login
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-slate-950 py-12">
        <div className="section">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-red-600 rounded-lg flex items-center justify-center">
                <Zap className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="text-white/80 font-semibold">Accel Business</span>
            </div>
            <div className="flex gap-6">
              <Link href="/advisor" className="text-white/40 hover:text-white/80 text-sm transition-colors">Get a Quote</Link>
              <Link href="/products" className="text-white/40 hover:text-white/80 text-sm transition-colors">Products</Link>
              <Link href="/dashboard" className="text-white/40 hover:text-white/80 text-sm transition-colors">Partner Portal</Link>
            </div>
            <div className="text-white/30 text-xs">
              Hackathon demo © 2026 — Synthetic data only
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
