import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { resultsAPI } from '../api/client'
import { Download } from 'lucide-react'
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
