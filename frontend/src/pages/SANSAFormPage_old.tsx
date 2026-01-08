import { useParams, useNavigate } from 'react-router-dom'

export default function SANSAFormPage() {
  const { respondentCode } = useParams()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-6">
            SANSA Assessment
          </h1>
          <p className="text-gray-600 mb-8">
            Participant Code: {respondentCode}
          </p>

          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Screening Questions</h2>
              <p className="text-gray-600">
                This section contains 4 screening questions about your nutritional status.
                {/* Full SANSA screening form would be implemented here */}
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Dietary Behavior Assessment</h2>
              <p className="text-gray-600">
                This section contains 12 questions about your dietary habits.
                {/* Full SANSA dietary behavior form would be implemented here */}
              </p>
            </section>
          </div>

          <div className="mt-8 flex gap-4">
            <button
              onClick={() => navigate(-1)}
              className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={() => navigate(`/result/1`)}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Submit Assessment
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
