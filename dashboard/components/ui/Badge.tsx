'use client'

import { cn } from '@/lib/utils'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'lead-a' | 'lead-b' | 'lead-c' | 'lead-n'
  size?: 'sm' | 'md'
}

export function Badge({ className, variant = 'default', size = 'md', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-medium transition-colors',
        {
          'px-2 py-0.5 text-xs rounded-full': size === 'sm',
          'px-2.5 py-0.5 text-sm rounded-full': size === 'md',
        },
        {
          'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200':
            variant === 'default',
          'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300':
            variant === 'success',
          'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300':
            variant === 'warning',
          'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300':
            variant === 'danger',
          'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300':
            variant === 'info',
          'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300':
            variant === 'lead-a',
          'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300':
            variant === 'lead-b',
          'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300':
            variant === 'lead-c',
          'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300':
            variant === 'lead-n',
        },
        className
      )}
      {...props}
    />
  )
}
