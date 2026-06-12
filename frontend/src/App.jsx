import React, { useState } from 'react';
import { useEmailSocket } from './hooks/useEmailSocket';
import Header from './components/Header';
import FilterBar from './components/FilterBar';
import NotificationCard from './components/NotificationCard';

function App() {
  const { notifications, isConnected } = useEmailSocket();
  const [filter, setFilter] = useState('ALL');

  const filteredNotifications = notifications.filter(item => {
    if (filter === 'ALL') return true;
    return item.priority === filter;
  });

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-indigo-500 selection:text-white">
      
      {/* 🚀 Modern Product Layout Sidebar Left Pane */}
      <aside className="hidden md:flex w-64 shrink-0 flex-col justify-between border-r border-slate-200 bg-slate-900 p-6">
        <div>
          {/* Brand Logo node section */}
          <div className="flex items-center gap-3 px-2 py-3 border-b border-slate-800">
            <span className="text-xl">⚡</span>
            <div>
              <h1 className="text-sm font-black text-white tracking-wider uppercase">Email Classifier AI Agent</h1>
              <p className="text-[10px] text-slate-400 font-bold tracking-tight">Operations Node</p>
            </div>
          </div>

          {/* Navigation Action Links list group */}
          <nav className="mt-8 flex flex-col gap-1.5">
            <button className="flex items-center gap-3 rounded-xl bg-slate-800 px-4 py-2.5 text-xs font-bold text-white transition-all text-left">
              <span>📊</span> Dashboard Stream
            </button>
            <button className="flex items-center gap-3 rounded-xl px-4 py-2.5 text-xs font-bold text-slate-400 hover:bg-slate-800 hover:text-white transition-all text-left" disabled>
              <span>⚙️</span> Ingestion Config
            </button>
            <button className="flex items-center gap-3 rounded-xl px-4 py-2.5 text-xs font-bold text-slate-400 hover:bg-slate-800 hover:text-white transition-all text-left" disabled>
              <span>🔑</span> Model Registry
            </button>
          </nav>
        </div>

        {/* Corporate bottom label node */}
        <div className="px-2 py-3 border-t border-slate-800 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
          © 2026 Mugdha Ahmed
        </div>
      </aside>

      {/* Main Content Workspace viewport wrapper node panel frame layout area */}
      <div className="flex flex-col flex-1 min-w-0">
        <Header isConnected={isConnected} totalCount={filteredNotifications.length} />

        <main className="flex-1 overflow-y-auto px-8 py-8">
          <FilterBar 
            filter={filter} 
            setFilter={setFilter} 
            totalCount={filteredNotifications.length} 
            notifications={notifications}
          />

          {/* Empty State Layout */}
          {filteredNotifications.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-16 text-center shadow-sm max-w-xl mx-auto mt-12">
              <div className="text-4xl">📨</div>
              <h3 className="mt-4 text-base font-bold text-slate-900 tracking-tight">Queue completely clear</h3>
              <p className="mt-1.5 text-xs text-slate-500 max-w-xs mx-auto leading-relaxed">
                The Gemini AI classifier sequence is actively listening for new critical network ingestion streams[cite: 5, 6].
              </p>
            </div>
          ) : (
            /* Premium Responsive Cards Layout Grid system component */
            <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
              {filteredNotifications.map((alert) => (
                <NotificationCard key={alert.id} alert={alert} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;