import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { resultsAPI, analyticsAPI } from '../api/client'
import { Download, Users, Star, Award, ThumbsUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import TrendChart from '../components/TrendChart'

function TestResults() {
  const { id } = useParams()

  const { data: results, isLoading } = useQuery({
    queryKey: ['test-results', id],
    queryFn: async () => {
      const response = await resultsAPI.get(id)
      return response.data
    },
  })

  // Fetch evaluations to find focus group evaluations
  const { data: evaluations } = useQuery({
    queryKey: ['evaluations', id],
    queryFn: async () => {
      const response = await analyticsAPI.getTestEvaluations(id)
      return response.data
    },
    enabled: !!id
  })

  // Find focus group evaluations
  const focusGroupEvaluations = evaluations?.filter(eval => eval.agent_id === 'focus_group') || []

  // Find ideal responses (top 3 highest rated evaluations)
  const idealResponses = evaluations
    ?.filter(eval => eval.rating && eval.rating >= 8) // Only ratings 8 or above
    ?.sort((a, b) => (b.rating || 0) - (a.rating || 0))
    ?.slice(0, 3) || []

  const handleExport = async (format) => {
    try {
      const response = await resultsAPI.export(id, format)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `results.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  if (isLoading) return <div>Loading results...</div>
  if (!results || results.error) return <div>No results available</div>

  const { overall } = results

  // Prepare chart data for ratings
  const ratingData = [
    { name: 'Average', value: overall.rating_stats?.average || 0 },
    { name: 'Median', value: overall.rating_stats?.median || 0 },
    { name: 'Min', value: overall.rating_stats?.min || 0 },
    { name: 'Max', value: overall.rating_stats?.max || 0 },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Test Results</h1>
        <div className="flex gap-2">
          <button onClick={() => handleExport('json')} className="btn btn-secondary text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            JSON
          </button>
          <button onClick={() => handleExport('csv')} className="btn btn-secondary text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            CSV
          </button>
          <button onClick={() => handleExport('report')} className="btn btn-primary text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            Full Report
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">Total Evaluations</p>
          <p className="text-3xl font-bold mt-1">{overall.total_evaluations}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Questions</p>
          <p className="text-3xl font-bold mt-1">{overall.unique_questions}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Agents</p>
          <p className="text-3xl font-bold mt-1">{overall.unique_agents}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Average Rating</p>
          <p className="text-3xl font-bold mt-1">{overall.rating_stats?.average?.toFixed(1) || 'N/A'}</p>
        </div>
      </div>

      {/* Focus Group Insights */}
      {focusGroupEvaluations.length > 0 && (
        <div className="card mb-8 bg-purple-50 border-purple-200">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-purple-900">Focus Group Evaluations Available</h3>
                <p className="text-sm text-purple-700 mt-1">
                  {focusGroupEvaluations.length} focus group evaluation{focusGroupEvaluations.length !== 1 ? 's' : ''} with detailed discussion insights
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {focusGroupEvaluations.map((evaluation, index) => (
                <Link
                  key={evaluation.id}
                  to={`/focus-group-insights/${evaluation.id}`}
                  className="btn btn-primary text-sm flex items-center gap-2"
                >
                  <Users className="w-4 h-4" />
                  View Insights {focusGroupEvaluations.length > 1 ? `#${index + 1}` : ''}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Rating Chart */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Rating Statistics</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ratingData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 10]} />
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Ideal Response Examples */}
      {idealResponses.length > 0 && (
        <div className="card mb-8 bg-gradient-to-br from-amber-50 to-yellow-50 border-amber-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Award className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-amber-900">Ideal Response Examples</h2>
              <p className="text-sm text-amber-700">Top-rated responses that exemplify quality criteria</p>
            </div>
          </div>

          <div className="space-y-4">
            {idealResponses.map((evaluation, index) => (
              <div key={evaluation.id} className="bg-white rounded-lg p-5 border-2 border-amber-200 shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1 px-3 py-1 bg-amber-100 rounded-full">
                      <Star className="w-4 h-4 text-amber-600 fill-amber-600" />
                      <span className="font-bold text-amber-900">{evaluation.rating?.toFixed(1)}</span>
                      <span className="text-xs text-amber-700">/10</span>
                    </div>
                    <span className="text-sm text-gray-600">by {evaluation.agent_id}</span>
                  </div>
                  {index === 0 && (
                    <span className="px-2 py-1 bg-gradient-to-r from-amber-400 to-yellow-400 text-amber-900 text-xs font-bold rounded-full">
                      BEST EXAMPLE
                    </span>
                  )}
                </div>

                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-600 mb-1">Response:</p>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg border border-gray-200">
                    {evaluation.api_response}
                  </p>
                </div>

                {evaluation.likes && evaluation.likes.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-green-700 mb-2 flex items-center gap-1">
                      <ThumbsUp className="w-4 h-4" />
                      What made this response excellent:
                    </p>
                    <div className="space-y-1">
                      {evaluation.likes.slice(0, 3).map((like, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="text-green-600 mt-1">•</span>
                          <span className="text-sm text-gray-700">{like}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {evaluation.agent_perspective && (
                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-600 italic">
                      "{evaluation.agent_perspective}"
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {idealResponses.length === 0 && (
            <p className="text-amber-700 text-center py-4">
              No responses with rating 8+ found yet. Keep testing to discover ideal examples!
            </p>
          )}
        </div>
      )}

      {/* Top Likes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Common Positive Feedback</h2>
          {overall.common_likes?.length > 0 ? (
            <div className="space-y-2">
              {overall.common_likes.slice(0, 5).map(([theme, count], i) => (
                <div key={i} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-gray-700">{theme}</span>
                  <span className="font-medium text-green-700">{count}×</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No feedback yet</p>
          )}
        </div>

        {/* Top Dislikes */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Common Concerns</h2>
          {overall.common_dislikes?.length > 0 ? (
            <div className="space-y-2">
              {overall.common_dislikes.slice(0, 5).map(([theme, count], i) => (
                <div key={i} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                  <span className="text-sm text-gray-700">{theme}</span>
                  <span className="font-medium text-red-700">{count}×</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No concerns yet</p>
          )}
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Trend Analysis</h2>
        <TrendChart testId={id} timeRangeDays={7} />
      </div>

      {/* Top Suggestions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Top Improvement Suggestions</h2>
        {overall.common_suggestions?.length > 0 ? (
          <div className="space-y-2">
            {overall.common_suggestions.slice(0, 5).map(([suggestion, count], i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <span className="font-mono text-sm text-gray-500 mt-0.5">{i + 1}.</span>
                <div className="flex-1">
                  <p className="text-sm text-gray-700">{suggestion}</p>
                </div>
                <span className="font-medium text-blue-700">{count}×</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No suggestions yet</p>
        )}
      </div>
    </div>
  )
}

export default TestResults
