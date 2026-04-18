import { useEffect, useMemo, useState } from 'react'
import { Activity } from 'lucide-react'
import { PieChart, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Pie, Cell, Legend } from 'recharts'
import { FocusState, PieSegment, ReportPoint } from '../types'

const API_BASE = 'http://127.0.0.1:8000'
const COLORS = ['#22c55e', '#f97316', '#3b82f6']

interface DashboardProps {
  activeState: FocusState | null
}

export default function Dashboard({ activeState }: DashboardProps) {
  const [pieData, setPieData] = useState<PieSegment[]>([])
  const [lineData, setLineData] = useState<ReportPoint[]>([])

  useEffect(() => {
    async function fetchReports() {
      const [pieRes, lineRes] = await Promise.all([
        fetch(`${API_BASE}/reports/pie`),
        fetch(`${API_BASE}/reports/focus-line`),
      ])
      setPieData(await pieRes.json())
      setLineData(await lineRes.json())
    }
    fetchReports().catch(console.error)
  }, [])

  const scoreLabel = useMemo(() => {
    if (!activeState) return 'Pending...'
    if (activeState.intervention_required) return 'Intervene'
    if (activeState.forbidden) return 'Blocked'
    return activeState.category === 'focus' ? 'On task' : 'Monitoring'
  }, [activeState])

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">Current Focus</h2>
              <p className="text-slate-400">Live analysis from your active window and input rate.</p>
            </div>
            <div className="rounded-3xl bg-slate-950 px-4 py-2 text-sm text-slate-200">{scoreLabel}</div>
          </div>
          <div className="space-y-4">
            <div className="rounded-3xl bg-slate-950/80 p-5">
              <p className="text-slate-400">Active Window</p>
              <p className="mt-2 text-lg font-semibold text-white">{activeState?.title || 'Not detected'}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { label: 'Score', value: activeState?.focus_score ?? 0 },
                { label: 'Category', value: activeState?.category ?? 'neutral' },
                { label: 'Activity / sec', value: activeState?.activity_rate.toFixed(2) ?? '0.00' },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl bg-slate-950/80 p-4">
                  <p className="text-sm text-slate-400">{item.label}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
          <div className="mb-4 flex items-center gap-3 text-lg font-semibold">
            <Activity size={20} /> Productivity composition
          </div>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={4}>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend verticalAlign="bottom" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <section className="rounded-3xl bg-slate-900/90 p-6 shadow-xl ring-1 ring-slate-700">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">24-hour Focus Trend</h2>
            <p className="text-slate-400">A rolling line graph of session focus levels.</p>
          </div>
        </div>
        <div className="h-96 rounded-3xl bg-slate-950/80 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData}>
              <CartesianGrid stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
              <YAxis domain={[0, 100]} stroke="#94a3b8" />
              <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
              <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={3} dot />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
}
