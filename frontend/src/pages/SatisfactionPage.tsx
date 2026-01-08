import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import apiClient from "../lib/api";

export default function SatisfactionPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state for all 7 Likert questions + comments
  const [formData, setFormData] = useState({
    q1_clarity: "",
    q2_ease_of_use: "",
    q3_confidence: "",
    q4_presentation: "",
    q5_results_display: "",
    q6_usefulness: "",
    q7_overall_satisfaction: "",
    comments: "",
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Submit satisfaction survey
      await apiClient.post("/satisfaction", {
        visit_id: parseInt(visitId || "0"),
        ...formData,
      });

      // Navigate to results page
      navigate(`/visit/${visitId}/result`);
    } catch (err: any) {
      console.error("Error submitting satisfaction survey:", err);
      setError(
        err.response?.data?.detail || "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาลองใหม่อีกครั้ง"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = () => {
    // Skip satisfaction survey and go directly to results
    navigate(`/visit/${visitId}/result`);
  };

  const likertOptions = [
    { value: "5", label: "มากที่สุด", color: "text-green-700" },
    { value: "4", label: "มาก", color: "text-green-600" },
    { value: "3", label: "ปานกลาง", color: "text-yellow-600" },
    { value: "2", label: "น้อย", color: "text-orange-600" },
    { value: "1", label: "น้อยที่สุด", color: "text-red-600" },
  ];

  const questions = [
    {
      id: "q1_clarity",
      label: "1. ความชัดเจนของคำถาม",
      description: "คำถามในแบบประเมินมีความชัดเจน เข้าใจง่าย",
    },
    {
      id: "q2_ease_of_use",
      label: "2. ความสะดวกในการใช้งาน",
      description: "แบบประเมินใช้งานง่าย ไม่ซับซ้อน",
    },
    {
      id: "q3_confidence",
      label: "3. ความมั่นใจในการกรอกข้อมูล",
      description: "มั่นใจว่าข้อมูลที่กรอกถูกต้องและเหมาะสม",
    },
    {
      id: "q4_presentation",
      label: "4. รูปแบบการนำเสนอ",
      description: "รูปแบบการแสดงผลสวยงาม เป็นระเบียบ",
    },
    {
      id: "q5_results_display",
      label: "5. การแสดงผลลัพธ์",
      description: "ผลลัพธ์แสดงได้ชัดเจน เข้าใจง่าย",
    },
    {
      id: "q6_usefulness",
      label: "6. ประโยชน์ที่ได้รับ",
      description: "แบบประเมินมีประโยชน์ต่อการดูแลสุขภาพ",
    },
    {
      id: "q7_overall_satisfaction",
      label: "7. ความพึงพอใจโดยรวม",
      description: "พึงพอใจกับระบบประเมินโดยรวม",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-700">
              ขั้นตอนที่ 3 จาก 3: แบบประเมินความพึงพอใจ
            </span>
            <span className="text-sm font-medium text-purple-700">100%</span>
          </div>
          <div className="w-full bg-purple-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-500"
              style={{ width: "100%" }}
            />
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 mb-4">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">แบบประเมินความพึงพอใจ</h1>
            <p className="text-gray-600">กรุณาประเมินความพึงพอใจของท่านต่อแบบประเมินนี้</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Questions */}
            {questions.map((question, index) => (
              <div
                key={question.id}
                className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-100 hover:border-purple-300 transition-colors"
              >
                <label className="block mb-4">
                  <div className="font-semibold text-gray-800 text-lg mb-1">{question.label}</div>
                  <div className="text-sm text-gray-600">{question.description}</div>
                </label>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  {likertOptions.map((option) => (
                    <label
                      key={option.value}
                      className={`flex items-center justify-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        formData[question.id as keyof typeof formData] === option.value
                          ? "border-purple-500 bg-purple-100 shadow-md"
                          : "border-gray-200 bg-white hover:border-purple-300 hover:bg-purple-50"
                      }`}
                    >
                      <input
                        type="radio"
                        name={question.id}
                        value={option.value}
                        checked={formData[question.id as keyof typeof formData] === option.value}
                        onChange={(e) => handleChange(question.id, e.target.value)}
                        className="sr-only"
                      />
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${option.color}`}>{option.value}</div>
                        <div className="text-xs text-gray-600 mt-1">{option.label}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            {/* Comments Section */}
            <div className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-100">
              <label className="block mb-3">
                <div className="font-semibold text-gray-800 text-lg mb-1">
                  ข้อเสนอแนะเพิ่มเติม (ถ้ามี)
                </div>
                <div className="text-sm text-gray-600 mb-3">
                  กรุณาแสดงความคิดเห็นหรือข้อเสนอแนะเพิ่มเติม
                </div>
              </label>
              <textarea
                value={formData.comments}
                onChange={(e) => handleChange("comments", e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                placeholder="กรุณากรอกข้อเสนอแนะหรือความคิดเห็นของท่าน..."
              />
            </div>

            {/* Navigation Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <button
                type="button"
                onClick={handleSkip}
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                ข้ามขั้นตอนนี้
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    กำลังบันทึก...
                  </span>
                ) : (
                  "บันทึกและดูผลลัพธ์"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>ข้อมูลของท่านจะถูกเก็บเป็นความลับและใช้เพื่อการพัฒนาระบบเท่านั้น</p>
        </div>
      </div>
    </div>
  );
}
