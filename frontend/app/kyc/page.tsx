'use client';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Upload, CheckCircle, XCircle, AlertTriangle, Clock, FileText, Shield, Eye, X, Loader2 } from 'lucide-react';
import { kyc, auth } from '@/lib/api';

const DOC_TYPES = [
  { key: 'gst_certificate', label: 'GST Certificate', desc: 'Certificate of GST registration', required: true },
  { key: 'udyam_certificate', label: 'Udyam Certificate', desc: 'MSME Udyam registration certificate', required: false },
  { key: 'signatory_id', label: 'Authorised Signatory ID', desc: "Owner/director's government ID", required: true },
  { key: 'address_proof', label: 'Address Proof', desc: 'Electricity bill/bank statement (max 90 days old)', required: true },
];

const STATUS_ICONS: Record<string, React.ReactNode> = {
  verified: <CheckCircle className="w-4 h-4 text-emerald-500" />,
  needs_review: <AlertTriangle className="w-4 h-4 text-amber-500" />,
  failed: <XCircle className="w-4 h-4 text-red-500" />,
  pending: <Clock className="w-4 h-4 text-slate-400" />,
};

const STATUS_BADGE: Record<string, string> = {
  verified: 'badge-green',
  needs_review: 'badge-yellow',
  failed: 'badge-red',
  pending: 'badge-gray',
  success: 'badge-green',
  partial: 'badge-yellow',
  not_available: 'badge-gray',
};

