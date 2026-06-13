import React from 'react';

// Per-category icon + color accent for the industry taxonomy.
const CATEGORY_STYLES = {
  SECURITY:     { icon: '🛡️', cls: 'bg-red-50 text-red-700 border-red-200/60' },
  BILLING:      { icon: '💳', cls: 'bg-emerald-50 text-emerald-700 border-emerald-200/60' },
  SYSTEM_ALERT: { icon: '🚨', cls: 'bg-orange-50 text-orange-700 border-orange-200/60' },
  SUPPORT:      { icon: '🎧', cls: 'bg-violet-50 text-violet-700 border-violet-200/60' },
  SALES:        { icon: '💼', cls: 'bg-teal-50 text-teal-700 border-teal-200/60' },
  RECRUITMENT:  { icon: '🧑‍💼', cls: 'bg-indigo-50 text-indigo-700 border-indigo-200/60' },
  NEWSLETTER:   { icon: '📰', cls: 'bg-sky-50 text-sky-700 border-sky-200/60' },
  PROMOTION:    { icon: '🏷️', cls: 'bg-pink-50 text-pink-700 border-pink-200/60' },
  SOCIAL:       { icon: '💬', cls: 'bg-cyan-50 text-cyan-700 border-cyan-200/60' },
  LEGAL:        { icon: '⚖️', cls: 'bg-amber-50 text-amber-700 border-amber-200/60' },
  PERSONAL:     { icon: '✉️', cls: 'bg-lime-50 text-lime-700 border-lime-200/60' },
  SPAM:         { icon: '🚫', cls: 'bg-slate-100 text-slate-500 border-slate-200/60' },
  OTHER:        { icon: '📁', cls: 'bg-slate-50 text-slate-600 border-slate-200/60' },
};

export default function NotificationCard({ alert }) {
  // Determine semantic color rings depending on priority tier
  const priorityStyles = {
    HIGH: 'bg-rose-50 text-rose-700 border-rose-200/60',
    MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200/60',
    LOW: 'bg-sky-50 text-sky-700 border-sky-200/60'
  };

  const category = CATEGORY_STYLES[alert.category] || CATEGORY_STYLES.OTHER;

  return (
    <div className="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-md">
      <div>
        {/* Card Header row metadata */}
        <div className="mb-4 flex items-center justify-between gap-2">
          <span className={`inline-block rounded-lg px-2.5 py-1 text-[10px] font-extrabold tracking-wider uppercase border ${category.cls}`}>
            {category.icon} {alert.category}
          </span>
          <span className={`inline-block rounded-lg px-2.5 py-1 text-[10px] font-black tracking-widest uppercase border ${priorityStyles[alert.priority] || priorityStyles.LOW}`}>
            {alert.priority}
          </span>
        </div>

        {/* Content Elements */}
        <h3 className="text-sm font-bold leading-snug text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2" title={alert.subject}>
          {alert.subject}
        </h3>
        
        <div className="mt-2 flex items-center gap-1.5 text-xs text-slate-400">
          <span>From:</span>
          <span className="font-semibold text-slate-600 truncate max-w-50">{alert.sender}</span>
        </div>

        {/* Reason Block Box Panel */}
        <div className="mt-5 rounded-xl bg-slate-50 p-4 border border-slate-100 group-hover:bg-slate-50/50 transition-all">
          <p className="text-[9px] font-extrabold text-slate-400 uppercase tracking-widest">
            🤖 AI Rationale Mapping
          </p>
          <p className="mt-1.5 text-xs font-medium leading-relaxed text-slate-600">
            {alert.reason}
          </p>
        </div>
      </div>

      {/* Card Footer section timeline string */}
      <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
        <span>Received Axis</span>
        <span className="font-mono text-slate-500">
          ⏰ {new Date(alert.received_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}