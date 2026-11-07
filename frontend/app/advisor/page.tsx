'use client';
import { useState, useEffect, useRef, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Send, ArrowLeft, Bot, User, Loader2, Zap, ArrowRight, CheckCircle, ShoppingBag, Stethoscope, Building2 } from 'lucide-react';
import { auth, advisor, recommendations } from '@/lib/api';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

const PERSONA_ICONS: Record<string, React.ReactNode> = {
  kirana: <ShoppingBag className="w-5 h-5" />,
  clinic: <Stethoscope className="w-5 h-5" />,
  multi_retail: <Building2 className="w-5 h-5" />,
};

function AdvisorContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const persona = searchParams.get('persona') || undefined;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [convId, setConvId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [isComplete, setIsComplete] = useState(false);
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [recommendation, setRecommendation] = useState<Record<string, unknown> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Ensure we have a demo token
  const ensureAuth = async () => {
    if (!localStorage.getItem('token')) {
      const res = await auth.demoLogin();
      localStorage.setItem('token', res.access_token);
      localStorage.setItem('user', JSON.stringify(res.user));
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        await ensureAuth();
        const res = await advisor.start(persona);
        setConvId(res.conversation_id);
        setMessages([{ role: 'assistant', content: res.message }]);
        if (res.state?.completed) {
          setIsComplete(true);
          setProfile(res.state.profile);
        }
      } catch (e) {
        setMessages([{ role: 'assistant', content: 'Welcome! Tell me about your business and I will find the right bundle for you.' }]);
      } finally {
        setInitializing(false);
      }
    };
    init();
  }, [persona]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading || !convId) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(m => [...m, { role: 'user', content: userMsg }]);
    setLoading(true);
    try {
      const res = await advisor.message(convId, userMsg);
      setMessages(m => [...m, { role: 'assistant', content: res.message }]);
      if (res.is_complete) {
        setIsComplete(true);
        setProfile(res.profile);
      }
    } catch {
      setMessages(m => [...m, { role: 'assistant', content: 'I encountered an issue. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendation = async () => {
    if (!convId) return;
    setRecLoading(true);
    try {
      const conv = await advisor.conversation(convId);
      const rec = await recommendations.generate({ conversation_id: convId, profile: conv.profile });
      setRecommendation(rec);
      localStorage.setItem('last_recommendation', JSON.stringify(rec));
      localStorage.setItem('last_conversation_id', convId);
      localStorage.setItem('last_profile', JSON.stringify(conv.profile));
    } catch (e) {
      alert('Could not generate recommendation: ' + (e as Error).message);
    } finally {
      setRecLoading(false);
    }
  };

  const goToBundle = () => {
    router.push('/bundle');
  };

  const formatMsg = (content: string) =>
    content.split('\n').map((line, i) => {
      const bold = line.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      return <p key={i} dangerouslySetInnerHTML={{ __html: bold }} className={i > 0 ? 'mt-1.5' : ''} />;
    });

  if (initializing) {
    return (
      <div className="min-h-screen hero-gradient flex items-center justify-center">
        <div className="text-center text-white">
          <Loader2 className="w-10 h-10 animate-spin mx-auto mb-4 opacity-60" />
          <p className="text-white/60">Starting your advisor session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 px-4 py-3 flex items-center gap-3 sticky top-0 z-40">
        <Link href="/" className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></Link>
        <div className="w-9 h-9 bg-red-600 rounded-xl flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="font-semibold text-slate-900 text-sm">Accel Business Advisor</div>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-slate-500">AI-Powered · Always Available</span>
          </div>
        </div>
        {isComplete && (
          <div className="ml-auto">
            <span className="badge-green">
              <CheckCircle className="w-3.5 h-3.5" /> Profile Complete
            </span>
          </div>
        )}
      </div>

      {/* Persona quick-selects */}
      {!persona && messages.length <= 1 && (
        <div className="section-sm px-4 pt-4">
          <p className="text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">Quick Start — Select a Demo Persona</p>
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'kirana', label: '🛒 Kirana Store', sub: 'Price-sensitive, Tier 2' },
              { key: 'clinic', label: '🏥 Clinic / Office', sub: 'Professional, GSTIN' },
              { key: 'multi_retail', label: '🏪 Multi-location', sub: '5 stores, 40 staff' },
            ].map(p => (
              <a key={p.key} href={`/advisor?persona=${p.key}`}
                className="flex items-center gap-2 px-3.5 py-2 bg-white border border-slate-200 hover:border-red-300 hover:bg-red-50 rounded-xl text-sm font-medium text-slate-700 transition-all">
                {p.label}
                <span className="text-slate-400 text-xs hidden sm:inline">· {p.sub}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full">
        <div className="space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex items-end gap-2 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-7 h-7 bg-red-600 rounded-full flex items-center justify-center flex-shrink-0 mb-1">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </div>
              )}
              <div className={m.role === 'assistant' ? 'chat-bubble-assistant' : 'chat-bubble-user'}>
                {formatMsg(m.content)}
              </div>
              {m.role === 'user' && (
                <div className="w-7 h-7 bg-slate-200 rounded-full flex items-center justify-center flex-shrink-0 mb-1">
                  <User className="w-3.5 h-3.5 text-slate-500" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-end gap-2">
              <div className="w-7 h-7 bg-red-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="chat-bubble-assistant">
                <div className="flex gap-1 items-center">
                  <div className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Recommendation Panel (when complete) */}
      {isComplete && !recommendation && (
        <div className="max-w-3xl mx-auto w-full px-4 pb-4">
          <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-100 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <span className="font-semibold text-slate-900">Business profile complete!</span>
            </div>
            <p className="text-sm text-slate-600 mb-4">Your business details have been captured. Click below to generate your personalised product bundle.</p>
            <button onClick={getRecommendation} disabled={recLoading}
              className="btn-primary w-full sm:w-auto">
              {recLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Zap className="w-4 h-4" /> View My Bundle Recommendation</>}
            </button>
          </div>
        </div>
      )}

      {recommendation && (
        <div className="max-w-3xl mx-auto w-full px-4 pb-4">
          <div className="bg-white border border-emerald-200 rounded-2xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                <span className="font-semibold text-slate-900">Recommendation Ready!</span>
              </div>
              <div className="text-right">
                <div className="text-xl font-bold text-red-600">₹{((recommendation.total_monthly_inr as number) || 0).toLocaleString('en-IN')}/mo</div>
                <div className="text-xs text-slate-500">{(recommendation.primary_bundle as unknown[])?.length || 0} products · +₹{((recommendation.total_setup_inr as number) || 0).toLocaleString('en-IN')} setup</div>
              </div>
            </div>
            <p className="text-sm text-slate-600 mb-4 line-clamp-2">{recommendation.explanation as string}</p>
            <button onClick={goToBundle} className="btn-primary w-full">
              Customise & Build Bundle <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Input */}
      {!isComplete && (
        <div className="bg-white border-t border-slate-100 p-4">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              className="input flex-1"
              placeholder="Type your answer..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}
              className="w-12 h-12 bg-red-600 hover:bg-red-700 disabled:opacity-40 text-white rounded-xl flex items-center justify-center transition-colors flex-shrink-0">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
          <p className="text-center text-xs text-slate-400 mt-2">Deterministic AI advisor · No external API required</p>
        </div>
      )}
    </div>
  );
}

export default function AdvisorPage() {
  return (
    <Suspense fallback={<div className="min-h-screen hero-gradient flex items-center justify-center"><Loader2 className="w-10 h-10 animate-spin text-white/40" /></div>}>
      <AdvisorContent />
    </Suspense>
  );
}