function KYCContent() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get('order_id') || localStorage.getItem('last_order_id') || '';

  const [consentGiven, setConsentGiven] = useState(false);
  const [submissionId, setSubmissionId] = useState<string | null>(null);
  const [docs, setDocs] = useState<Record<string, Record<string, unknown>>>({});
  const [uploading, setUploading] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [overallResult, setOverallResult] = useState<string | null>(null);
  const [crossChecks, setCrossChecks] = useState<Record<string, Record<string, string>>>({});
  const [error, setError] = useState('');
  const [consentLoading, setConsentLoading] = useState(false);

  const ensureAuth = async () => {
    if (!localStorage.getItem('token')) {
      const res = await auth.demoLogin();
      localStorage.setItem('token', res.access_token);
    }
  };

  const handleConsent = async () => {
    if (!orderId) { setError('No order found. Please complete checkout first.'); return; }
    setConsentLoading(true);
    try {
      await ensureAuth();
      const res = await kyc.consent({ order_id: orderId, consented: true });
      setSubmissionId(res.submission_id);
      setConsentGiven(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setConsentLoading(false);
    }
  };

  const handleUpload = async (docType: string, file: File) => {
    if (!submissionId) return;
    setUploading(docType);
    setError('');
    try {
      const fd = new FormData();
      fd.append('submission_id', submissionId);
      fd.append('doc_type', docType);
      fd.append('file', file);
      const res = await kyc.upload(fd);
      setDocs(prev => ({ ...prev, [docType]: res }));
    } catch (e) {
      setError(`Upload failed: ${(e as Error).message}`);
    } finally {
      setUploading(null);
    }
  };

  const runVerification = async () => {
    if (!submissionId) return;
    setVerifying(true);
    try {
      const res = await kyc.verify(submissionId);
      setOverallResult(res.overall_result);
      setCrossChecks(res.cross_check_results || {});
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setVerifying(false);
    }
  };

  const uploadedCount = Object.keys(docs).length;
  const canVerify = uploadedCount >= 2 && !overallResult;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="section flex items-center h-16 gap-3">
          <Link href="/checkout" className="btn-ghost p-2"><ArrowLeft className="w-4 h-4" /></Link>
          <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 text-sm">Smart KYC Verification</h1>
            <p className="text-xs text-slate-400">DPDP Act 2023 compliant · Documents processed securely</p>
          </div>
        </div>
      </div>

      <div className="section py-8 max-w-4xl">
        {error && (
          <div className="bg-red-50 border border-red-100 text-red-700 text-sm px-4 py-3 rounded-xl mb-4 flex items-start gap-2">
            <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />{error}
          </div>
        )}

        {/* CONSENT */}
        {!consentGiven && (
          <div className="card-premium p-8 max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <Eye className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="font-bold text-slate-900">KYC Consent Notice</h2>
                <p className="text-sm text-slate-500">Please read carefully before proceeding</p>
              </div>
            </div>
            <div className="space-y-3 mb-6">
              {[
                { title: 'What we collect', desc: 'GST Certificate, Udyam Registration, Authorised Signatory ID, Address Proof' },
                { title: 'Why we collect it', desc: 'Regulatory requirement for business telecom service activation in India' },
                { title: 'How it\'s processed', desc: 'OCR extraction + matching against mock government registries (GSTIN, Udyam)' },
                { title: 'Retention', desc: 'Documents retained for 90 days post-activation, then permanently deleted' },
                { title: 'DPDP Act 2023', desc: 'Processed under principles of purpose limitation, data minimisation and consent' },
                { title: 'Withdrawal', desc: 'Contact dpo@accel.business to withdraw consent at any time' },
              ].map(item => (
                <div key={item.title} className="bg-slate-50 rounded-xl p-3">
                  <div className="text-sm font-semibold text-slate-800 mb-0.5">{item.title}</div>
                  <div className="text-xs text-slate-500">{item.desc}</div>
                </div>
              ))}
            </div>
            <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 mb-6 text-xs text-amber-800">
              <strong>Demo Notice:</strong> This is a simulated KYC system for the hackathon. No real government APIs are called. Documents are processed only within this application.
            </div>
            <button onClick={handleConsent} disabled={consentLoading} className="btn-primary w-full">
              {consentLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</> : 'I Consent — Proceed with KYC'}
            </button>
          </div>
        )}

        {/* UPLOAD */}
        {consentGiven && !overallResult && (
          <div className="space-y-6">
            <div>
              <h2 className="font-bold text-slate-900 text-xl mb-1">Upload Your Documents</h2>
              <p className="text-slate-500 text-sm">{uploadedCount} of {DOC_TYPES.length} documents uploaded · {DOC_TYPES.filter(d => d.required).length} required</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {DOC_TYPES.map(dt => {
                const doc = docs[dt.key];
                const isUploading = uploading === dt.key;
                const status = doc?.verification_status as string;

                return (
                  <div key={dt.key} className={`bg-white rounded-2xl border-2 p-5 transition-all ${doc ? 'border-emerald-200' : 'border-slate-200 border-dashed hover:border-red-300'}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-sm text-slate-900">{dt.label}</h3>
                          {dt.required && <span className="badge-red text-xs">Required</span>}
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">{dt.desc}</p>
                      </div>
                      {doc && STATUS_ICONS[status]}
                    </div>

                    {doc ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className={`badge ${STATUS_BADGE[status] || 'badge-gray'} text-xs`}>
                            {status?.replace(/_/g, ' ')}
                          </span>
                          <span className={`badge text-xs ${STATUS_BADGE[(doc.ocr_status as string)] || 'badge-gray'}`}>
                            OCR: {doc.ocr_status as string}
                          </span>
                        </div>
                        {Boolean(doc.verification_notes) && (
                          <p className="text-xs text-slate-500 bg-slate-50 rounded-lg px-3 py-2 leading-relaxed">{doc.verification_notes as string}</p>
                        )}
                        {/* Extracted fields */}
                        {Boolean(doc.extracted_fields && Object.keys(doc.extracted_fields as object).length > 0) && (
                          <div className="bg-blue-50 rounded-lg px-3 py-2">
                            <p className="text-xs font-medium text-blue-700 mb-1">Extracted Fields (masked):</p>
                            {Object.entries(doc.extracted_fields as Record<string, string>).map(([k, v]) => (
                              <div key={k} className="text-xs text-blue-600"><span className="font-medium">{k}:</span> {v}</div>
                            ))}
                          </div>
                        )}
                        {/* Registry result */}
                        {Boolean(doc.registry_result && (doc.registry_result as Record<string, string>).status) && (
                          <div className={`text-xs rounded-lg px-3 py-2 ${(doc.registry_result as Record<string, string>).status === 'found' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                            Registry: {(doc.registry_result as Record<string, string>).message}
                          </div>
                        )}
                      </div>
                    ) : (
                      <label className="flex flex-col items-center justify-center gap-2 cursor-pointer py-4">
                        {isUploading ? (
                          <><Loader2 className="w-8 h-8 text-red-400 animate-spin" /><span className="text-sm text-slate-500">Processing...</span></>
                        ) : (
                          <><Upload className="w-8 h-8 text-slate-300" /><span className="text-sm text-slate-400">Click to upload</span><span className="text-xs text-slate-300">JPG, PNG up to 10 MB</span></>
                        )}
                        <input type="file" className="hidden" accept="image/*,.pdf" disabled={isUploading}
                          onChange={e => e.target.files?.[0] && handleUpload(dt.key, e.target.files[0])} />
                      </label>
                    )}
                  </div>
                );
              })}
            </div>

            {canVerify && (
              <div className="text-center">
                <button onClick={runVerification} disabled={verifying} className="btn-primary px-10 py-4 text-base">
                  {verifying ? <><Loader2 className="w-5 h-5 animate-spin" /> Running Verification...</> : <><Shield className="w-5 h-5" /> Run Full Verification</>}
                </button>
              </div>
            )}
          </div>
        )}

        {/* RESULT */}
        {overallResult && (
          <div className="space-y-6">
            <div className={`rounded-2xl p-6 border-2 ${overallResult === 'verified' ? 'bg-emerald-50 border-emerald-200' : overallResult === 'needs_review' ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200'}`}>
              <div className="flex items-center gap-3 mb-3">
                {overallResult === 'verified' ? <CheckCircle className="w-8 h-8 text-emerald-600" /> : overallResult === 'needs_review' ? <AlertTriangle className="w-8 h-8 text-amber-600" /> : <XCircle className="w-8 h-8 text-red-600" />}
                <div>
                  <h2 className="font-bold text-slate-900 text-xl">KYC {overallResult === 'verified' ? 'Verified ✓' : overallResult === 'needs_review' ? 'Under Review' : 'Failed'}</h2>
                  <p className="text-sm text-slate-600">{overallResult === 'verified' ? 'All documents verified successfully.' : overallResult === 'needs_review' ? 'Some documents need manual review. Our team will contact you.' : 'Verification failed. Please re-upload clearer documents.'}</p>
                </div>
              </div>

              {/* Cross-checks */}
              {Object.keys(crossChecks).length > 0 && (
                <div className="space-y-2 mb-4">
                  <p className="text-sm font-semibold text-slate-700">Cross-document Checks:</p>
                  {Object.entries(crossChecks).map(([check, result]) => (
                    <div key={check} className={`flex items-start gap-2 text-sm rounded-lg px-3 py-2 ${(result as Record<string, string>).status === 'pass' ? 'bg-emerald-100 text-emerald-800' : (result as Record<string, string>).status === 'warning' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}>
                      {(result as Record<string, string>).status === 'pass' ? <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /> : <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                      <span>{(result as Record<string, string>).message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Link href={`/track?order_id=${orderId}`} className="btn-primary flex-1 text-center">
                Track My Order →
              </Link>
              {overallResult !== 'verified' && (
                <button onClick={() => { setOverallResult(null); setCrossChecks({}); setDocs({}); }} className="btn-secondary flex-1">
                  Re-upload Documents
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function KYCPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-red-500" /></div>}>
      <KYCContent />
    </Suspense>
  );
}
