import { useNavigate, useParams } from "react-router-dom";

export default function FoodDiaryPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 py-8" data-respondent-code={respondentCode}>
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-6">Food Diary</h1>
          <p className="text-gray-600 mb-8">Track your daily meals and nutrition</p>

          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Recent Entries</h2>
            <div className="text-gray-500 text-center py-8">
              No diary entries yet. Add your first entry below.
            </div>
          </div>

          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Add New Entry</h3>
            <button className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
              + Add Meal
            </button>
          </div>

          <div className="mt-8">
            <button
              onClick={() => navigate("/")}
              className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
