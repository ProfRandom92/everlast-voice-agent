'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
} from 'recharts'
import {
  Phone,
  Calendar,
  Users,
  TrendingUp,
  Clock,
  Headphones,
  Moon,
  Sun,
  Filter,
  Download,
  RefreshCw,
  Activity,
  Zap,
  Target,
  BarChart3,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SkeletonCard, SkeletonChart, SkeletonTable } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/hooks/useTheme'
import { formatPhone, formatDuration, formatDate, calculatePercentage, cn } from '@/lib/utils'

// Types
interface CallStats {
  total_calls: number
  booked_appointments: number
  conversion_rate: number
  avg_duration: number
  active_calls: number
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
  sentiment: string
}

interface ObjectionStats {
  by_type: Record<string, number>
  by_outcome: Record<string, number>
  total: number
}

interface TimeSeriesData {
  date: string
  calls: number
  appointments: number
  conversion: number
}

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
}

// Custom tooltip for charts
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-3 shadow-xl">
        <p className="font-semibold text-gray-900 dark:text-gray-100 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600 dark:text-gray-400">{entry.name}:</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{entry.value}</span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function DashboardV2() {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [supabase, setSupabase] = useState<any>(null)
  const [stats, setStats] = useState<CallStats | null>(null)
  const [leadDist, setLeadDist] = useState<LeadDistribution | null>(null)
  const [recentCalls, setRecentCalls] = useState<RecentCall[]>([])
  const [objections, setObjections] = useState<ObjectionStats | null>(null)
  const [timeSeries, setTimeSeries] = useState<TimeSeriesData[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7')
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (supabaseUrl && supabaseKey) {
      const client = createClient(supabaseUrl, supabaseKey)
      setSupabase(client)
    }
  }, [])

  const fetchDashboardData = async () => {
    if (!supabase) return

    try {
      setLoading(true)
      const daysAgo = new Date(Date.now() - parseInt(timeRange) * 24 * 60 * 60 * 1000).toISOString()

      // Fetch stats
      const { data: statsData } = await supabase
        .from('call_summaries')
        .select('call_outcome, duration_seconds')
        .gte('created_at', daysAgo)

      const totalCalls = statsData?.length || 0
      const booked = statsData?.filter((c: any) => c.call_outcome === 'Termin gebucht').length || 0
      const avgDuration = statsData?.length
        ? Math.round(statsData.reduce((acc: number, c: any) => acc + (c.duration_seconds || 0), 0) / statsData.length)
        : 0

      setStats({
        total_calls: totalCalls,
        booked_appointments: booked,
        conversion_rate: totalCalls > 0 ? Math.round((booked / totalCalls) * 100) : 0,
        avg_duration: avgDuration,
        active_calls: 0, // Would come from real-time system
      })

      // Fetch lead distribution
      const { data: leadsData } = await supabase.from('call_summaries').select('lead_score')
      const distribution: LeadDistribution = { A: 0, B: 0, C: 0, N: 0 }
      leadsData?.forEach((lead: any) => {
        if (lead.lead_score in distribution) {
          distribution[lead.lead_score as keyof LeadDistribution]++
        }
      })
      setLeadDist(distribution)

      // Fetch recent calls with sentiment
      const { data: callsData } = await supabase
        .from('calls')
        .select(`
          id,
          phone_number,
          started_at,
          duration_seconds,
          call_summaries (lead_score, call_outcome, sentiment)
        `)
        .order('started_at', { ascending: false })
        .limit(10)

      const formattedCalls: RecentCall[] = callsData?.map((call: any) => ({
        id: call.id,
        phone_number: call.phone_number,
        started_at: call.started_at,
        duration_seconds: call.duration_seconds || 0,
        lead_score: call.call_summaries?.[0]?.lead_score || 'N',
        call_outcome: call.call_summaries?.[0]?.call_outcome || 'Unbekannt',
        sentiment: call.call_summaries?.[0]?.sentiment || 'neutral',
      })) || []
      setRecentCalls(formattedCalls)

      // Fetch objections
      const { data: objectionsData } = await supabase.from('objections').select('objection_type, outcome')
      const objStats: ObjectionStats = {
        by_type: {},
        by_outcome: { Überwunden: 0, 'Nicht überwunden': 0, Offen: 0 },
        total: objectionsData?.length || 0,
      }
      objectionsData?.forEach((obj: any) => {
        objStats.by_type[obj.objection_type] = (objStats.by_type[obj.objection_type] || 0) + 1
        if (obj.outcome in objStats.by_outcome) {
          objStats.by_outcome[obj.outcome]++
        }
      })
      setObjections(objStats)

      // Fetch time series data
      const { data: timeData } = await supabase
        .from('call_summaries')
        .select('created_at, call_outcome')
        .gte('created_at', daysAgo)
        .order('created_at', { ascending: true })

      const timeMap = new Map<string, { calls: number; appointments: number }>()
      timeData?.forEach((item: any) => {
        const date = new Date(item.created_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
        const current = timeMap.get(date) || { calls: 0, appointments: 0 }
        current.calls++
        if (item.call_outcome === 'Termin gebucht') {
          current.appointments++
        }
        timeMap.set(date, current)
      })

      const seriesData: TimeSeriesData[] = Array.from(timeMap.entries()).map(([date, data]) => ({
        date,
        calls: data.calls,
        appointments: data.appointments,
        conversion: data.calls > 0 ? Math.round((data.appointments / data.calls) * 100) : 0,
      }))
      setTimeSeries(seriesData)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (supabase) {
      fetchDashboardData()

      const channel = supabase
        .channel('dashboard-v2-updates')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'call_summaries' }, () => {
          fetchDashboardData()
        })
        .subscribe()

      return () => {
        supabase.removeChannel(channel)
      }
    }
  }, [supabase, timeRange])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchDashboardData()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  const leadChartData = leadDist
    ? [
        { name: 'A (Heiß)', value: leadDist.A, color: '#22c55e' },
        { name: 'B (Warm)', value: leadDist.B, color: '#3b82f6' },
        { name: 'C (Kalt)', value: leadDist.C, color: '#f59e0b' },
        { name: 'N (Nein)', value: leadDist.N, color: '#6b7280' },
      ]
    : []

  const objectionChartData = objections
    ? Object.entries(objections.by_type).map(([type, count]) => ({
        name: type,
        value: count,
      }))
    : []

  const isDark = resolvedTheme === 'dark'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 transition-colors duration-300">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-b from-sky-100/30 to-transparent dark:from-sky-900/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-t from-purple-100/30 to-transparent dark:from-purple-900/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-800/50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Title */}
            <div className="flex items-center gap-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-br from-sky-500 to-blue-600 p-3 rounded-2xl shadow-lg shadow-sky-500/25"
              >
                <Headphones className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
                  Everlast Voice Agent
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Real-time Lead Qualification Dashboard</p>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3">
              {/* Time Range */}
              <div className="flex items-center bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur rounded-xl p-1">
                {['7', '30', '90'].map((days) => (
                  <button
                    key={days}
                    onClick={() => setTimeRange(days)}
                    className={cn(
                      'px-3 py-1.5 text-sm font-medium rounded-lg transition-all duration-200',
                      timeRange === days
                        ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                    )}
                  >
                    {days === '7' ? '7D' : days === '30' ? '30D' : '90D'}
                  </button>
                ))}
              </div>

              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="rounded-xl"
              >
                {resolvedTheme === 'dark' ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </Button>

              {/* Refresh */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleRefresh}
                className="rounded-xl"
              >
                <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
              </Button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.main
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {loading ? (
            [...Array(4)].map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              {/* Total Calls */}
              <motion.div variants={itemVariants}>
                <Card variant="elevated" hover className="h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Gesamt-Calls</p>
                        <motion.p
                          initial={{ opacity: 0, scale: 0.5 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.2 }}
                          className="text-3xl font-bold text-gray-900 dark:text-white mt-1"
                        >
                          {stats?.total_calls || 0}
                        </motion.p>
                        <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                          <Activity className="w-4 h-4" />
                          <span>Live</span>
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-500/25">
                        <Phone className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Conversion Rate */}
              <motion.div variants={itemVariants}>
                <Card variant="elevated" hover className="h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Conversion Rate</p>
                        <motion.p
                          initial={{ opacity: 0, scale: 0.5 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.3 }}
                          className="text-3xl font-bold text-gray-900 dark:text-white mt-1"
                        >
                          {stats?.conversion_rate || 0}%
                        </motion.p>
                        <div className="mt-3">
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.min(stats?.conversion_rate || 0, 100)}%` }}
                              transition={{ delay: 0.5, duration: 0.8 }}
                              className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                            />
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Ziel: ≥35%</p>
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-3 rounded-2xl shadow-lg shadow-green-500/25">
                        <TrendingUp className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Appointments */}
              <motion.div variants={itemVariants}>
                <Card variant="elevated" hover className="h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Termine gebucht</p>
                        <motion.p
                          initial={{ opacity: 0, scale: 0.5 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.4 }}
                          className="text-3xl font-bold text-gray-900 dark:text-white mt-1"
                        >
                          {stats?.booked_appointments || 0}
                        </motion.p>
                        <div className="flex items-center gap-1 mt-2 text-sm text-purple-600 dark:text-purple-400">
                          <Zap className="w-4 h-4" />
                          <span>{stats?.booked_appointments || 0} Bestätigt</span>
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-purple-500 to-violet-600 p-3 rounded-2xl shadow-lg shadow-purple-500/25">
                        <Calendar className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Qualified Leads */}
              <motion.div variants={itemVariants}>
                <Card variant="elevated" hover className="h-full">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Qualifizierte Leads</p>
                        <motion.p
                          initial={{ opacity: 0, scale: 0.5 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.5 }}
                          className="text-3xl font-bold text-gray-900 dark:text-white mt-1"
                        >
                          {(leadDist?.A || 0) + (leadDist?.B || 0)}
                        </motion.p>
                        <div className="flex items-center gap-3 mt-2 text-xs">
                          <span className="flex items-center text-green-600">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1" />
                            {leadDist?.A || 0} A
                          </span>
                          <span className="flex items-center text-blue-600">
                            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1" />
                            {leadDist?.B || 0} B
                          </span>
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-3 rounded-2xl shadow-lg shadow-orange-500/25">
                        <Target className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </>
          )}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Lead Distribution */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <Card variant="elevated" className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-sky-500" />
                  Lead-Score Verteilung
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <SkeletonChart />
                ) : (
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
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Lead Stats Grid */}
                {!loading && leadDist && (
                  <div className="grid grid-cols-4 gap-2 mt-4">
                    {[
                      { label: 'A', value: leadDist.A, color: 'bg-emerald-500' },
                      { label: 'B', value: leadDist.B, color: 'bg-blue-500' },
                      { label: 'C', value: leadDist.C, color: 'bg-amber-500' },
                      { label: 'N', value: leadDist.N, color: 'bg-gray-500' },
                    ].map((item) => (
                      <motion.div
                        key={item.label}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.6 }}
                        className="text-center p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                      >
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{item.value}</p>
                        <div className="flex items-center justify-center gap-1 mt-1">
                          <div className={`w-2 h-2 rounded-full ${item.color}`} />
                          <span className="text-xs text-gray-500 dark:text-gray-400">{item.label}</span>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Call Volume Timeline */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <Card variant="elevated" className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-sky-500" />
                  Call Volume & Conversion Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <SkeletonChart />
                ) : (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={timeSeries}>
                        <defs>
                          <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                          </linearGradient>
                          <linearGradient id="colorAppointments" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                        <XAxis
                          dataKey="date"
                          tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
                          stroke={isDark ? '#374151' : '#e5e7eb'}
                        />
                        <YAxis
                          tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
                          stroke={isDark ? '#374151' : '#e5e7eb'}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Area
                          type="monotone"
                          dataKey="calls"
                          name="Calls"
                          stroke="#0ea5e9"
                          fillOpacity={1}
                          fill="url(#colorCalls)"
                          strokeWidth={2}
                        />
                        <Area
                          type="monotone"
                          dataKey="appointments"
                          name="Appointments"
                          stroke="#22c55e"
                          fillOpacity={1}
                          fill="url(#colorAppointments)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Objection Analysis */}
          <motion.div variants={itemVariants}>
            <Card variant="elevated" className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="w-5 h-5 text-amber-500" />
                  Einwand-Analyse
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <SkeletonChart />
                ) : (
                  <>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={objectionChartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                          <XAxis
                            dataKey="name"
                            tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 11 }}
                            interval={0}
                            stroke={isDark ? '#374151' : '#e5e7eb'}
                          />
                          <YAxis
                            tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
                            stroke={isDark ? '#374151' : '#e5e7eb'}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Bar
                            dataKey="value"
                            fill="#0ea5e9"
                            radius={[8, 8, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {objections && (
                      <div className="grid grid-cols-3 gap-3 mt-4">
                        {[
                          { label: 'Überwunden', value: objections.by_outcome['Überwunden'] || 0, color: 'bg-green-500' },
                          { label: 'Nicht überwunden', value: objections.by_outcome['Nicht überwunden'] || 0, color: 'bg-red-500' },
                          { label: 'Offen', value: objections.by_outcome['Offen'] || 0, color: 'bg-gray-500' },
                        ].map((item) => (
                          <div
                            key={item.label}
                            className="text-center p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                          >
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{item.value}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{item.label}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Calls Table */}
          <motion.div variants={itemVariants}>
            <Card variant="elevated" className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-purple-500" />
                    Letzte Calls
                  </div>
                  <Badge variant="info" size="sm">{recentCalls.length} Einträge</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {loading ? (
                  <div className="p-6">
                    <SkeletonTable />
                  </div>
                ) : recentCalls.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400">
                    <Phone className="w-12 h-12 mb-4 opacity-50" />
                    <p className="text-lg font-medium">Keine Calls vorhanden</p>
                    <p className="text-sm opacity-70">Calls werden hier angezeigt sobald Anrufe eingehen</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50/80 dark:bg-gray-800/50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Zeit</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Nummer</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Score</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Dauer</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Ergebnis</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                        <AnimatePresence>
                          {recentCalls.map((call, index) => (
                            <motion.tr
                              key={call.id}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: 20 }}
                              transition={{ delay: index * 0.05 }}
                              className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors"
                            >
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                                {formatDate(call.started_at)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                                {formatPhone(call.phone_number)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <Badge
                                  variant={
                                    call.lead_score === 'A'
                                      ? 'lead-a'
                                      : call.lead_score === 'B'
                                      ? 'lead-b'
                                      : call.lead_score === 'C'
                                      ? 'lead-c'
                                      : 'lead-n'
                                  }
                                  size="sm"
                                >
                                  {call.lead_score}
                                </Badge>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                                <div className="flex items-center gap-1">
                                  <Clock className="w-3.5 h-3.5" />
                                  {formatDuration(call.duration_seconds)}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span
                                  className={cn(
                                    'inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full',
                                    call.call_outcome === 'Termin gebucht'
                                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                      : call.call_outcome === 'Nicht interessiert'
                                      ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                                      : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                                  )}
                                >
                                  {call.call_outcome === 'Termin gebucht' && (
                                    <Calendar className="w-3 h-3" />
                                  )}
                                  {call.call_outcome}
                                </span>
                              </td>
                            </motion.tr>
                          ))}
                        </AnimatePresence>
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.main>
    </div>
  )
}
