import { useNavigate } from 'react-router-dom'

export default function FacilitiesPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            Health Service Centers
          </h1>
          <p className="text-gray-600">
            Find nearby health facilities and services
          </p>
        </div>

        <div className="space-y-4 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-2">
              Central Community Health Center
            </h3>
            <p className="text-gray-600 mb-3">
              📍 123 Main Street, Bangkok 10100
            </p>
            <p className="text-gray-600 mb-3">
              📞 02-123-4567
            </p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              View on Map →
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-2">
              University Hospital Nutrition Clinic
            </h3>
            <p className="text-gray-600 mb-3">
              📍 456 University Ave, Bangkok 10120
            </p>
            <p className="text-gray-600 mb-3">
              📞 02-234-5678
            </p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              View on Map →
            </button>
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
