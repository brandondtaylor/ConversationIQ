import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { testsAPI } from '../api/client'
import { Plus, Play, Trash2, Eye, Activity } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

function Tests() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: tests, isLoading } = useQuery({
    queryKey: ['tests'],
    queryFn: async () => {
      const response = await testsAPI.list()
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => testsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['tests'])
    },
  })

  const runMutation = useMutation({
    mutationFn: (id) => testsAPI.run(id),
    onSuccess: (_, testId) => {
      queryClient.invalidateQueries(['tests'])
      // Navigate to monitor page after starting test
      navigate(`/tests/${testId}/monitor`)
    },
  })

  if (isLoading) return <div>Loading tests...</div>

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700'
      case 'running': return 'bg-blue-100 text-blue-700'
      case 'failed': return 'bg-red-100 text-red-700'
      case 'ready': return 'bg-purple-100 text-purple-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Tests</h1>
        <Link to="/tests/create" className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Test
        </Link>
      </div>

      <div className="space-y-4">
        {tests?.map((test) => (
          <div key={test.id} className="card">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-lg">{test.name}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(test.status)}`}>
                    {test.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{test.description}</p>
                <div className="flex gap-6 text-sm text-gray-500">
                  <span>{test.agent_ids?.length || 0} agents</span>
                  <span>Created: {new Date(test.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex gap-2">
                {test.status === 'running' && (
                  <Link
                    to={`/tests/${test.id}/monitor`}
                    className="btn btn-primary text-sm flex items-center gap-2 animate-pulse"
                  >
                    <Activity className="w-4 h-4" />
                    Monitor
                  </Link>
                )}
                {test.status === 'completed' && (
                  <Link
                    to={`/tests/${test.id}/results`}
                    className="btn btn-secondary text-sm flex items-center gap-2"
                  >
                    <Eye className="w-4 h-4" />
                    Results
                  </Link>
                )}
                {(test.status === 'draft' || test.status === 'ready') && (
                  <button
                    onClick={() => {
                      if (confirm(`Run test "${test.name}"?`)) {
                        runMutation.mutate(test.id)
                      }
                    }}
                    disabled={runMutation.isPending}
                    className="btn btn-primary text-sm flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    {runMutation.isPending ? 'Starting...' : 'Run'}
                  </button>
                )}
                <Link to={`/tests/${test.id}`} className="btn btn-secondary text-sm">
                  Details
                </Link>
                <button
                  onClick={() => {
                    if (confirm(`Delete test "${test.name}"?`)) {
                      deleteMutation.mutate(test.id)
                    }
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {tests?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="mb-4">No tests yet</p>
          <Link to="/tests/create" className="btn btn-primary">
            Create Your First Test
          </Link>
        </div>
      )}
    </div>
  )
}

export default Tests
