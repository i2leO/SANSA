import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import apiClient from "../lib/api";
import { displayResearchValue } from '@/lib/researchLabels';

export default function BIAMeasurementPage({ staffMode = false, embedded = false, onSaved }: { staffMode?: boolean; embedded?: boolean; onSaved?: () => void }) {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [saved, setSaved] = useState(false);

  // Form state for BIA measurements
  const [formData, setFormData] = useState({
    waist_circumference_cm: "",
    weight_kg: "",
    height_cm: "",
    fat_mass_kg: "",
    body_fat_percentage: "",
    visceral_fat_level: "",
    muscle_mass_kg: "",
    bone_mass_kg: "",
    water_percentage: "",
    metabolic_rate: "",
    mac_cm: "",
    cc_cm: "",
  });

  const [bmi, setBmi] = useState<number | null>(null);
  const [bmiCategory, setBmiCategory] = useState<string>("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setLoadFailed(false);
    setError(null); setSaved(false);
    setBmi(null); setBmiCategory('');
    setFormData(previous => Object.fromEntries(Object.keys(previous).map(key => [key, ''])) as typeof previous);
    const load = async () => {
      try {
        const { data } = await apiClient.get(`/bia/visit/${visitId}`);
        if (!active) return;
        setFormData(previous => Object.fromEntries(Object.keys(previous).map(key => [key, data[key] == null ? '' : String(data[key])])) as typeof previous);
        setBmi(data.bmi == null ? null : Number(data.bmi));
        setBmiCategory(displayResearchValue('bmi_category', data.bmi_category));
      } catch (e: unknown) {
        if (!active) return;
        if ((e as { response?: { status?: number } }).response?.status !== 404) {
          setLoadFailed(true);
          setError('โหลดข้อมูลเดิมไม่สำเร็จ กรุณาเปิดหน้านี้ใหม่ก่อนบันทึก');
        }
      } finally { if (active) setLoading(false); }
    };
    void load();
    return () => { active = false; };
  }, [visitId]);

  const handleChange = (field: string, value: string) => {
    setSaved(false);
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Auto-calculate BMI when weight or height changes
    if (field === "weight_kg" || field === "height_cm") {
      const weight = field === "weight_kg" ? parseFloat(value) : parseFloat(formData.weight_kg);
      const height = field === "height_cm" ? parseFloat(value) : parseFloat(formData.height_cm);

      if (weight && height && height > 0) {
        const heightM = height / 100;
        const calculatedBmi = weight / (heightM * heightM);
        setBmi(calculatedBmi);

        setBmiCategory('จะแสดงหลังบันทึก');
      } else { setBmi(null); setBmiCategory(''); }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || loadFailed || isSubmitting) return;
    setError(null);
    setIsSubmitting(true);

    const requiredFields = Object.entries(formData).filter(([, value]) => value.trim() === "");
    if (requiredFields.length > 0) {
      setError("กรุณากรอกข้อมูล BIA และสัดส่วนร่างกายให้ครบทุกช่อง");
      setIsSubmitting(false);
      return;
    }

    try {
      // Submit BIA record
      const response = await apiClient.request({
        method: 'put',
        url: `/bia/visit/${visitId}/staff`,
        data: {
        waist_circumference_cm: parseFloat(formData.waist_circumference_cm),
        weight_kg: parseFloat(formData.weight_kg),
        height_cm: parseFloat(formData.height_cm),
        fat_mass_kg: parseFloat(formData.fat_mass_kg),
        body_fat_percentage: parseFloat(formData.body_fat_percentage),
        visceral_fat_level: parseFloat(formData.visceral_fat_level),
        muscle_mass_kg: parseFloat(formData.muscle_mass_kg),
        bone_mass_kg: parseFloat(formData.bone_mass_kg),
        water_percentage: parseFloat(formData.water_percentage),
        metabolic_rate: parseInt(formData.metabolic_rate),
        mac_cm: parseFloat(formData.mac_cm),
        cc_cm: parseFloat(formData.cc_cm),
        },
      });

      // Continue to satisfaction survey
      setBmi(response.data.bmi == null ? null : Number(response.data.bmi));
      setBmiCategory(displayResearchValue('bmi_category', response.data.bmi_category));
      setSaved(true);
      if (embedded) onSaved?.();
      else navigate(staffMode ? `/admin/results/${visitId}` : `/satisfaction/${visitId}`);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบค่าที่กรอกแล้วลองใหม่อีกครั้ง");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <p className="p-8">กำลังโหลดข้อมูลเดิม...</p>;
  if (loadFailed) return <p role="alert" className="p-8 text-red-700">{error}</p>;

  return (
    <div className={embedded ? '' : 'min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50 py-8'}>
      {saved && <p role="status" className="my-3 text-emerald-700">บันทึก BIA แล้ว</p>}
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

              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เส้นรอบเอว (cm) <span className="text-red-600">*</span>
                  </label>
                  <img className="sansa-question-image" src="/question-images/wc_cm.jpg" alt="ภาพประกอบวิธีวัดเส้นรอบเอว" loading="lazy" />
                  <input
                    type="number"
                    required
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
                    มวลไขมัน (kg) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={formData.fat_mass_kg}
                    onChange={(e) => handleChange("fat_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 15.5"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เปอร์เซ็นต์ไขมัน (%) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={formData.body_fat_percentage}
                    onChange={(e) => handleChange("body_fat_percentage", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 25.3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">ระดับไขมันในช่องท้อง <span className="text-red-600">*</span></label>
                  <input type="number" required step="0.1" value={formData.visceral_fat_level} onChange={(e) => handleChange("visceral_fat_level", e.target.value)} className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200" placeholder="เช่น 8" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    มวลกล้ามเนื้อ (kg) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={formData.muscle_mass_kg}
                    onChange={(e) => handleChange("muscle_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 45.2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    มวลกระดูก (kg) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={formData.bone_mass_kg}
                    onChange={(e) => handleChange("bone_mass_kg", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 3.2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    เปอร์เซ็นต์น้ำ (%) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={formData.water_percentage}
                    onChange={(e) => handleChange("water_percentage", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 55.8"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    อัตราการเผาผลาญพลังงาน (kcal/day) <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    value={formData.metabolic_rate}
                    onChange={(e) => handleChange("metabolic_rate", e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    placeholder="เช่น 1450"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">เส้นรอบวงแขน (MAC) (ซม.) <span className="text-red-600">*</span></label>
                  <input type="number" required step="0.1" value={formData.mac_cm} onChange={(e) => handleChange("mac_cm", e.target.value)} className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200" placeholder="เช่น 24.5" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">เส้นรอบวงน่อง (CC) (ซม.) <span className="text-red-600">*</span></label>
                  <input type="number" required step="0.1" value={formData.cc_cm} onChange={(e) => handleChange("cc_cm", e.target.value)} className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200" placeholder="เช่น 32.0" />
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
