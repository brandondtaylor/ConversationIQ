import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Activity, CheckCircle, XCircle, Clock, TrendingUp, BarChart3, RefreshCw, Wifi, WifiOff, AlertCircle } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function TestMonitor() {
  const { testId } = useParams()
  const navigate = useNavigate()
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState('connecting')
  const [progress, setProgress] = useState(0)
  const [evaluationCount, setEvaluationCount] = useState(0)
  const [ratingData, setRatingData] = useState([])
  const [agentData, setAgentData] = useState({})
  const [connectionStatus, setConnectionStatus] = useState('connecting')
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const wsRef = useRef(null)
  const logsEndRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)

  // Fetch initial test data
  const { data: testData } = useQuery({
    queryKey: ['test', testId],
    queryFn: async () => {
      const response = await axios.get(`http://localhost:8000/api/tests/${testId}`)
      return response.data
    }
  })

  // Auto-scroll to bottom of logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // WebSocket connection with retry logic
  const connectWebSocket = useCallback(() => {
    if (!testId) return

    // Clear any existing reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    setConnectionStatus('connecting')
    const ws = new WebSocket(`ws://localhost:8000/ws/test/${testId}`)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnectionStatus('connected')
      setStatus('connected')
      reconnectAttemptsRef.current = 0
      setReconnectAttempts(0)
      addLog('✓ Connected to test monitor', 'success')

      // Send ping every 30 seconds to keep connection alive
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping')
        }
      }, 30000)

      ws.pingInterval = pingInterval
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'pong') {
          return // Ignore pong messages
        }

        if (data.type === 'progress') {
          addLog(data.message, 'progress')
          if (data.progress_percentage !== undefined) {
            setProgress(data.progress_percentage)
          }
        } else if (data.type === 'status') {
          setStatus(data.status)
          addLog(`Test status changed to: ${data.status}`, 'status')
        } else if (data.type === 'evaluation') {
          setEvaluationCount(prev => prev + 1)
          addLog('New evaluation completed', 'success')

          // Update rating data for line chart
          if (data.rating !== undefined) {
            setRatingData(prev => [
              ...prev,
              {
                index: prev.length + 1,
                rating: data.rating,
                time: new Date().toLocaleTimeString()
              }
            ])
          }

          // Update agent data for bar chart
          if (data.agent_id) {
            setAgentData(prev => ({
              ...prev,
              [data.agent_id]: (prev[data.agent_id] || 0) + 1
            }))
          }
        } else if (data.type === 'error') {
          addLog(`Error: ${data.message}`, 'error')
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
        addLog('Failed to parse server message', 'error')
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
      addLog('✗ WebSocket connection error', 'error')
    }

    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason)
      setConnectionStatus('disconnected')

      if (ws.pingInterval) {
        clearInterval(ws.pingInterval)
      }

      // Only attempt reconnection if test is still running and not manually closed
      if (status !== 'completed' && status !== 'failed' && event.code !== 1000) {
        const maxRetries = 10
        const attempt = reconnectAttemptsRef.current

        if (attempt < maxRetries) {
          // Exponential backoff: 2^attempt seconds, max 30 seconds
          const backoffDelay = Math.min(1000 * Math.pow(2, attempt), 30000)

          reconnectAttemptsRef.current += 1
          setReconnectAttempts(reconnectAttemptsRef.current)

          addLog(
            `Connection lost. Reconnecting in ${Math.round(backoffDelay / 1000)}s... (Attempt ${attempt + 1}/${maxRetries})`,
            'info'
          )

          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket()
          }, backoffDelay)
        } else {
          addLog('✗ Maximum reconnection attempts reached. Please refresh the page.', 'error')
          setConnectionStatus('failed')
        }
      } else {
        addLog('Disconnected from test monitor', 'info')
      }
    }
  }, [testId, status])

  // Initial WebSocket connection
  useEffect(() => {
    connectWebSocket()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        if (wsRef.current.pingInterval) {
          clearInterval(wsRef.current.pingInterval)
        }
        wsRef.current.close(1000, 'Component unmounting')
      }
    }
  }, [connectWebSocket])

  const addLog = (message, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, { message, level, timestamp }])
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
      case 'running':
        return <Activity className="w-5 h-5 text-blue-600 animate-pulse" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getLogColor = (level) => {
    switch (level) {
      case 'error':
        return 'text-red-600 bg-red-50'
      case 'success':
        return 'text-green-600 bg-green-50'
      case 'status':
        return 'text-blue-600 bg-blue-50'
      case 'progress':
        return 'text-purple-600 bg-purple-50'
      default:
        return 'text-gray-700 bg-gray-50'
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Test Monitor</h1>
        <button
          onClick={() => navigate('/tests')}
          className="btn btn-secondary"
        >
          Back to Tests
        </button>
      </div>

      {/* Test Info Card */}
      {testData && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">{testData.name}</h2>
          <p className="text-gray-600 mb-4">{testData.description}</p>
          <div className="flex gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                {status}
              </span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <TrendingUp className="w-5 h-5" />
              <span>{evaluationCount} evaluations completed</span>
            </div>
            <div className="flex items-center gap-2">
              {connectionStatus === 'connected' && (
                <>
                  <Wifi className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-green-700 font-medium">Connected</span>
                </>
              )}
              {connectionStatus === 'connecting' && (
                <>
                  <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />
                  <span className="text-sm text-blue-700 font-medium">Connecting...</span>
                </>
              )}
              {(connectionStatus === 'disconnected' || connectionStatus === 'error') && (
                <>
                  <WifiOff className="w-5 h-5 text-orange-600" />
                  <span className="text-sm text-orange-700 font-medium">
                    Disconnected {reconnectAttempts > 0 && `(Retry ${reconnectAttempts}/10)`}
                  </span>
                  <button
                    onClick={connectWebSocket}
                    className="ml-2 px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Reconnect
                  </button>
                </>
              )}
              {connectionStatus === 'failed' && (
                <>
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <span className="text-sm text-red-700 font-medium">Connection Failed</span>
                  <button
                    onClick={() => window.location.reload()}
                    className="ml-2 px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Refresh Page
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">Progress</h3>
          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              status === 'completed' ? 'bg-green-600' :
              status === 'failed' ? 'bg-red-600' :
              'bg-blue-600'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Real-time Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Rating Trend Chart */}
        {ratingData.length > 0 && (
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold">Rating Trend</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={ratingData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="index" label={{ value: 'Evaluation #', position: 'insideBottom', offset: -5 }} />
                <YAxis domain={[0, 10]} label={{ value: 'Rating', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Line type="monotone" dataKey="rating" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Evaluations Per Agent Chart */}
        {Object.keys(agentData).length > 0 && (
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold">Evaluations by Agent</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={Object.entries(agentData).map(([agent, count]) => ({ agent, count }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="agent" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#a855f7" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Live Logs */}
      <div className="card">
        <h3 className="font-semibold mb-4">Live Activity Log</h3>
        <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
          {logs.length === 0 ? (
            <p className="text-gray-400">Waiting for activity...</p>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={`mb-2 p-2 rounded ${getLogColor(log.level)}`}
              >
                <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                <span className="font-medium">{log.level.toUpperCase()}</span>:{' '}
                {log.message}
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Action Buttons */}
      {status === 'completed' && (
        <div className="mt-6 flex gap-4">
          <button
            onClick={() => navigate(`/tests/${testId}/results`)}
            className="btn btn-primary"
          >
            View Results
          </button>
          <button
            onClick={() => navigate('/tests')}
            className="btn btn-secondary"
          >
            Back to Tests
          </button>
        </div>
      )}
    </div>
  )
}

export default TestMonitor
