import { useEffect, useMemo, useState } from 'react'
import { Activity, Settings, ShieldCheck, Timer } from 'lucide-react'
import Dashboard from './components/Dashboard'
import TimerPanel from './components/Timer'
import SettingsPanel from './components/Settings'
import { FocusState, SettingsData } from './types'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [activeState, setActiveState] = useState<FocusState | null>(null)
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [selectedView, setSelectedView] = useState<'dashboard' | 'timer' | 'settings'>('dashboard')

  useEffect(() => {
    async function loadState() {
      const [stateRes, settingsRes] = await Promise.all([
        fetch(`${API_BASE}/monitor/state`),
        fetch(`${API_BASE}/settings`),
      ])
      setActiveState(await stateRes.json())
      setSettings(await settingsRes.json())
    }

    loadState().catch(console.error)
    const interval = setInterval(loadState, 8000)
    return () => clearInterval(interval)
  }, [])

  const welcome = useMemo(() => {
    if (!activeState) return 'Loading your productivity dashboard...'
    if (activeState.intervention_required) return 'Intervention required — take a short break now.'
    if (activeState.forbidden) return 'A blocked app was detected. Stay focused.'
    return 'FocusFlow AI is monitoring your attention and productivity.'
  }, [activeState])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl p-6">
        <header className="mb-8 rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-4xl font-semibold">FocusFlow AI</h1>
              <p className="mt-2 text-slate-400">Smart productivity insights, app blocking, and Pomodoro support.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm ${selectedView === 'dashboard' ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
                onClick={() => setSelectedView('dashboard')}
              >
                <Activity size={16} /> Dashboard
              </button>
              <button
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm ${selectedView === 'timer' ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
                onClick={() => setSelectedView('timer')}
              >
                <Timer size={16} /> Timer
              </button>
              <button
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm ${selectedView === 'settings' ? 'bg-violet-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
                onClick={() => setSelectedView('settings')}
              >
                <Settings size={16} /> Settings
              </button>
            </div>
          </div>
          <div className="mt-6 rounded-3xl bg-slate-950/80 p-5 text-slate-200">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">Status</h2>
                <p className="mt-1 text-slate-400">{welcome}</p>
              </div>
              <span className="inline-flex items-center gap-2 rounded-full bg-slate-800 px-3 py-2 text-sm text-slate-200">
                <ShieldCheck size={16} /> {activeState?.focus_score ?? 0}% score
              </span>
            </div>
          </div>
        </header>

        {selectedView === 'dashboard' && <Dashboard activeState={activeState} />}
        {selectedView === 'timer' && <TimerPanel />}
        {selectedView === 'settings' && settings && <SettingsPanel settings={settings} onSettingsChange={setSettings} />}
      </div>
    </div>
  )
}

export default App
