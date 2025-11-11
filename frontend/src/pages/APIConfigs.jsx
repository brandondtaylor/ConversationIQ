import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiConfigsAPI } from '../api/client'
import { Plus, Trash2, Check, X } from 'lucide-react'
import { useState } from 'react'

function APIConfigs() {
  const queryClient = useQueryClient()
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    endpoint: '',
    api_key: '',
  })

  const { data: configs, isLoading } = useQuery({
    queryKey: ['api-configs'],
    queryFn: async () => {
      const response = await apiConfigsAPI.list()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (data) => apiConfigsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['api-configs'])
      setShowDialog(false)
      setFormData({ name: '', endpoint: '', api_key: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => apiConfigsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['api-configs'])
    },
  })

  const testMutation = useMutation({
    mutationFn: (id) => apiConfigsAPI.test(id),
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div>Loading API configs...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">API Configurations</h1>
        <button
          onClick={() => setShowDialog(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add API Config
        </button>
      </div>

      {/* Create Dialog */}
      {showDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Add API Configuration</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                  placeholder="My Chat API"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Endpoint URL</label>
                <input
                  type="url"
                  value={formData.endpoint}
                  onChange={(e) => setFormData({ ...formData, endpoint: e.target.value })}
                  required
                  className="input"
                  placeholder="https://api.example.com/v1/chat"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">API Key</label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  required
                  className="input"
                  placeholder="sk-..."
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowDialog(false)}
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="btn btn-primary flex-1"
                >
                  {createMutation.isPending ? 'Adding...' : 'Add'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Configs List */}
      <div className="space-y-4">
        {configs?.map((config) => (
          <div key={config.id} className="card">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-1">{config.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{config.endpoint}</p>
                <p className="text-xs text-gray-400">
                  Created: {new Date(config.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => testMutation.mutate(config.id)}
                  disabled={testMutation.isPending}
                  className="btn btn-secondary text-sm"
                >
                  Test Connection
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Delete "${config.name}"?`)) {
                      deleteMutation.mutate(config.id)
                    }
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {testMutation.data && testMutation.variables === config.id && (
              <div className={`mt-3 p-3 rounded-lg flex items-center gap-2 ${
                testMutation.data.data.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                {testMutation.data.data.success ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                {testMutation.data.data.message}
              </div>
            )}
          </div>
        ))}
      </div>

      {configs?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="mb-4">No API configurations yet</p>
          <button onClick={() => setShowDialog(true)} className="btn btn-primary">
            Add Your First API Config
          </button>
        </div>
      )}
    </div>
  )
}

export default APIConfigs
