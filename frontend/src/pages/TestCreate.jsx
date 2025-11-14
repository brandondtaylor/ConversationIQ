import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { testsAPI, agentsAPI, apiConfigsAPI, questionsAPI } from '../api/client'
import { useNavigate } from 'react-router-dom'
import { Upload } from 'lucide-react'

function TestCreate() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    task_context: '',
    api_config_id: '',
    agent_ids: [],
    evaluation_mode: 'single_agent',
    questions: [],
  })

  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentsAPI.list()
      return response.data
    },
  })

  const { data: apiConfigs } = useQuery({
    queryKey: ['api-configs'],
    queryFn: async () => {
      const response = await apiConfigsAPI.list()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (data) => testsAPI.create(data),
    onSuccess: () => {
      navigate('/tests')
    },
  })

  const uploadMutation = useMutation({
    mutationFn: (file) => questionsAPI.upload(file),
    onSuccess: (response) => {
      setFormData({ ...formData, questions: response.data })
    },
  })

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const toggleAgent = (agentId) => {
    const newAgents = formData.agent_ids.includes(agentId)
      ? formData.agent_ids.filter(id => id !== agentId)
      : [...formData.agent_ids, agentId]
    setFormData({ ...formData, agent_ids: newAgents })
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Create Test</h1>

      <div className="max-w-3xl">
        {/* Step Indicator */}
        <div className="flex mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                s === step ? 'bg-primary-600 text-white' : s < step ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {s}
              </div>
              {s < 4 && <div className="flex-1 h-1 bg-gray-200 mx-2" />}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="card">
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
              <div>
                <label className="block text-sm font-medium mb-1">Test Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                  placeholder="Customer Support Evaluation"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description *</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  rows="3"
                  className="input"
                  placeholder="Describe what this test evaluates..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Task Context *</label>
                <textarea
                  value={formData.task_context}
                  onChange={(e) => setFormData({ ...formData, task_context: e.target.value })}
                  required
                  rows="3"
                  className="input"
                  placeholder="Provide context about what the chat API should accomplish..."
                />
              </div>
            </div>
          )}

          {/* Step 2: API Config */}
          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold mb-4">Select API Configuration</h2>
              <div className="space-y-2">
                {apiConfigs?.map((config) => (
                  <label key={config.id} className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="api_config"
                      value={config.id}
                      checked={formData.api_config_id === config.id}
                      onChange={(e) => setFormData({ ...formData, api_config_id: e.target.value })}
                      className="mr-3"
                    />
                    <div>
                      <p className="font-medium">{config.name}</p>
                      <p className="text-sm text-gray-500">{config.endpoint}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Select Agents */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-4">Select Agents</h2>
                <p className="text-sm text-gray-600 mb-4">Choose agents who will evaluate the responses</p>
                <div className="space-y-2">
                  {agents?.map((agent) => (
                    <label key={agent.id} className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={formData.agent_ids.includes(agent.id)}
                        onChange={() => toggleAgent(agent.id)}
                        className="mt-1 mr-3"
                      />
                      <div>
                        <p className="font-medium">{agent.name}</p>
                        <p className="text-sm text-gray-600">{agent.description}</p>
                        <div className="flex gap-1 mt-2">
                          {agent.expertise_areas?.slice(0, 3).map((area, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                              {area}
                            </span>
                          ))}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Evaluation Mode Selector */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-3">Evaluation Mode</h3>
                <p className="text-sm text-gray-600 mb-4">Choose how agents will evaluate the responses</p>
                <div className="space-y-3">
                  <label className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="evaluation_mode"
                      value="single_agent"
                      checked={formData.evaluation_mode === 'single_agent'}
                      onChange={(e) => setFormData({ ...formData, evaluation_mode: e.target.value })}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-medium">Single-Agent Evaluation</p>
                      <p className="text-sm text-gray-600">Each agent evaluates independently and provides individual feedback</p>
                    </div>
                  </label>

                  <label className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="evaluation_mode"
                      value="focus_group"
                      checked={formData.evaluation_mode === 'focus_group'}
                      onChange={(e) => setFormData({ ...formData, evaluation_mode: e.target.value })}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-medium">Focus Group Evaluation</p>
                      <p className="text-sm text-gray-600">Agents discuss together as a focus group using TinyTroupe's collaborative environment</p>
                    </div>
                  </label>

                  <label className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="evaluation_mode"
                      value="both"
                      checked={formData.evaluation_mode === 'both'}
                      onChange={(e) => setFormData({ ...formData, evaluation_mode: e.target.value })}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-medium">Both Single & Focus Group</p>
                      <p className="text-sm text-gray-600">Run both evaluation modes - get individual agent feedback AND collaborative group insights</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Upload Questions */}
          {step === 4 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold mb-4">Upload Questions</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <label className="btn btn-primary cursor-pointer">
                  <input
                    type="file"
                    accept=".json,.csv,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  {uploadMutation.isPending ? 'Uploading...' : 'Upload Questions File'}
                </label>
                <p className="text-sm text-gray-500 mt-2">JSON, CSV, or TXT format</p>
              </div>
              {formData.questions.length > 0 && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="font-medium text-green-700">✓ {formData.questions.length} questions loaded</p>
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t">
            <button
              type="button"
              onClick={() => step > 1 ? setStep(step - 1) : navigate('/tests')}
              className="btn btn-secondary"
            >
              {step === 1 ? 'Cancel' : 'Back'}
            </button>
            {step < 4 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                disabled={
                  (step === 1 && (!formData.name || !formData.description || !formData.task_context)) ||
                  (step === 2 && !formData.api_config_id) ||
                  (step === 3 && formData.agent_ids.length === 0)
                }
                className="btn btn-primary"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={createMutation.isPending || formData.questions.length === 0}
                className="btn btn-primary"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Test'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

export default TestCreate
