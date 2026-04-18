import { useEffect, useMemo, useState } from 'react'
import { Play, Pause, Repeat, Activity } from 'lucide-react'
import { PomodoroMode } from '../types'

const API_BASE = 'http://127.0.0.1:8000'

interface TimerState {
  mode: PomodoroMode | null
  started_at: string | null
  duration: number
  running: boolean
}

const modes: { label: string; value: PomodoroMode }[] = [
  { label: 'Focus', value: 'focus' },
  { label: 'Short Break', value: 'short_break' },
  { label: 'Long Break', value: 'long_break' },
]

export default function TimerPanel() {
  const [timer, setTimer] = useState<TimerState>({ mode: null, started_at: null, duration: 0, running: false })
  const [selectedMode, setSelectedMode] = useState<PomodoroMode>('focus')

  useEffect(() => {
    fetch(`${API_BASE}/timer/state`)
      .then((res) => res.json())
      .then((data) => setTimer(data))
      .catch(console.error)
  }, [])

  const remaining = useMemo(() => {
    if (!timer.running || !timer.started_at) return timer.duration
    const elapsed = (Date.now() - new Date(timer.started_at).getTime()) / 1000
    return Math.max(timer.duration - elapsed, 0)
  }, [timer])

  async function startTimer() {
    const resp = await fetch(`${API_BASE}/timer/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: selectedMode }),
    })
    setTimer(await resp.json())
  }

  async function stopTimer() {
    const resp = await fetch(`${API_BASE}/timer/stop`, { method: 'POST' })
    setTimer(await resp.json())
  }

  return (
    <div className="rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Pomodoro Timer</h2>
          <p className="text-slate-400">Start a focused session and block distracting sites automatically.</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-3xl bg-slate-950 px-4 py-2 text-sm text-slate-200">
          <Activity size={16} /> {timer.running ? 'Running' : 'Stopped'}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_0.7fr]">
        <div className="space-y-4 rounded-3xl bg-slate-950/80 p-6">
          <div className="flex flex-wrap items-center gap-3">
            {modes.map((mode) => (
              <button
                key={mode.value}
                className={`rounded-full px-4 py-2 text-sm ${selectedMode === mode.value ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
                onClick={() => setSelectedMode(mode.value)}
              >
                {mode.label}
              </button>
            ))}
          </div>
          <div className="rounded-3xl bg-slate-900 p-6 text-center">
            <p className="text-sm text-slate-400">Current mode</p>
            <p className="mt-3 text-4xl font-semibold text-white">{timer.mode ?? 'None'}</p>
            <p className="mt-2 text-slate-400">{Math.floor(remaining / 60)}:{String(Math.floor(remaining % 60)).padStart(2, '0')}</p>
          </div>
        </div>

        <div className="space-y-4">
          <button
            onClick={startTimer}
            className="inline-flex w-full items-center justify-center gap-2 rounded-3xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-emerald-400"
          >
            <Play size={16} /> Start Timer
          </button>
          <button
            onClick={stopTimer}
            className="inline-flex w-full items-center justify-center gap-2 rounded-3xl bg-rose-500 px-5 py-3 text-sm font-semibold text-white hover:bg-rose-400"
          >
            <Pause size={16} /> Stop Timer
          </button>
          <div className="rounded-3xl bg-slate-950/80 p-4 text-slate-200">
            <h3 className="text-sm font-semibold text-white">Auto-blocker</h3>
            <p className="mt-2 text-sm text-slate-400">The blocker activates automatically when a session starts.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
