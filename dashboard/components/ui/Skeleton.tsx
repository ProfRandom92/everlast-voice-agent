'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'card' | 'text' | 'chart'
}

export function Skeleton({ className, variant = 'default', ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800',
        {
          'h-4 w-full': variant === 'text',
          'h-32 w-full': variant === 'card',
          'h-64 w-full': variant === 'chart',
        },
        'bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-800 dark:via-gray-700 dark:to-gray-800',
        'bg-[length:200%_100%]',
        'animate-shimmer',
        className
      )}
      style={{
        animation: 'shimmer 2s infinite',
      }}
      {...props}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="w-1/3" />
        <Skeleton variant="text" className="w-10 h-10 rounded-xl" />
      </div>
      <Skeleton variant="text" className="w-1/2 h-8" />
      <Skeleton variant="text" className="w-2/3" />
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-6">
      <Skeleton variant="text" className="w-1/4 mb-6" />
      <Skeleton variant="chart" />
    </div>
  )
}

export function SkeletonTable() {
  return (
    <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <Skeleton variant="text" className="w-1/4" />
      </div>
      <div className="p-6 space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex gap-4">
            <Skeleton variant="text" className="w-32" />
            <Skeleton variant="text" className="w-32" />
            <Skeleton variant="text" className="w-20" />
            <Skeleton variant="text" className="w-24" />
          </div>
        ))}
      </div>
    </div>
  )
}
