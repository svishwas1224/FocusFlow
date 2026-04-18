export interface FocusState {
  title: string
  category: string
  focus_score: number
  activity_rate: number
  forbidden: boolean
  intervention_required: boolean
}

export interface PieSegment {
  name: string
  value: number
}

export interface ReportPoint {
  label: string
  value: number
}

export interface SettingsData {
  id: number
  blocked_apps: string[]
  blocked_urls: string[]
  aggressive_mode: boolean
  pomodoro_enabled: boolean
}

export type PomodoroMode = 'focus' | 'short_break' | 'long_break'
