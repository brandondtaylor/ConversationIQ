import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { agentsAPI } from '../api/client'
import { useNavigate } from 'react-router-dom'

function AgentCreate() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    age: 35,
    occupation: '',
    education: '',
    personality_traits: '',
    expertise_areas: '',
  })

  const createMutation = useMutation({
    mutationFn: (data) => agentsAPI.create(data),
    onSuccess: () => {
      navigate('/agents')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    const agentData = {
      name: formData.name,
      description: formData.description,
      demographics: {
        age: parseInt(formData.age),
        occupation: formData.occupation,
        education: formData.education,
      },
      personality_traits: formData.personality_traits.split(',').map(t => t.trim()).filter(Boolean),
      expertise_areas: formData.expertise_areas.split(',').map(e => e.trim()).filter(Boolean),
      evaluation_criteria_weights: {},
    }

    createMutation.mutate(agentData)
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Create New Agent</h1>

      <div className="max-w-2xl">
        <form onSubmit={handleSubmit} className="card space-y-6">
          <div>
            <label className="block text-sm font-medium mb-1">Agent Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="input"
              placeholder="e.g., Tech-Savvy Professional"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows="3"
              className="input"
              placeholder="Describe the agent's background and perspective..."
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Age</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Occupation</label>
              <input
                type="text"
                name="occupation"
                value={formData.occupation}
                onChange={handleChange}
                className="input"
                placeholder="Software Engineer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Education</label>
              <input
                type="text"
                name="education"
                value={formData.education}
                onChange={handleChange}
                className="input"
                placeholder="Bachelor's"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Personality Traits (comma-separated)
            </label>
            <input
              type="text"
              name="personality_traits"
              value={formData.personality_traits}
              onChange={handleChange}
              className="input"
              placeholder="Analytical, Detail-oriented, Direct"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Expertise Areas (comma-separated)
            </label>
            <input
              type="text"
              name="expertise_areas"
              value={formData.expertise_areas}
              onChange={handleChange}
              className="input"
              placeholder="Technology, Programming, Problem-solving"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => navigate('/agents')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="btn btn-primary"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Agent'}
            </button>
          </div>

          {createMutation.isError && (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg">
              Error: {createMutation.error.message}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

export default AgentCreate
