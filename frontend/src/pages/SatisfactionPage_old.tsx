import { useNavigate, useParams } from "react-router-dom";

export default function SatisfactionPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 py-8" data-visit-id={visitId}>
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-6">Satisfaction Survey</h1>
          <p className="text-gray-600 mb-8">Please share your feedback about this assessment</p>

          <div className="space-y-6">
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Overall Satisfaction (1-5)
              </label>
              <select className="w-full px-4 py-3 border border-gray-300 rounded-lg">
                <option value="5">5 - Very Satisfied</option>
                <option value="4">4 - Satisfied</option>
                <option value="3">3 - Neutral</option>
                <option value="2">2 - Dissatisfied</option>
                <option value="1">1 - Very Dissatisfied</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Comments (Optional)</label>
              <textarea
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                placeholder="Please share any additional feedback..."
              />
            </div>
          </div>

          <div className="mt-8 flex gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Skip
            </button>
            <button
              onClick={() => navigate("/")}
              className="flex-1 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Submit Feedback
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
