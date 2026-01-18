import { useQuery } from '@tanstack/react-query'
import { Users, Heart, Activity, AlertTriangle } from 'lucide-react'
import { patientsApi } from '../../api/patients'

export default function Dashboard() {
  const { data: patientStats } = useQuery({
    queryKey: ['patient-stats'],
    queryFn: patientsApi.getStats,
  })

  const stats = [
    {
      title: 'Total Patients',
      value: patientStats?.total || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Grossesses en cours',
      value: 24,
      icon: Heart,
      color: 'bg-pink-500',
    },
    {
      title: 'CPN ce mois',
      value: 156,
      icon: Activity,
      color: 'bg-green-500',
    },
    {
      title: 'Cas à risque',
      value: 8,
      icon: AlertTriangle,
      color: 'bg-red-500',
    },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Tableau de bord</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.title} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">{stat.title}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg text-white`}>
                <stat.icon size={24} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-4">Activité récente</h3>
          <div className="space-y-3">
            <p className="text-sm text-gray-500">Aucune activité récente</p>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Rappels CPN</h3>
          <div className="space-y-3">
            <p className="text-sm text-gray-500">Aucun rappel aujourd'hui</p>
          </div>
        </div>
      </div>
    </div>
  )
}
