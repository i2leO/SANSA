import { useNavigate } from 'react-router-dom'

export default function KnowledgePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            Knowledge Center
          </h1>
          <p className="text-gray-600">
            Learn about nutrition and healthy living
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">🥗</div>
            <h3 className="text-xl font-semibold mb-2">Healthy Eating</h3>
            <p className="text-gray-600">
              Tips for maintaining a balanced and nutritious diet
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">🏃</div>
            <h3 className="text-xl font-semibold mb-2">Physical Activity</h3>
            <p className="text-gray-600">
              The importance of regular exercise for health
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">💊</div>
            <h3 className="text-xl font-semibold mb-2">Supplements</h3>
            <p className="text-gray-600">
              Understanding vitamins and nutritional supplements
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Back to Home
        </button>
      </div>
    </div>
  )
}
