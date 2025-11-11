import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentsAPI } from '../api/client'
import { Plus, Trash2, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'

function Agents() {
  const queryClient = useQueryClient()
  const [generateTask, setGenerateTask] = useState('')
  const [generateCount, setGenerateCount] = useState(3)
  const [showGenerateDialog, setShowGenerateDialog] = useState(false)

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentsAPI.list()
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => agentsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
    },
  })

  const generateMutation = useMutation({
    mutationFn: () => agentsAPI.generate({
      task_description: generateTask,
      num_agents: generateCount,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries(['agents'])
      setShowGenerateDialog(false)
      setGenerateTask('')
    },
  })

  if (isLoading) return <div>Loading agents...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Virtual Agents</h1>
        <div className="flex gap-3">
          <button
            onClick={() => setShowGenerateDialog(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Generate Agents
          </button>
          <Link to="/agents/create" className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Create Agent
          </Link>
        </div>
      </div>

      {/* Generate Dialog */}
      {showGenerateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Generate Agents</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Task Description</label>
                <textarea
                  value={generateTask}
                  onChange={(e) => setGenerateTask(e.target.value)}
                  placeholder="e.g., customer support for a SaaS product"
                  className="input"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Number of Agents</label>
                <input
                  type="number"
                  value={generateCount}
                  onChange={(e) => setGenerateCount(parseInt(e.target.value))}
                  min="1"
                  max="10"
                  className="input"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowGenerateDialog(false)}
                className="btn btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={() => generateMutation.mutate()}
                disabled={!generateTask || generateMutation.isPending}
                className="btn btn-primary flex-1"
              >
                {generateMutation.isPending ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents?.map((agent) => (
          <div key={agent.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-lg">{agent.name}</h3>
              <button
                onClick={() => {
                  if (confirm(`Delete agent "${agent.name}"?`)) {
                    deleteMutation.mutate(agent.id)
                  }
                }}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">{agent.description}</p>
            <div className="space-y-2">
              <div>
                <p className="text-xs font-medium text-gray-500">Occupation</p>
                <p className="text-sm">{agent.demographics?.occupation || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500">Expertise</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {agent.expertise_areas?.map((area, i) => (
                    <span key={i} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded">
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {agents?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="mb-4">No agents yet</p>
          <Link to="/agents/create" className="btn btn-primary">
            Create Your First Agent
          </Link>
        </div>
      )}
    </div>
  )
}

export default Agents
