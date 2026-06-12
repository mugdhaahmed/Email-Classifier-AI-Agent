// import React from 'react';

// export default function FilterBar({ filter, setFilter, totalCount, notifications }) {
//   return (
//     <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
//       <div className="flex gap-2">
//         {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
//           <button
//             key={lvl}
//             onClick={() => setFilter(lvl)}
//             className={`rounded-lg px-4 py-2 text-xs font-semibold uppercase transition-all ${
//               filter === lvl
//                 ? 'bg-slate-900 text-white shadow-md'
//                 : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
//             }`}
//           >
//             {lvl} ({lvl === 'ALL' ? totalCount : notifications.filter(n => n.priority === lvl).length})
//           </button>
//         ))}
//       </div>
//       <span className="text-xs font-medium text-slate-500">
//         Showing {totalCount} flagged operations
//       </span>
//     </div>
//   );
// }



import React from 'react';

export default function FilterBar({ filter, setFilter, totalCount, notifications }) {
  const absoluteTotal = notifications.length;
  const highPriorityCount = notifications.filter(n => n.priority === 'HIGH').length;
  const mediumPriorityCount = notifications.filter(n => n.priority === 'MEDIUM').length;

  return (
    <div className="mb-8">
      {/* Segment Filter Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-200 pb-5">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Triage Incident Stream</h2>
          <p className="text-xs text-slate-500 mt-0.5">Real-time threat classification and anomaly reports mapping.</p>
        </div>
        
        <div className="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200/60 shadow-inner">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              className={`rounded-lg px-4 py-2 text-xs font-bold uppercase transition-all ${
                filter === lvl
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Analytics KPI Dashboard Grid Cards */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mt-6">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Flagged</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{absoluteTotal}</p>
        </div>
        <div className="rounded-2xl border border-rose-100 bg-rose-50/30 p-5 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-rose-500">Critical High</p>
          <p className="text-2xl font-black text-rose-700 mt-1">{highPriorityCount}</p>
        </div>
        <div className="rounded-2xl border border-amber-100 bg-amber-50/30 p-5 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-amber-600">Medium Risk</p>
          <p className="text-2xl font-black text-amber-700 mt-1">{mediumPriorityCount}</p>
        </div>
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Current View</p>
          <p className="text-2xl font-black text-indigo-600 mt-1">{totalCount}</p>
        </div>
      </div>
    </div>
  );
}