import { FileText } from 'lucide-react'

function QuestionPreview({ questions = [] }) {
  if (questions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileText className="w-12 h-12 mx-auto mb-2 text-gray-400" />
        <p>No questions to preview</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Question Preview</h3>
        <span className="text-sm text-gray-600">{questions.length} questions</span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {questions.map((question, index) => (
          <div key={index} className="border rounded-lg p-4 bg-white">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold text-sm">
                {index + 1}
              </div>
              <div className="flex-1">
                <p className="text-gray-900 mb-2">{question.text}</p>
                <div className="flex flex-wrap gap-2">
                  {question.category && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {question.category}
                    </span>
                  )}
                  {question.expected_tone && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      Tone: {question.expected_tone}
                    </span>
                  )}
                  {question.priority && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                      Priority: {question.priority}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default QuestionPreview
