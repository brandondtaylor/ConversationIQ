import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Activity, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react'

function TestMonitor() {
  const { testId } = useParams()
  const navigate = useNavigate()
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState('connecting')
  const [progress, setProgress] = useState(0)
  const [evaluationCount, setEvaluationCount] = useState(0)
  const wsRef = useRef(null)
  const logsEndRef = useRef(null)

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

  // WebSocket connection
  useEffect(() => {
    if (!testId) return

    const ws = new WebSocket(`ws://localhost:8000/ws/test/${testId}`)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      setStatus('connected')
      addLog('Connected to test monitor', 'info')

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
        } else if (data.type === 'error') {
          addLog(`Error: ${data.message}`, 'error')
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setStatus('error')
      addLog('WebSocket connection error', 'error')
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setStatus('disconnected')
      addLog('Disconnected from test monitor', 'info')

      if (ws.pingInterval) {
        clearInterval(ws.pingInterval)
      }
    }

    return () => {
      if (ws.pingInterval) {
        clearInterval(ws.pingInterval)
      }
      ws.close()
    }
  }, [testId])

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
          <div className="flex gap-4">
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
