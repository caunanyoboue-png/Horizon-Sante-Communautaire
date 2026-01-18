import { Bell } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

export default function Header() {
  const { user } = useAuthStore()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Bonjour, {user?.first_name} 👋</h2>
          <p className="text-sm text-gray-500">{user?.location}</p>
        </div>

        <div className="flex items-center gap-4">
          <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {user?.avatar ? (
            <img
              src={user.avatar}
              alt={user.full_name}
              className="w-10 h-10 rounded-full object-cover"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-primary-600 font-medium">
                {user?.first_name?.charAt(0)}
                {user?.last_name?.charAt(0)}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
