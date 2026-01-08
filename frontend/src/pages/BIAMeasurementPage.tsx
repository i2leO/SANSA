import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import apiClient from "../lib/api";

export default function BIAMeasurementPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state for BIA measurements
  const [formData, setFormData] = useState({
    age: "",
    sex: "male",
    waist_circumference_cm: "",
    weight_kg: "",
    height_cm: "",
    fat_mass_kg: "",
    body_fat_percentage: "",
    visceral_fat_kg: "",
    muscle_mass_kg: "",
    bone_mass_kg: "",
    water_percentage: "",
    metabolic_rate: "",
    weight_management: "",
    food_recommendation: "",
    staff_signature: "",
  });

  const [bmi, setBmi] = useState<number | null>(null);
  const [bmiCategory, setBmiCategory] = useState<string>("");

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Auto-calculate BMI when weight or height changes
    if (field === "weight_kg" || field === "height_cm") {
      const weight = field === "weight_kg" ? parseFloat(value) : parseFloat(formData.weight_kg);
      const height = field === "height_cm" ? parseFloat(value) : parseFloat(formData.height_cm);

      if (weight && height && height > 0) {
        const heightM = height / 100;
        const calculatedBmi = weight / (heightM * heightM);
        setBmi(calculatedBmi);

        // Determine BMI category (Asian-Pacific thresholds)
        if (calculatedBmi < 18.5) {
          setBmiCategory("ผอม (Underweight)");
        } else if (calculatedBmi < 23) {
          setBmiCategory("ปกติ (Normal)");
        } else if (calculatedBmi < 25) {
          setBmiCategory("เกิน (Overweight)");
        } else if (calculatedBmi < 30) {
          setBmiCategory("อ้วนระดับ 1 (Obese I)");
        } else {
          setBmiCategory("อ้วนระดับ 2 (Obese II)");
        }
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    // Validate required fields
    if (!formData.weight_kg || !formData.height_cm) {
      setError("กรุณากรอกน้ำหนักและส่วนสูง");
      setIsSubmitting(false);
      return;
    }

    try {
      // Submit BIA record
      await apiClient.post("/bia", {
        visit_id: parseInt(visitId || "0"),
        age: formData.age ? parseInt(formData.age) : null,
        sex: formData.sex,
        waist_circumference_cm: formData.waist_circumference_cm
          ? parseFloat(formData.waist_circumference_cm)
          : null,
        weight_kg: parseFloat(formData.weight_kg),
        height_cm: parseFloat(formData.height_cm),
        fat_mass_kg: formData.fat_mass_kg ? parseFloat(formData.fat_mass_kg) : null,
        body_fat_percentage: formData.body_fat_percentage
          ? parseFloat(formData.body_fat_percentage)
          : null,
        visceral_fat_kg: formData.visceral_fat_kg ? parseFloat(formData.visceral_fat_kg) : null,
        muscle_mass_kg: formData.muscle_mass_kg ? parseFloat(formData.muscle_mass_kg) : null,
        bone_mass_kg: formData.bone_mass_kg ? parseFloat(formData.bone_mass_kg) : null,
        water_percentage: formData.water_percentage ? parseFloat(formData.water_percentage) : null,
        metabolic_rate: formData.metabolic_rate ? parseInt(formData.metabolic_rate) : null,
        weight_management: formData.weight_management || null,
        food_recommendation: formData.food_recommendation || null,
        staff_signature: formData.staff_signature || null,
      });

      // Navigate back or to results
      navigate(`/visit/${visitId}/result`);
    } catch (err: any) {
      console.error("Error submitting BIA record:", err);
      setError(
        err.response?.data?.detail || "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาลองใหม่อีกครั้ง"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 mb-4">
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
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">การวัดองค์ประกอบร่างกาย (BIA)</h1>
          <p className="text-gray-600">Body Impedance Analysis Measurement</p>
          <p className="text-sm text-orange-600 mt-2">⚠️ เฉพาะเจ้าหน้าที่เท่านั้น (Staff Only)</p>
        </div>

        {/* Main Card */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8">
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
            {/* Section 1: Basic Information */}
            <div className="p-6 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl border-2 border-teal-100">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">ข้อมูลพื้นฐาน</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">อายุ (ปี)</label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => handleChange("age", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 65"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">เพศ</label>
                  <select
                    value={formData.sex}
                    onChange={(e) => handleChange("sex", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                  >
                    <option value="male">ชาย</option>
                    <option value="female">หญิง</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เส้นรอบเอว (cm)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.waist_circumference_cm}
                    onChange={(e) => handleChange("waist_circumference_cm", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 85.5"
                  />
                </div>
              </div>
            </div>

            {/* Section 2: Basic Measurements with BMI */}
            <div className="p-6 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl border-2 border-cyan-100">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">การวัดพื้นฐานและ BMI</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    น้ำหนัก (kg) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.weight_kg}
                    onChange={(e) => handleChange("weight_kg", e.target.value)}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 65.5"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ส่วนสูง (cm) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.height_cm}
                    onChange={(e) => handleChange("height_cm", e.target.value)}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 165.0"
                  />
                </div>
              </div>

              {/* BMI Display */}
              {bmi && (
                <div className="mt-4 p-4 bg-white rounded-lg border-2 border-teal-300">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">BMI (ดัชนีมวลกาย)</p>
                      <p className="text-2xl font-bold text-teal-700">{bmi.toFixed(2)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">หมวดหมู่</p>
                      <p className="text-lg font-semibold text-gray-800">{bmiCategory}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Section 3: Body Composition (BIA Results) */}
            <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-100">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                ผลการวิเคราะห์องค์ประกอบร่างกาย
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    มวลไขมัน (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.fat_mass_kg}
                    onChange={(e) => handleChange("fat_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 15.5"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เปอร์เซ็นต์ไขมัน (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.body_fat_percentage}
                    onChange={(e) => handleChange("body_fat_percentage", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 25.3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ไขมันในช่องท้อง (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.visceral_fat_kg}
                    onChange={(e) => handleChange("visceral_fat_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 2.5"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    มวลกล้ามเนื้อ (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.muscle_mass_kg}
                    onChange={(e) => handleChange("muscle_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 45.2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    มวลกระดูก (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.bone_mass_kg}
                    onChange={(e) => handleChange("bone_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 3.2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เปอร์เซ็นต์น้ำ (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.water_percentage}
                    onChange={(e) => handleChange("water_percentage", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 55.8"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    อัตราการเผาผลาญพลังงาน (kcal/day)
                  </label>
                  <input
                    type="number"
                    value={formData.metabolic_rate}
                    onChange={(e) => handleChange("metabolic_rate", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 1450"
                  />
                </div>
              </div>
            </div>

            {/* Section 4: Recommendations */}
            <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-100">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">คำแนะนำ</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    การจัดการน้ำหนัก
                  </label>
                  <select
                    value={formData.weight_management}
                    onChange={(e) => handleChange("weight_management", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                  >
                    <option value="">-- เลือก --</option>
                    <option value="maintain">คงไว้</option>
                    <option value="decrease">ลดน้ำหนัก</option>
                    <option value="increase">เพิ่มน้ำหนัก</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    คำแนะนำด้านอาหาร
                  </label>
                  <textarea
                    value={formData.food_recommendation}
                    onChange={(e) => handleChange("food_recommendation", e.target.value)}
                    rows={4}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="คำแนะนำด้านการรับประทานอาหารและโภชนาการ..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ลายเซ็นเจ้าหน้าที่
                  </label>
                  <input
                    type="text"
                    value={formData.staff_signature}
                    onChange={(e) => handleChange("staff_signature", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="ชื่อเจ้าหน้าที่ผู้บันทึกข้อมูล"
                  />
                </div>
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <button
                type="button"
                onClick={() => navigate(-1)}
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                ยกเลิก
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 py-4 px-6 bg-gradient-to-r from-teal-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-teal-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
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
                  "บันทึกข้อมูล"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            ข้อมูลจากเครื่องวัดองค์ประกอบร่างกาย (BIA)
            ใช้สำหรับประเมินภาวะโภชนาการและให้คำแนะนำด้านสุขภาพ
          </p>
        </div>
      </div>
    </div>
  );
}
