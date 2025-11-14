import { useState } from 'react'
import { Plus, Trash2, Edit2, Save, X } from 'lucide-react'

function QuestionEditor({ questions = [], onChange }) {
  const [editingIndex, setEditingIndex] = useState(null)
  const [editForm, setEditForm] = useState({
    text: '',
    category: '',
    priority: 5,
    expected_tone: '',
    meta_data: {}
  })

  const handleAdd = () => {
    setEditingIndex(-1) // -1 means adding new
    setEditForm({
      text: '',
      category: '',
      priority: 5,
      expected_tone: '',
      meta_data: {}
    })
  }

  const handleEdit = (index) => {
    setEditingIndex(index)
    setEditForm({ ...questions[index] })
  }

  const handleSave = () => {
    if (editingIndex === -1) {
      // Adding new question
      onChange([...questions, editForm])
    } else {
      // Updating existing question
      const updated = [...questions]
      updated[editingIndex] = editForm
      onChange(updated)
    }
    setEditingIndex(null)
  }

  const handleDelete = (index) => {
    if (confirm('Are you sure you want to delete this question?')) {
      onChange(questions.filter((_, i) => i !== index))
    }
  }

  const handleCancel = () => {
    setEditingIndex(null)
  }

  return (
    <div className="space-y-4">
      {/* Questions List */}
      <div className="space-y-2">
        {questions.map((question, index) => (
          <div key={index}>
            {editingIndex === index ? (
              // Edit Mode
              <div className="border border-primary-300 rounded-lg p-4 bg-primary-50">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Question Text *</label>
                    <textarea
                      value={editForm.text}
                      onChange={(e) => setEditForm({ ...editForm, text: e.target.value })}
                      className="input"
                      rows="3"
                      placeholder="Enter the question..."
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">Category</label>
                      <input
                        type="text"
                        value={editForm.category}
                        onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                        className="input"
                        placeholder="e.g., Support, Sales"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">Expected Tone</label>
                      <input
                        type="text"
                        value={editForm.expected_tone}
                        onChange={(e) => setEditForm({ ...editForm, expected_tone: e.target.value })}
                        className="input"
                        placeholder="e.g., Professional, Friendly"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Priority (1-10)</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={editForm.priority}
                      onChange={(e) => setEditForm({ ...editForm, priority: parseInt(e.target.value) })}
                      className="input w-32"
                    />
                  </div>

                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={handleSave}
                      disabled={!editForm.text}
                      className="btn btn-primary flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      Save
                    </button>
                    <button
                      onClick={handleCancel}
                      className="btn btn-secondary flex items-center gap-2"
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              // View Mode
              <div className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{question.text}</p>
                    <div className="flex gap-3 mt-2 text-sm text-gray-600">
                      {question.category && (
                        <span className="px-2 py-1 bg-gray-100 rounded">
                          {question.category}
                        </span>
                      )}
                      {question.expected_tone && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                          Tone: {question.expected_tone}
                        </span>
                      )}
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                        Priority: {question.priority}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(index)}
                      className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(index)}
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add New Question Form */}
      {editingIndex === -1 && (
        <div className="border border-primary-300 rounded-lg p-4 bg-primary-50">
          <h3 className="font-semibold mb-3">Add New Question</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Question Text *</label>
              <textarea
                value={editForm.text}
                onChange={(e) => setEditForm({ ...editForm, text: e.target.value })}
                className="input"
                rows="3"
                placeholder="Enter the question..."
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <input
                  type="text"
                  value={editForm.category}
                  onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                  className="input"
                  placeholder="e.g., Support, Sales"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Expected Tone</label>
                <input
                  type="text"
                  value={editForm.expected_tone}
                  onChange={(e) => setEditForm({ ...editForm, expected_tone: e.target.value })}
                  className="input"
                  placeholder="e.g., Professional, Friendly"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Priority (1-10)</label>
              <input
                type="number"
                min="1"
                max="10"
                value={editForm.priority}
                onChange={(e) => setEditForm({ ...editForm, priority: parseInt(e.target.value) })}
                className="input w-32"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={handleSave}
                disabled={!editForm.text}
                className="btn btn-primary flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Add Question
              </button>
              <button
                onClick={handleCancel}
                className="btn btn-secondary flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Button */}
      {editingIndex === null && (
        <button
          onClick={handleAdd}
          className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-primary-500 hover:text-primary-600 hover:bg-primary-50 flex items-center justify-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Question
        </button>
      )}

      {/* Summary */}
      {questions.length > 0 && (
        <div className="bg-blue-50 p-3 rounded-lg text-sm text-blue-800">
          <strong>{questions.length}</strong> question{questions.length !== 1 ? 's' : ''} ready
        </div>
      )}
    </div>
  )
}

export default QuestionEditor
