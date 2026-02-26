'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts'
import {
  Phone,
  Calendar,
  Users,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  Headphones,
  BarChart3,
  Activity,
  Filter
} from 'lucide-react'

// Types
interface CallStats {
  total_calls: number
  booked_appointments: number
  conversion_rate: number
}

interface LeadDistribution {
  A: number
  B: number
  C: number
  N: number
}

interface RecentCall {
  id: string
  phone_number: string
  lead_score: string
  call_outcome: string
  started_at: string
  duration_seconds: number
}

interface ObjectionStats {
  by_type: Record<string, number>
  by_outcome: Record<string, number>
  total: number
}

// Hook to safely initialize Supabase client
function useSupabaseClient() {
  const [supabase, setSupabase] = useState<ReturnType<typeof createClient> | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Only initialize on client side
    if (typeof window === 'undefined') {
      return
    }

    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

      if (!supabaseUrl || !supabaseKey) {
        setError('Supabase configuration missing')
        console.error('Supabase URL or Key not configured')
        return
      }

      const client = createClient(supabaseUrl, supabaseKey)
      setSupabase(client)
    } catch (err) {
      setError('Failed to initialize Supabase')
      console.error('Supabase initialization error:', err)
    }
  }, [])

  return { supabase, error }
}

export default function Dashboard() {
  const { supabase, error: supabaseError } = useSupabaseClient()
  const [stats, setStats] = useState<CallStats | null>(null)
  const [leadDist, setLeadDist] = useState<LeadDistribution | null>(null)
  const [recentCalls, setRecentCalls] = useState<RecentCall[]>([])
  const [objections, setObjections] = useState<ObjectionStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7')

  useEffect(() => {
    // Only fetch data when supabase client is initialized
    if (!supabase) {
      if (supabaseError) {
        setLoading(false)
      }
      return
    }

    fetchDashboardData()

    // Subscribe to real-time updates
    const channel = supabase
      .channel('dashboard-updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'call_summaries' }, () => {
        fetchDashboardData()
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [timeRange, supabase, supabaseError])

  async function fetchDashboardData() {
    try {
      if (!supabase) {
        console.warn('Supabase client not initialized')
        return
      }

      setLoading(true)

      // Fetch conversion stats
      const { data: statsData } = await supabase
        .from('call_summaries')
        .select('call_outcome')
        .gte('created_at', new Date(Date.now() - parseInt(timeRange) * 24 * 60 * 60 * 1000).toISOString())

      const totalCalls = statsData?.length || 0
      const booked = statsData?.filter(c => c.call_outcome === 'Termin gebucht').length || 0

      setStats({
        total_calls: totalCalls,
        booked_appointments: booked,
        conversion_rate: totalCalls > 0 ? Math.round((booked / totalCalls) * 100) : 0
      })

      // Fetch lead distribution
      const { data: leadsData } = await supabase
        .from('call_summaries')
        .select('lead_score')

      const distribution: LeadDistribution = { A: 0, B: 0, C: 0, N: 0 }
      leadsData?.forEach(lead => {
        if (lead.lead_score in distribution) {
          distribution[lead.lead_score as keyof LeadDistribution]++
        }
      })
      setLeadDist(distribution)

      // Fetch recent calls
      const { data: callsData } = await supabase
        .from('calls')
        .select(`
          id,
          phone_number,
          started_at,
          duration_seconds,
          call_summaries (lead_score, call_outcome)
        `)
        .order('started_at', { ascending: false })
        .limit(10)

      const formattedCalls: RecentCall[] = callsData?.map(call => ({
        id: call.id,
        phone_number: call.phone_number,
        started_at: call.started_at,
        duration_seconds: call.duration_seconds || 0,
        lead_score: call.call_summaries?.[0]?.lead_score || 'N',
        call_outcome: call.call_summaries?.[0]?.call_outcome || 'Unbekannt'
      })) || []

      setRecentCalls(formattedCalls)

      // Fetch objection stats
      const { data: objectionsData } = await supabase
        .from('objections')
        .select('objection_type, outcome')

      const objStats: ObjectionStats = {
        by_type: {},
        by_outcome: { 'Überwunden': 0, 'Nicht überwunden': 0, 'Offen': 0 },
        total: objectionsData?.length || 0
      }

      objectionsData?.forEach(obj => {
        objStats.by_type[obj.objection_type] = (objStats.by_type[obj.objection_type] || 0) + 1
        if (obj.outcome in objStats.by_outcome) {
          objStats.by_outcome[obj.outcome]++
        }
      })

      setObjections(objStats)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Chart data preparation
  const leadChartData = leadDist ? [
    { name: 'A (Heiß)', value: leadDist.A, color: '#22c55e' },
    { name: 'B (Warm)', value: leadDist.B, color: '#3b82f6' },
    { name: 'C (Kalt)', value: leadDist.C, color: '#f59e0b' },
    { name: 'N (Nein)', value: leadDist.N, color: '#6b7280' },
  ] : []

  const objectionChartData = objections ? Object.entries(objections.by_type).map(([type, count]) => ({
    name: type,
    value: count
  })) : []

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatPhone = (phone: string) => {
    // Mask phone number for privacy
    if (phone.length > 4) {
      return phone.slice(0, -4).replace(/./g, '*') + phone.slice(-4)
    }
    return phone
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-everlast-600 p-2 rounded-lg">
                <Headphones className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Everlast Voice Agent</h1>
                <p className="text-sm text-gray-500">Dashboard & KPI Tracking</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <span className="text-sm text-gray-600 px-2">Zeitraum:</span>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="bg-white border-0 rounded-md text-sm py-1 px-3 focus:ring-2 focus:ring-everlast-500"
                >
                  <option value="7">Letzte 7 Tage</option>
                  <option value="30">Letzte 30 Tage</option>
                  <option value="90">Letzte 90 Tage</option>
                </select>
              </div>

              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {supabaseError ? (
          <div className="flex flex-col items-center justify-center h-64 text-red-600">
            <AlertCircle className="w-12 h-12 mb-4" />
            <p className="text-lg font-medium">{supabaseError}</p>
            <p className="text-sm text-gray-500 mt-2">Bitte überprüfen Sie Ihre Umgebungsvariablen</p>
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-everlast-600"></div>
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Total Calls */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Gesamt-Calls</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stats?.total_calls || 0}</p>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <Phone className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <Activity className="w-4 h-4 text-green-500 mr-1" />
                  <span className="text-green-600 font-medium">Aktiv</span>
                </div>
              </div>

              {/* Conversion Rate */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Conversion Rate</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stats?.conversion_rate || 0}%</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${Math.min(stats?.conversion_rate || 0, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Ziel: ≥35%</p>
                </div>
              </div>

              {/* Appointments */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Termine gebucht</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stats?.booked_appointments || 0}</p>
                  </div>
                  <div className="bg-purple-50 p-3 rounded-lg">
                    <Calendar className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  <span className="text-green-600">{stats?.booked_appointments || 0} Bestätigt</span>
                </div>
              </div>

              {/* Qualified Leads */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Qualifizierte Leads</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">
                      {(leadDist?.A || 0) + (leadDist?.B || 0)}
                    </p>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg">
                    <Users className="w-6 h-6 text-orange-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center space-x-3 text-sm">
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                    {leadDist?.A || 0} A
                  </span>
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
                    {leadDist?.B || 0} B
                  </span>
                </div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Lead Distribution Chart */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Lead-Score Verteilung</h3>
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={leadChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {leadChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-4 gap-2 mt-4 text-center text-xs">
                  <div className="p-2 bg-green-50 rounded">
                    <p className="font-semibold text-green-700">{leadDist?.A || 0}</p>
                    <p className="text-green-600">Heiß</p>
                  </div>
                  <div className="p-2 bg-blue-50 rounded">
                    <p className="font-semibold text-blue-700">{leadDist?.B || 0}</p>
                    <p className="text-blue-600">Warm</p>
                  </div>
                  <div className="p-2 bg-amber-50 rounded">
                    <p className="font-semibold text-amber-700">{leadDist?.C || 0}</p>
                    <p className="text-amber-600">Kalt</p>
                  </div>
                  <div className="p-2 bg-gray-50 rounded">
                    <p className="font-semibold text-gray-700">{leadDist?.N || 0}</p>
                    <p className="text-gray-600">Nein</p>
                  </div>
                </div>
              </div>

              {/* Objection Handling Chart */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Einwand-Analyse</h3>
                  <AlertCircle className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={objectionChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#0ea5e9" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                {objections && (
                  <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-2 bg-green-50 rounded">
                      <p className="font-semibold text-green-700">{objections.by_outcome['Überwunden'] || 0}</p>
                      <p className="text-green-600">Überwunden</p>
                    </div>
                    <div className="p-2 bg-red-50 rounded">
                      <p className="font-semibold text-red-700">{objections.by_outcome['Nicht überwunden'] || 0}</p>
                      <p className="text-red-600">Nicht überwunden</p>
                    </div>
                    <div className="p-2 bg-gray-50 rounded">
                      <p className="font-semibold text-gray-700">{objections.by_outcome['Offen'] || 0}</p>
                      <p className="text-gray-600">Offen</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Calls Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Letzte Calls</h3>
                <Filter className="w-5 h-5 text-gray-400" />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Zeit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nummer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dauer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ergebnis</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {recentCalls.map((call) => (
                      <tr key={call.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(call.started_at).toLocaleString('de-DE', {
                            day: '2-digit',
                            month: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatPhone(call.phone_number)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            call.lead_score === 'A' ? 'bg-green-100 text-green-800' :
                            call.lead_score === 'B' ? 'bg-blue-100 text-blue-800' :
                            call.lead_score === 'C' ? 'bg-amber-100 text-amber-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {call.lead_score}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1 text-gray-400" />
                            {formatDuration(call.duration_seconds)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                            call.call_outcome === 'Termin gebucht' ? 'bg-green-100 text-green-800' :
                            call.call_outcome === 'Nicht interessiert' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {call.call_outcome === 'Termin gebucht' && <CheckCircle className="w-3 h-3 mr-1" />}
                            {call.call_outcome === 'Nicht interessiert' && <XCircle className="w-3 h-3 mr-1" />}
                            {call.call_outcome}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
