import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '../api/client'
import { Users, MessageCircle, TrendingUp, Award, Star, ArrowRight, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

function FocusGroupInsights() {
  const { evaluationId } = useParams()
  const [showFullTranscript, setShowFullTranscript] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['focus-group-insights', evaluationId],
    queryFn: async () => {
      const response = await analyticsAPI.getFocusGroupInsights(evaluationId)
      return response.data
    }
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse bg-gray-200 h-64 rounded-lg"></div>
        <div className="animate-pulse bg-gray-200 h-64 rounded-lg"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-red-900 mb-2">Error Loading Insights</h2>
        <p className="text-red-700">{error.response?.data?.detail || error.message}</p>
      </div>
    )
  }

  const insights = data.insights

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Focus Group Insights</h1>

      {/* Consensus Points */}
      <div className="card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-green-100 rounded-lg">
            <TrendingUp className="w-6 h-6 text-green-600" />
          </div>
          <h2 className="text-xl font-semibold">Consensus Points</h2>
        </div>

        {insights.consensus_points && insights.consensus_points.length > 0 ? (
          <div className="space-y-3">
            {insights.consensus_points.map((point, index) => (
              <div key={index} className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    point.type === 'positive' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {point.type === 'positive' ? 'Positive Agreement' : 'Shared Concern'}
                  </span>
                  <span className="text-sm text-gray-600">
                    {Math.round(point.strength * 100)}% agreement
                  </span>
                </div>
                <p className="text-gray-900 mb-2">{point.description}</p>
                <div className="flex flex-wrap gap-2">
                  {point.supporting_agents.map((agent, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 text-sm rounded">
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No strong consensus points identified</p>
        )}
      </div>

      {/* Disagreement Points */}
      {insights.disagreement_points && insights.disagreement_points.length > 0 && (
        <div className="card mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-100 rounded-lg">
              <MessageCircle className="w-6 h-6 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold">Disagreements</h2>
          </div>

          <div className="space-y-3">
            {insights.disagreement_points.map((point, index) => (
              <div key={index} className="border rounded-lg p-4 bg-red-50">
                <p className="text-gray-900 font-medium mb-2">{point.description}</p>
                <div className="grid grid-cols-2 gap-4">
                  {point.low_raters && point.low_raters.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Lower ratings:</p>
                      <div className="flex flex-wrap gap-1">
                        {point.low_raters.map((agent, i) => (
                          <span key={i} className="px-2 py-1 bg-red-200 text-red-800 text-xs rounded">
                            {agent}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {point.high_raters && point.high_raters.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Higher ratings:</p>
                      <div className="flex flex-wrap gap-1">
                        {point.high_raters.map((agent, i) => (
                          <span key={i} className="px-2 py-1 bg-green-200 text-green-800 text-xs rounded">
                            {agent}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Influential Agents */}
      <div className="card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Award className="w-6 h-6 text-purple-600" />
          </div>
          <h2 className="text-xl font-semibold">Most Influential Agents</h2>
        </div>

        {insights.influential_agents && insights.influential_agents.length > 0 ? (
          <div className="space-y-2">
            {insights.influential_agents.map((agent, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                  <span className="font-medium text-gray-900">{agent.agent_name}</span>
                </div>
                <div className="flex gap-4 text-sm text-gray-600">
                  <span>{agent.speaking_turns} turns</span>
                  <span>Avg {agent.avg_message_length} chars</span>
                  <span className="font-semibold text-purple-600">
                    Score: {agent.influence_score.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No influence data available</p>
        )}
      </div>

      {/* Key Themes */}
      <div className="card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold">Key Discussion Themes</h2>
        </div>

        {insights.key_themes && insights.key_themes.length > 0 ? (
          <div className="grid grid-cols-2 gap-3">
            {insights.key_themes.map((theme, index) => (
              <div key={index} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 capitalize">{theme.theme}</span>
                  <span className="text-sm text-gray-600">{Math.round(theme.relevance * 100)}%</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {theme.mentioning_agents.map((agent, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No themes identified</p>
        )}
      </div>

      {/* Participation Balance */}
      {insights.participation_balance && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Participation Balance</h2>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Balance Score</span>
              <span className="text-lg font-semibold text-blue-600">
                {Math.round(insights.participation_balance.balance_score * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${insights.participation_balance.balance_score * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Higher is better - indicates balanced participation across all agents
            </p>
          </div>

          <div className="space-y-2">
            {insights.participation_balance.participation_by_agent.map((agent, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-900">{agent.agent}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${agent.percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">{agent.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Discussion Flow Visualization */}
      {insights.discussion_flow && insights.discussion_flow.sequence && (
        <div className="card mt-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold">Conversation Flow</h2>
              <p className="text-sm text-gray-600">
                Total turns: {insights.discussion_flow.total_turns}
              </p>
            </div>
            <button
              onClick={() => setShowFullTranscript(!showFullTranscript)}
              className="btn btn-secondary flex items-center gap-2"
            >
              {showFullTranscript ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  Show Less
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  Show Full Transcript
                </>
              )}
            </button>
          </div>

          {/* Visual Timeline */}
          <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Discussion Timeline</h3>
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
              {insights.discussion_flow.sequence.slice(0, Math.min(30, insights.discussion_flow.sequence.length)).map((turn, index) => (
                <div key={index} className="flex items-center gap-1 flex-shrink-0">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-medium shadow-sm"
                    style={{
                      backgroundColor: `hsl(${(turn.speaker.charCodeAt(0) * 137.5) % 360}, 70%, 85%)`,
                      color: `hsl(${(turn.speaker.charCodeAt(0) * 137.5) % 360}, 70%, 30%)`
                    }}
                    title={turn.speaker}
                  >
                    {turn.speaker.substring(0, 2).toUpperCase()}
                  </div>
                  {index < Math.min(29, insights.discussion_flow.sequence.length - 1) && (
                    <ArrowRight className="w-3 h-3 text-gray-400" />
                  )}
                </div>
              ))}
              {insights.discussion_flow.sequence.length > 30 && (
                <span className="text-sm text-gray-500 ml-2">+{insights.discussion_flow.sequence.length - 30} more</span>
              )}
            </div>
          </div>

          {/* Conversation Transcript */}
          <div className={`space-y-2 ${!showFullTranscript ? 'max-h-96' : 'max-h-[600px]'} overflow-y-auto`}>
            {(showFullTranscript
              ? insights.discussion_flow.sequence
              : insights.discussion_flow.sequence.slice(0, 20)
            ).map((turn, index) => {
              // Highlight key moments (consensus/disagreement points)
              const isConsensus = turn.message_preview && insights.consensus_points?.some(
                point => point.supporting_agents?.includes(turn.speaker)
              )
              const isDisagreement = turn.message_preview && insights.disagreement_points?.some(
                point => point.low_raters?.includes(turn.speaker) || point.high_raters?.includes(turn.speaker)
              )

              return (
                <div
                  key={index}
                  className={`flex gap-3 p-3 rounded-lg transition-colors ${
                    isConsensus ? 'bg-green-50 border border-green-200' :
                    isDisagreement ? 'bg-orange-50 border border-orange-200' :
                    'hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xs text-gray-400 w-8 flex-shrink-0">{index + 1}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm text-blue-600">{turn.speaker}</span>
                      {isConsensus && (
                        <span className="px-2 py-0.5 bg-green-200 text-green-800 text-xs rounded-full flex items-center gap-1">
                          <Star className="w-3 h-3" />
                          Consensus
                        </span>
                      )}
                      {isDisagreement && (
                        <span className="px-2 py-0.5 bg-orange-200 text-orange-800 text-xs rounded-full flex items-center gap-1">
                          <Lightbulb className="w-3 h-3" />
                          Key Point
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700">{turn.message_preview}</p>
                  </div>
                </div>
              )
            })}
            {!showFullTranscript && insights.discussion_flow.sequence.length > 20 && (
              <button
                onClick={() => setShowFullTranscript(true)}
                className="w-full py-3 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                Show {insights.discussion_flow.sequence.length - 20} more turns
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FocusGroupInsights
