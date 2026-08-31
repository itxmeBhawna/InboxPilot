import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Copy,
  Database,
  FileEdit,
  Mail,
  MessageSquare,
  Radio,
  RefreshCw,
  Send,
  ShieldAlert,
  Sparkles,
  User,
  Zap,
} from 'lucide-react';
import type { EmailTriageData } from './types';

const CATEGORIES = [
  'ACTION_REQUIRED',
  'MEETING',
  'APPLICATION',
  'FINANCE',
  'NEWSLETTER',
  'PROMOTION',
  'SPAM_SCAM',
  'PERSONAL',
  'OTHER',
];

const PRIORITIES = ['HIGH', 'MEDIUM', 'LOW'];

export const App: React.FC = () => {
  const [data, setData] = useState<EmailTriageData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Auto-poll and timestamp state
  const [autoPoll, setAutoPoll] = useState<boolean>(false);
  const [lastCheckedTime, setLastCheckedTime] = useState<string>(new Date().toLocaleTimeString());

  // Feedback form state
  const [userPriority, setUserPriority] = useState<string>('HIGH');
  const [userCategory, setUserCategory] = useState<string>('ACTION_REQUIRED');
  const [feedbackNotes, setFeedbackNotes] = useState<string>('');
  const [submittingFeedback, setSubmittingFeedback] = useState<boolean>(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState<boolean>(false);
  const [copiedDraft, setCopiedDraft] = useState<boolean>(false);
  const [showReasoning, setShowReasoning] = useState<boolean>(true);

  const fetchLatestEmail = async () => {
    setLoading(true);
    setError(null);
    setFeedbackSuccess(false);

    try {
      const response = await fetch('/emails/latest');
      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }
      const json: EmailTriageData = await response.json();
      setData(json);
      setLastCheckedTime(new Date().toLocaleTimeString());

      if (json.unread) {
        if (json.priority) setUserPriority(json.priority);
        if (json.category) setUserCategory(json.category);
      }
    } catch (err: any) {
      console.error('Failed to fetch latest email:', err);
      setError(err.message || 'Failed to connect to InboxPilot service');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestEmail();
  }, []);

  useEffect(() => {
    let interval: any;
    if (autoPoll) {
      interval = setInterval(() => {
        fetchLatestEmail();
      }, 15000);
    }
    return () => clearInterval(interval);
  }, [autoPoll]);

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!data || !data.email_id) return;

    setSubmittingFeedback(true);
    setFeedbackSuccess(false);

    try {
      const payload = {
        email_id: data.email_id,
        sender: data.sender || '',
        subject: data.subject || '',
        predicted_priority: data.priority || 'MEDIUM',
        user_priority: userPriority,
        predicted_category: data.category || 'OTHER',
        user_category: userCategory,
        feedback_reason: feedbackNotes.trim() || null,
      };

      const res = await fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Failed to record feedback (${res.status})`);
      }

      setFeedbackSuccess(true);
      setFeedbackNotes('');
    } catch (err: any) {
      alert(`Feedback submission failed: ${err.message}`);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const copyDraftToClipboard = () => {
    if (!data?.draft_reply) return;
    navigator.clipboard.writeText(data.draft_reply);
    setCopiedDraft(true);
    setTimeout(() => setCopiedDraft(false), 2500);
  };

  const getPriorityStyle = (p?: string) => {
    switch (p?.toUpperCase()) {
      case 'HIGH':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30 glow-border-rose';
      case 'MEDIUM':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'LOW':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 glow-border-emerald';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getCategoryStyle = (c?: string) => {
    switch (c?.toUpperCase()) {
      case 'ACTION_REQUIRED':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'APPLICATION':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
      case 'MEETING':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'FINANCE':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'NEWSLETTER':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
      case 'PROMOTION':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'SPAM_SCAM':
        return 'bg-rose-600/20 text-rose-300 border-rose-600/40';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header Navbar */}
      <header className="glass-panel sticky top-0 z-50 border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-violet-500 rounded-xl shadow-lg shadow-indigo-500/20">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                InboxPilot
              </h1>
              <p className="text-xs text-slate-400 font-medium">Autonomous AI Email Triage & Workspace Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Gemini 3.6 Flash Active
            </div>

            <button
              onClick={fetchLatestEmail}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium text-xs rounded-lg transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Analyzing...' : 'Fetch Latest Email'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Error State */}
        {error && (
          <div className="p-4 rounded-xl glass-card border border-rose-500/30 bg-rose-500/10 text-rose-300 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
            <div>
              <h3 className="font-semibold text-sm">Connection Error</h3>
              <p className="text-xs mt-1 text-rose-200">{error}</p>
            </div>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && (
          <div className="glass-panel rounded-2xl p-8 space-y-6 animate-pulse border border-slate-800">
            <div className="flex justify-between items-center">
              <div className="h-6 bg-slate-800 rounded w-1/3"></div>
              <div className="h-6 bg-slate-800 rounded w-24"></div>
            </div>
            <div className="h-10 bg-slate-800 rounded w-3/4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-slate-800 rounded w-full"></div>
              <div className="h-4 bg-slate-800 rounded w-5/6"></div>
              <div className="h-4 bg-slate-800 rounded w-2/3"></div>
            </div>
          </div>
        )}

        {/* Empty Inbox State / Autonomous Monitoring Active */}
        {!loading && data && !data.unread && (
          <div className="glass-panel rounded-2xl p-10 text-center border border-slate-800 space-y-6 max-w-xl mx-auto my-8 glow-border-indigo">
            <div className="relative p-4 bg-indigo-500/10 rounded-full w-20 h-20 mx-auto flex items-center justify-center border border-indigo-500/30">
              <Radio className="w-10 h-10 text-indigo-400 animate-pulse" />
              <span className="absolute top-1 right-1 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-slate-950 animate-ping" />
            </div>

            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Autonomous Monitoring Active
              </div>
              <h2 className="text-xl font-bold text-slate-100 mt-1">No New Unread Emails Found</h2>
              <p className="text-slate-400 text-xs mt-2 leading-relaxed">
                InboxPilot is actively watching your connected Gmail inbox. When a new email arrives, it will automatically triage, classify, sync to Notion, and generate draft replies.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                onClick={() => {
                  fetchLatestEmail();
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Check Now
              </button>

              <button
                onClick={() => setAutoPoll(!autoPoll)}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl border transition cursor-pointer ${
                  autoPoll
                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <Zap className="w-3.5 h-3.5" />
                {autoPoll ? 'Auto-Poll (15s): ON' : 'Auto-Poll: OFF'}
              </button>
            </div>

            <div className="text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-900">
              Last Checked: {lastCheckedTime}
            </div>
          </div>
        )}

        {/* Unread Email Triaged Card */}
        {!loading && data && data.unread && (
          <div className="space-y-6">
            {/* Top Email Header & Badges */}
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`px-3 py-1 rounded-md border text-xs font-semibold uppercase tracking-wider ${getCategoryStyle(data.category)}`}>
                    {data.category}
                  </span>
                  <span className={`px-3 py-1 rounded-md border text-xs font-semibold uppercase tracking-wider ${getPriorityStyle(data.priority)}`}>
                    Priority: {data.priority}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" />
                  {data.received_at ? new Date(data.received_at).toLocaleString() : 'Just now'}
                </div>
              </div>

              {/* Email Title */}
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight leading-snug">
                  {data.subject || '(No Subject)'}
                </h2>
                <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-300">
                  <div className="flex items-center gap-1.5 bg-slate-900/80 px-3 py-1.5 rounded-md border border-slate-800">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-slate-400">From:</span>
                    <span className="font-mono text-slate-200 font-medium">{data.sender}</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-slate-900/80 px-3 py-1.5 rounded-md border border-slate-800">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-slate-400">To:</span>
                    <span className="font-mono text-slate-300">{data.recipient}</span>
                  </div>
                </div>
              </div>

              {/* Integration Status Badges */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
                {/* Spam Score Gauge */}
                <div className="glass-card rounded-xl p-4 border border-slate-800 flex items-center gap-3">
                  <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
                  <div>
                    <div className="text-xs text-slate-400 font-medium">Spam Risk Score</div>
                    <div className="text-sm font-semibold text-slate-100 mt-0.5">
                      {data.spam_score !== undefined ? `${data.spam_score}%` : '0%'}
                    </div>
                  </div>
                </div>

                {/* Notion Sync Status */}
                <div className="glass-card rounded-xl p-4 border border-slate-800 flex items-center gap-3">
                  <Database className={`w-5 h-5 shrink-0 ${data.synced_to_notion ? 'text-emerald-400' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-xs text-slate-400 font-medium">Notion Sync</div>
                    <div className="text-sm font-semibold text-slate-100 mt-0.5 flex items-center gap-1.5">
                      {data.synced_to_notion ? (
                        <>
                          <span className="text-emerald-400">Synced</span>
                          {data.notion_page_id && (
                            <span className="text-[10px] text-slate-500 font-mono">({data.notion_page_id.slice(0, 8)}...)</span>
                          )}
                        </>
                      ) : (
                        <span className="text-slate-400">Not Synced</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Gmail Draft Status */}
                <div className="glass-card rounded-xl p-4 border border-slate-800 flex items-center gap-3">
                  <FileEdit className={`w-5 h-5 shrink-0 ${data.draft_created ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-xs text-slate-400 font-medium">Gmail Draft Status</div>
                    <div className="text-sm font-semibold text-slate-100 mt-0.5">
                      {data.draft_created ? (
                        <span className="text-indigo-400 font-medium">Draft Saved</span>
                      ) : (
                        <span className="text-slate-400">No Draft Required</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Memory Context Badge */}
                <div className="glass-card rounded-xl p-4 border border-slate-800 flex items-center gap-3">
                  <Sparkles className={`w-5 h-5 shrink-0 ${data.preference_context_used ? 'text-purple-400' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-xs text-slate-400 font-medium">Memory Preference</div>
                    <div className="text-sm font-semibold text-slate-100 mt-0.5">
                      {data.preference_context_used ? (
                        <span className="text-purple-400 font-medium">Memory Context Used</span>
                      ) : (
                        <span className="text-slate-400">No Preference History</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Analysis Summary & Reasoning */}
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-5">
              <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
                <Sparkles className="w-4 h-4" />
                AI Triage Summary
              </div>
              <p className="text-slate-200 text-sm leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                {data.summary || 'No summary available.'}
              </p>

              {/* Reasoning Accordion */}
              {data.reasoning && (
                <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/40">
                  <button
                    onClick={() => setShowReasoning(!showReasoning)}
                    className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold text-slate-300 hover:bg-slate-800/50 transition cursor-pointer"
                  >
                    <span className="flex items-center gap-2">
                      <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                      Detailed Classification Reasoning
                    </span>
                    {showReasoning ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  {showReasoning && (
                    <div className="px-4 py-3 border-t border-slate-800/80 text-xs text-slate-300 leading-relaxed font-sans bg-slate-950/40">
                      {data.reasoning}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Draft Reply Preview */}
            {data.draft_reply && (
              <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
                    <Send className="w-4 h-4" />
                    Generated Reply Draft
                  </div>
                  <button
                    onClick={copyDraftToClipboard}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-xs text-slate-300 transition cursor-pointer"
                  >
                    {copiedDraft ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copiedDraft ? 'Copied!' : 'Copy Draft'}
                  </button>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {data.draft_reply}
                </div>
              </div>
            )}

            {/* Feedback Correction Form */}
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-5">
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <FileEdit className="w-4 h-4 text-indigo-400" />
                  Submit Feedback Correction
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Override priority or category predictions to help personalize InboxPilot memory rules.
                </p>
              </div>

              {/* Feedback Success Toast */}
              {feedbackSuccess && (
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-2 animate-pulse">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ✓ Feedback saved to memory repository!
                </div>
              )}

              <form onSubmit={handleFeedbackSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Priority Correction */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">Priority Correction</label>
                    <select
                      value={userPriority}
                      onChange={(e) => setUserPriority(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 cursor-pointer"
                    >
                      {PRIORITIES.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Category Correction */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300">Category Correction</label>
                    <select
                      value={userCategory}
                      onChange={(e) => setUserCategory(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 cursor-pointer"
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Notes Textarea */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Correction Rationale (Optional Notes)</label>
                  <textarea
                    rows={3}
                    value={feedbackNotes}
                    onChange={(e) => setFeedbackNotes(e.target.value)}
                    placeholder="Explain why this priority or category should be adjusted..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 placeholder-slate-500 resize-none"
                  />
                </div>

                {/* Submit Button */}
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={submittingFeedback}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 active:from-indigo-700 active:to-violet-700 text-white font-semibold text-xs rounded-xl transition shadow-md shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
                  >
                    <Send className="w-3.5 h-3.5" />
                    {submittingFeedback ? 'Saving Feedback...' : 'Submit Feedback'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        InboxPilot — Autonomous AI Email Triage Assistant
      </footer>
    </div>
  );
};

export default App;
