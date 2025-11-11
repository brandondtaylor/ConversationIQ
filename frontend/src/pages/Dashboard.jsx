import { useQuery } from '@tanstack/react-query'
import { dashboardAPI } from '../api/client'
import { Users, Settings, FileText, BarChart3 } from 'lucide-react'
import { Link } from 'react-router-dom'

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  )
}

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await dashboardAPI.getStats()
      return response.data
    },
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">
      <div className="text-gray-500">Loading dashboard...</div>
    </div>
  }

  if (error) {
    return <div className="card bg-red-50 text-red-700">
      Error loading dashboard: {error.message}
    </div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Agents"
          value={data.total_agents}
          icon={Users}
          color="bg-blue-500"
        />
        <StatCard
          title="API Configs"
          value={data.total_api_configs}
          icon={Settings}
          color="bg-green-500"
        />
        <StatCard
          title="Total Tests"
          value={data.total_tests}
          icon={FileText}
          color="bg-purple-500"
        />
        <StatCard
          title="Evaluations"
          value={data.total_evaluations}
          icon={BarChart3}
          color="bg-orange-500"
        />
      </div>

      {/* Tests by Status */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Tests by Status</h2>
        <div className="grid grid-cols-5 gap-4">
          {Object.entries(data.tests_by_status).map(([status, count]) => (
            <div key={status} className="text-center">
              <p className="text-2xl font-bold">{count}</p>
              <p className="text-sm text-gray-500 capitalize">{status}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Tests */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Tests</h2>
          <Link to="/tests" className="text-primary-600 hover:text-primary-700">
            View all
          </Link>
        </div>

        {data.recent_tests.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No tests yet</p>
        ) : (
          <div className="space-y-3">
            {data.recent_tests.map((test) => (
              <Link
                key={test.id}
                to={`/tests/${test.id}`}
                className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div>
                  <h3 className="font-medium">{test.name}</h3>
                  <p className="text-sm text-gray-500">
                    {test.agent_count} agents • {new Date(test.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  test.status === 'completed' ? 'bg-green-100 text-green-700' :
                  test.status === 'running' ? 'bg-blue-100 text-blue-700' :
                  test.status === 'failed' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {test.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/agents/create" className="card hover:shadow-md transition-shadow cursor-pointer">
          <h3 className="font-semibold mb-2">Create Agent</h3>
          <p className="text-sm text-gray-500">Add a new virtual agent persona</p>
        </Link>
        <Link to="/apis" className="card hover:shadow-md transition-shadow cursor-pointer">
          <h3 className="font-semibold mb-2">Configure API</h3>
          <p className="text-sm text-gray-500">Add a chat API endpoint</p>
        </Link>
        <Link to="/tests/create" className="card hover:shadow-md transition-shadow cursor-pointer">
          <h3 className="font-semibold mb-2">Create Test</h3>
          <p className="text-sm text-gray-500">Start evaluating responses</p>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard
