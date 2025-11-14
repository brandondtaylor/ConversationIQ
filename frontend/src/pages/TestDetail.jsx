import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { testsAPI, analyticsAPI } from '../api/client'
import { Play, BarChart3, Activity, Users } from 'lucide-react'

function TestDetail() {
  const { id } = useParams()

  const { data: test, isLoading } = useQuery({
    queryKey: ['test', id],
    queryFn: async () => {
      const response = await testsAPI.get(id)
      return response.data
    },
  })

  const { data: questions } = useQuery({
    queryKey: ['test-questions', id],
    queryFn: async () => {
      const response = await testsAPI.getQuestions(id)
      return response.data
    },
  })

  // Fetch evaluations to check for focus group insights
  const { data: evaluations } = useQuery({
    queryKey: ['evaluations', id],
    queryFn: async () => {
      const response = await analyticsAPI.getTestEvaluations(id)
      return response.data
    },
    enabled: !!id && test?.status === 'completed'
  })

  // Find focus group evaluations
  const focusGroupEvaluations = evaluations?.filter(eval => eval.agent_id === 'focus_group') || []

  if (isLoading) return <div>Loading test details...</div>
  if (!test) return <div>Test not found</div>

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{test.name}</h1>
        <p className="text-gray-600">{test.description}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">Status</p>
          <p className="text-2xl font-bold capitalize mt-1">{test.status}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Agents</p>
          <p className="text-2xl font-bold mt-1">{test.agent_ids?.length || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Questions</p>
          <p className="text-2xl font-bold mt-1">{questions?.length || 0}</p>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="mb-8 flex flex-wrap gap-3">
        {test.status === 'running' && (
          <Link
            to={`/tests/${id}/monitor`}
            className="btn btn-primary flex items-center gap-2 animate-pulse"
          >
            <Activity className="w-4 h-4" />
            Monitor Test
          </Link>
        )}

        {test.status === 'completed' && (
          <>
            <Link
              to={`/tests/${id}/results`}
              className="btn btn-primary flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              View Results
            </Link>

            {focusGroupEvaluations.length > 0 && (
              <>
                {focusGroupEvaluations.map((evaluation, index) => (
                  <Link
                    key={evaluation.id}
                    to={`/focus-group-insights/${evaluation.id}`}
                    className="btn btn-secondary flex items-center gap-2"
                  >
                    <Users className="w-4 h-4" />
                    Focus Group Insights {focusGroupEvaluations.length > 1 ? `#${index + 1}` : ''}
                  </Link>
                ))}
              </>
            )}
          </>
        )}
      </div>

      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Task Context</h2>
        <p className="text-gray-700 whitespace-pre-wrap">{test.task_context}</p>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Questions</h2>
        {questions && questions.length > 0 ? (
          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={q.id} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <span className="font-mono text-sm text-gray-500">{i + 1}.</span>
                  <div className="flex-1">
                    <p className="text-gray-900">{q.text}</p>
                    {q.category && (
                      <span className="inline-block mt-2 px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded">
                        {q.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No questions loaded</p>
        )}
      </div>
    </div>
  )
}

export default TestDetail
