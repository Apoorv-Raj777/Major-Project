import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message, onDismiss }) {
  return (
    <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded flex items-center">
      <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="ml-2 text-red-600 hover:text-red-700"
        >
          ✕
        </button>
      )}
    </div>
  )
}
