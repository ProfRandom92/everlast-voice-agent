'use client'

import { useState, useEffect, useCallback } from 'react'

interface UseRealtimeDataOptions<T> {
  supabase: any
  table: string
  select?: string
  orderBy?: { column: string; ascending?: boolean }
  limit?: number
  filter?: { column: string; operator: string; value: any }
}

export function useRealtimeData<T>(options: UseRealtimeDataOptions<T>) {
  const { supabase, table, select = '*', orderBy, limit, filter } = options
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    if (!supabase) return

    try {
      setLoading(true)
      let query = supabase.from(table).select(select)

      if (filter) {
        query = query.filter(filter.column, filter.operator, filter.value)
      }

      if (orderBy) {
        query = query.order(orderBy.column, { ascending: orderBy.ascending ?? false })
      }

      if (limit) {
        query = query.limit(limit)
      }

      const { data: result, error: queryError } = await query

      if (queryError) throw queryError
      setData(result || [])
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'))
    } finally {
      setLoading(false)
    }
  }, [supabase, table, select, orderBy, limit, filter])

  useEffect(() => {
    if (!supabase) return

    fetchData()

    const channel = supabase
      .channel(`${table}-changes`)
      .on('postgres_changes', { event: '*', schema: 'public', table }, () => {
        fetchData()
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [fetchData, supabase, table])

  return { data, loading, error, refetch: fetchData }
}
