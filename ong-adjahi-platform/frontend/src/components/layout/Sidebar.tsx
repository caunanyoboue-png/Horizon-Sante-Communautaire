import { NavLink } from 'react-router-dom'
import { Home, Users, Heart, FileText, Settings, LogOut } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { authApi } from '../../api/auth'

export default function Sidebar() {
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    authApi.logout()
    logout()
  }

  const navItems = [
    { path: '/', label: 'Tableau de bord', icon: Home },
    { path: '/patients', label: 'Patients', icon: Users },
    { path: '/cpn', label: 'Suivi CPN', icon: Heart },
    { path: '/reports', label: 'Rapports', icon: FileText },
    { path: '/settings', label: 'Paramètres', icon: Settings },
  ]

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary-600">ONG ADJAHI</h1>
        <p className="text-sm text-gray-500 mt-1">Santé Communautaire</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="mb-3 p-3 bg-gray-50 rounded-lg">
          <p className="font-medium text-sm">{user?.full_name}</p>
          <p className="text-xs text-gray-500">{user?.role}</p>
        </div>
        
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut size={20} />
          <span>Déconnexion</span>
        </button>
      </div>
    </aside>
  )
}
