import { useState } from 'react'
import { Settings2, Link, Slash } from 'lucide-react'
import { SettingsData } from '../types'

const API_BASE = 'http://127.0.0.1:8000'

interface SettingsProps {
  settings: SettingsData
  onSettingsChange: (updated: SettingsData) => void
}

export default function SettingsPanel({ settings, onSettingsChange }: SettingsProps) {
  const [blockedApps, setBlockedApps] = useState(settings.blocked_apps.join(', '))
  const [blockedUrls, setBlockedUrls] = useState(settings.blocked_urls.join(', '))
  const [aggressiveMode, setAggressiveMode] = useState(settings.aggressive_mode)
  const [pomodoroEnabled, setPomodoroEnabled] = useState(settings.pomodoro_enabled)

  async function save() {
    const payload = {
      blocked_apps: blockedApps.split(',').map((item) => item.trim()).filter(Boolean),
      blocked_urls: blockedUrls.split(',').map((item) => item.trim()).filter(Boolean),
      aggressive_mode: aggressiveMode,
      pomodoro_enabled: pomodoroEnabled,
    }
    const response = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await response.json()
    onSettingsChange(result)
  }

  return (
    <div className="rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
      <div className="mb-6 flex items-center gap-3 text-xl font-semibold">
        <Settings2 size={20} /> Preferences
      </div>
      <div className="grid gap-6">
        <div className="rounded-3xl bg-slate-950/80 p-5">
          <label className="block text-sm text-slate-400">Blocked apps (comma separated)</label>
          <textarea
            className="mt-3 w-full rounded-3xl border border-slate-700 bg-slate-900 p-4 text-slate-100 outline-none focus:border-sky-500"
            rows={4}
            value={blockedApps}
            onChange={(e) => setBlockedApps(e.target.value)}
          />
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-5">
          <label className="block text-sm text-slate-400">Blocked URLs (comma separated)</label>
          <textarea
            className="mt-3 w-full rounded-3xl border border-slate-700 bg-slate-900 p-4 text-slate-100 outline-none focus:border-sky-500"
            rows={4}
            value={blockedUrls}
            onChange={(e) => setBlockedUrls(e.target.value)}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl bg-slate-950/80 p-5">
            <label className="inline-flex items-center gap-2 text-slate-200">
              <input type="checkbox" checked={aggressiveMode} onChange={(e) => setAggressiveMode(e.target.checked)} className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-emerald-500" />
              Aggressive mode
            </label>
            <p className="mt-2 text-sm text-slate-400">Block access more aggressively during focus sessions.</p>
          </div>
          <div className="rounded-3xl bg-slate-950/80 p-5">
            <label className="inline-flex items-center gap-2 text-slate-200">
              <input type="checkbox" checked={pomodoroEnabled} onChange={(e) => setPomodoroEnabled(e.target.checked)} className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-sky-500" />
              Pomodoro enabled
            </label>
            <p className="mt-2 text-sm text-slate-400">Toggle Pomodoro auto-blocker integration.</p>
          </div>
        </div>
        <button
          onClick={save}
          className="inline-flex items-center gap-2 rounded-3xl bg-sky-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-sky-400"
        >
          <Link size={16} /> Save settings
        </button>
        <div className="rounded-3xl bg-slate-950/80 p-5 text-slate-300">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <Slash size={16} /> Note
          </div>
          <p className="mt-2 text-sm text-slate-400">On Windows, host file blocking requires administrator privileges.</p>
        </div>
      </div>
    </div>
  )
}
