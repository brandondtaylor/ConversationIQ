import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { analyticsAPI } from '../api/client'

function TrendChart({ testId, timeRangeDays = 7 }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['trend', testId, timeRangeDays],
    queryFn: async () => {
      const response = await analyticsAPI.getTrends(testId, {
        time_range_days: timeRangeDays
      })
      return response.data
    },
    enabled: !!testId
  })

  if (isLoading) {
    return <div className="animate-pulse bg-gray-200 h-64 rounded-lg"></div>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Failed to load trend data: {error.message}
      </div>
    )
  }

  if (!data || data.trend_data.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-600">
        No trend data available for the selected time range
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-blue-600 font-medium">Total Evaluations</p>
          <p className="text-2xl font-bold text-blue-900">{data.total_evaluations}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-green-600 font-medium">Average Rating</p>
          <p className="text-2xl font-bold text-green-900">
            {(
              data.trend_data.reduce((sum, d) => sum + (d.avg_rating || 0), 0) /
              data.trend_data.filter(d => d.avg_rating).length
            ).toFixed(2)}
            <span className="text-sm text-green-600">/10</span>
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-sm text-purple-600 font-medium">Avg Response Time</p>
          <p className="text-2xl font-bold text-purple-900">
            {(
              data.trend_data.reduce((sum, d) => sum + (d.avg_response_time || 0), 0) /
              data.trend_data.filter(d => d.avg_response_time).length
            ).toFixed(3)}
            <span className="text-sm text-purple-600">s</span>
          </p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Rating Trends Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.trend_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 10]} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="avg_rating"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Average Rating"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Response Time Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.trend_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="avg_response_time"
              stroke="#8b5cf6"
              strokeWidth={2}
              name="Avg Response Time (s)"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default TrendChart
