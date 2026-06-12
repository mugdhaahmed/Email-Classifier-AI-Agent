// import React from 'react';

// export default function Header({ isConnected }) {
//   return (
//     <header className="border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
//       <div className="mx-auto flex max-w-7xl items-center justify-between">
//         <div>
//           <h1 className="text-xl font-bold text-slate-900 tracking-tight">
//             Email Classifier AI Operations Center
//           </h1>
//           <p className="text-xs text-slate-500">
//             Automated Email Reading & Triage Pipeline
//           </p>
//         </div>
        
//         {/* Live Sync Status Indicator */}
//         <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium">
//           <span className={`h-2.5 w-2.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
//           <span className={isConnected ? 'text-emerald-700' : 'text-rose-700'}>
//             {isConnected ? 'STREAM ACTIVE' : 'STREAM OFFLINE'}
//           </span>
//         </div>
//       </div>
//     </header>
//   );
// }

import React from 'react';

export default function Header({ isConnected, totalCount }) {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 px-8 py-4 backdrop-blur-md">
      <div className="flex items-center justify-between">
        {/* Search / Global Action Area */}
        <div className="flex items-center gap-4 w-96">
          <div className="relative w-full">
            <span className="absolute inset-y-0 left-3 flex items-center text-slate-400 text-sm">🔍</span>
            <input 
              type="text" 
              placeholder="Search automated triage stream..." 
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-xs font-medium text-slate-700 outline-none transition-all focus:border-slate-400 focus:bg-white"
              disabled
            />
          </div>
        </div>
        
        {/* Connection & Meta Nodes */}
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-bold text-slate-900">System Monitor Layer</p>
            <p className="text-[10px] text-slate-400 font-medium">v1.1.0 Active</p>
          </div>
          <div className="h-8 w-px bg-slate-200 hidden sm:block" />
          
          <div className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold tracking-wide shadow-sm border ${
            isConnected 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}>
            <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            {isConnected ? 'STREAM ON' : 'DISCONNECTED'}
          </div>
        </div>
      </div>
    </header>
  );
}