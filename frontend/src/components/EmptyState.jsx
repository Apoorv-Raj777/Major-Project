import { LucideIcon } from 'lucide-react'

export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="text-center py-12">
      <Icon className="mx-auto h-12 w-12 text-gray-300 mb-4" />
      <p className="text-lg font-medium text-gray-900">{title}</p>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
