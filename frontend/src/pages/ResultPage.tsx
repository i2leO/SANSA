import apiClient from "@/lib/api";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

interface SANSAResult {
  id: number;
  screening_total: number;
  diet_total: number;
  total_score: number;
  result_level: string;
  completed_at: string;
}

export default function ResultPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState<SANSAResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const response = await apiClient.get(`/sansa/visit/${visitId}`);
        setResult(response.data);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || "ไม่สามารถโหลดผลการประเมินได้");
      } finally {
        setLoading(false);
      }
    };

    if (visitId) {
      fetchResult();
    }
  }, [visitId]);

  const getResultColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "from-green-500 to-teal-600";
      case "at-risk":
      case "เสี่ยง":
        return "from-yellow-500 to-orange-600";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "from-red-500 to-pink-600";
      default:
        return "from-gray-500 to-gray-600";
    }
  };

  const getResultEmoji = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "✅";
      case "at-risk":
      case "เสี่ยง":
        return "⚠️";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "⚠️";
      default:
        return "📊";
    }
  };

  const getRecommendation = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "สถานะโภชนาการของคุณอยู่ในเกณฑ์ดี ควรรักษาพฤติกรรมการกินอาหารและการใช้ชีวิตที่ดีต่อไป";
      case "at-risk":
      case "เสี่ยง":
        return "คุณมีความเสี่ยงต่อภาวะทุพโภชนาการ แนะนำให้ปรับปรุงพฤติกรรมการกินอาหาร และปรึกษานักโภชนาการหรือแพทย์";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "คุณอาจมีภาวะทุพโภชนาการ ควรปรึกษานักโภชนาการหรือแพทย์โดยเร็วเพื่อรับคำแนะนำที่เหมาะสม";
      default:
        return "ผลการประเมินของคุณได้รับการบันทึกเรียบร้อยแล้ว";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">⏳</div>
          <p className="text-xl text-gray-600">กำลังคำนวณผลการประเมิน...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center px-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
          <div className="text-6xl mb-4 text-center">❌</div>
          <h1 className="text-2xl font-bold text-red-600 mb-4 text-center">เกิดข้อผิดพลาด</h1>
          <p className="text-gray-600 mb-6 text-center">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="w-full py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 font-semibold"
          >
            กลับหน้าหลัก
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="text-center mb-6">
            <div className="text-7xl mb-4">{getResultEmoji(result.result_level)}</div>
            <h1 className="text-4xl font-bold text-primary-700 mb-2">ผลการประเมิน SANSA</h1>
            <p className="text-gray-600">ขอบคุณที่ทำแบบประเมินครบถ้วน</p>
          </div>
        </div>

        {/* Score Card */}
        <div
          className={`bg-gradient-to-br ${getResultColor(
            result.result_level
          )} rounded-2xl shadow-xl p-8 mb-6 text-white`}
        >
          <h2 className="text-3xl font-bold mb-6 text-center">คะแนนของคุณ</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
              <div className="text-5xl font-bold mb-2">{result.screening_total}</div>
              <div className="text-sm opacity-90">คะแนนคัดกรอง</div>
            </div>

            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
              <div className="text-5xl font-bold mb-2">{result.diet_total}</div>
              <div className="text-sm opacity-90">คะแนนพฤติกรรม</div>
            </div>

            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
              <div className="text-5xl font-bold mb-2">{result.total_score}</div>
              <div className="text-sm opacity-90">คะแนนรวม</div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 text-center">
            <div className="text-2xl font-bold text-gray-800 mb-2">
              สถานะโภชนาการ:{" "}
              <span
                className={`${getResultColor(result.result_level)} bg-clip-text text-transparent`}
              >
                {result.result_level}
              </span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-start gap-4">
            <div className="text-4xl">💡</div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-primary-700 mb-3">คำแนะนำ</h3>
              <p className="text-gray-700 text-lg leading-relaxed">
                {getRecommendation(result.result_level)}
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <button
              onClick={() => navigate(`/satisfaction/${visitId}`)}
              className="flex-1 py-4 bg-gradient-to-r from-primary-600 to-teal-600 text-white rounded-xl hover:from-primary-700 hover:to-teal-700 font-bold text-lg shadow-lg"
            >
              ดำเนินการต่อ: แบบสอบถามความพึงพอใจ →
            </button>
            <button
              onClick={() => navigate("/")}
              className="flex-1 py-4 border-2 border-primary-600 text-primary-700 rounded-xl hover:bg-primary-50 font-bold text-lg"
            >
              กลับหน้าหลัก
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-8 text-center text-gray-600">
          <p className="text-sm mb-2">ขั้นตอนที่ 3 จาก 4 | ผลการประเมิน</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-primary-600 to-teal-600 h-2 rounded-full transition-all"
              style={{ width: "75%" }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
