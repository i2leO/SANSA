import { useParams, useNavigate } from 'react-router-dom'

export default function ResultPage() {
  const { visitId } = useParams()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">✅</div>
            <h1 className="text-3xl font-bold text-primary-700 mb-2">
              Assessment Complete
            </h1>
            <p className="text-gray-600">
              Thank you for completing the SANSA assessment
            </p>
          </div>

          <div className="bg-primary-50 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Your Results</h2>
            <div className="space-y-2">
              <p><strong>Screening Score:</strong> XX points</p>
              <p><strong>Dietary Score:</strong> XX points</p>
              <p><strong>Total Score:</strong> XX points</p>
              <p><strong>Classification:</strong> Normal Nutritional Status</p>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-6 mb-8">
            <h3 className="font-semibold mb-2">Recommendations</h3>
            <p className="text-gray-700">
              Based on your assessment, your nutritional status appears to be good. 
              Continue maintaining a balanced diet and healthy lifestyle.
            </p>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => navigate(`/satisfaction/${visitId}`)}
              className="flex-1 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Continue to Satisfaction Survey
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Return Home
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
