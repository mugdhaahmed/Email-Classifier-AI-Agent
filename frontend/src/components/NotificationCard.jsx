import React from 'react';

export default function NotificationCard({ alert }) {
  // Determine semantic color rings depending on priority tier
  const priorityStyles = {
    HIGH: 'bg-rose-50 text-rose-700 border-rose-200/60',
    MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200/60',
    LOW: 'bg-sky-50 text-sky-700 border-sky-200/60'
  };

  return (
    <div className="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-md">
      <div>
        {/* Card Header row metadata */}
        <div className="mb-4 flex items-center justify-between gap-2">
          <span className="inline-block rounded-lg bg-slate-100 px-2.5 py-1 text-[10px] font-extrabold text-slate-600 tracking-wider uppercase border border-slate-200/40">
            📁 {alert.category}
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
          ⏰ {new Date(alert.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}