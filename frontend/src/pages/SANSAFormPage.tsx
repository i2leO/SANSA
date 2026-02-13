import apiClient from "@/lib/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

const sansaSchema = z.object({
  // Screening (Q1-Q4)
  q1_weight_change: z.string().optional(),
  q2_food_intake: z.string().optional(),
  q3_daily_activities: z.string().optional(),
  q4_chronic_disease: z.string().optional(),

  // Dietary (Q5-Q16)
  q5_meals_per_day: z.string().optional(),
  q6_portion_size: z.string().optional(),
  q7_food_texture: z.string().optional(),
  q8_rice_starch: z.string().optional(),
  q9_protein: z.string().optional(),
  q10_milk: z.string().optional(),
  q11_fruits: z.string().optional(),
  q12_vegetables: z.string().optional(),
  q13_water: z.string().optional(),
  q14_sweet_drinks: z.string().optional(),
  q15_cooking_method: z.string().optional(),
  q16_oil_coconut: z.string().optional(),
});

type SANSAForm = z.infer<typeof sansaSchema>;

export default function SANSAFormPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit } = useForm<SANSAForm>({
    resolver: zodResolver(sansaSchema),
  });

  const onSubmit = async (data: SANSAForm) => {
    setLoading(true);
    setError(null);

    try {
      // Step 1: Get respondent info by code
      const respondentResponse = await apiClient.get(`/respondents/${respondentCode}`);
      const respondent = respondentResponse.data;

      // Step 2: Get or use existing visit
      const visitsResponse = await apiClient.get(`/visits/respondent/${respondent.id}`);
      let visit;

      if (visitsResponse.data.length > 0) {
        // Use the latest visit
        visit = visitsResponse.data[0];
      } else {
        // Create new visit if none exists
        const visitResponse = await apiClient.post("/visits", {
          respondent_id: respondent.id,
          visit_number: 1,
          visit_date: new Date().toISOString().split("T")[0],
          visit_type: "baseline",
        });
        visit = visitResponse.data;
      }

      // Step 3: Submit SANSA response
      try {
        await apiClient.post("/sansa", {
          visit_id: visit.id,
          // Map form field names to match backend schema
          q1_weight_change: data.q1_weight_change,
          q2_food_intake: data.q2_food_intake,
          q3_daily_activities: data.q3_daily_activities,
          q4_chronic_disease: data.q4_chronic_disease,
          q5_meals_per_day: data.q5_meals_per_day,
          q6_portion_size: data.q6_portion_size,
          q7_food_texture: data.q7_food_texture,
          q8_rice_starch: data.q8_rice_starch,
          q9_protein: data.q9_protein,
          q10_milk: data.q10_milk,
          q11_fruits: data.q11_fruits,
          q12_vegetables: data.q12_vegetables,
          q13_water: data.q13_water,
          q14_sweet_drinks: data.q14_sweet_drinks,
          q15_cooking_method: data.q15_cooking_method,
          q16_oil_coconut: data.q16_oil_coconut,
        });
      } catch (err: unknown) {
        const apiError = err as { response?: { data?: { detail?: string } } };
        const detail = apiError.response?.data?.detail || "";
        const isDuplicate = detail.toLowerCase().includes("already exists");
        if (!isDuplicate) throw err;
      }

      // Continue to MNA assessment (respondent flow)
      navigate(`/mna/${visit.id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "ไม่สามารถบันทึกข้อมูลได้");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-600 rounded-2xl flex items-center justify-center">
              <span className="text-3xl">🥗</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-800">แบบประเมิน SANSA</h1>
              <p className="text-gray-600 mt-1">
                Self-administered Nutrition Screening and Assessment
              </p>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-4 mt-4">
            <p className="text-gray-700">
              รหัสผู้เข้าร่วม:{" "}
              <span className="font-mono font-bold text-green-600 text-xl">{respondentCode}</span>
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-5 bg-red-50 border-l-4 border-red-500 rounded-lg">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Screening Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-green-700 mb-6 pb-3 border-b-2 border-green-200">
              ส่วนที่ 1: คัดกรอง (Screening)
            </h2>

            {/* Q1: Weight Change */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                1. น้ำหนักตัวในช่วง 3 เดือนที่ผ่านมา
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ลดลง"
                    {...register("q1_weight_change")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ลดลง</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="คงเดิม"
                    {...register("q1_weight_change")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">คงเดิม</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="เพิ่มขึ้น"
                    {...register("q1_weight_change")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">เพิ่มขึ้น</span>
                </label>
              </div>
            </div>

            {/* Q2: Food Intake */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                2. การกินอาหารในช่วง 3 เดือนที่ผ่านมา
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="น้อยลง"
                    {...register("q2_food_intake")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">น้อยลง</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ปกติ"
                    {...register("q2_food_intake")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ปกติ</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="มากขึ้น"
                    {...register("q2_food_intake")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">มากขึ้น</span>
                </label>
              </div>
            </div>

            {/* Q3: Daily Activities */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                3. การทำกิจวัตรประจำวัน
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ไม่ได้"
                    {...register("q3_daily_activities")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ไม่ได้</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ช้ากว่าปกติ"
                    {...register("q3_daily_activities")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ช้ากว่าปกติ</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ปกติ"
                    {...register("q3_daily_activities")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ปกติ</span>
                </label>
              </div>
            </div>

            {/* Q4: Chronic Disease */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">4. โรคประจำตัว</label>
              <div className="space-y-2">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="ไม่มี"
                    {...register("q4_chronic_disease")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">ไม่มี</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
                  <input
                    type="radio"
                    value="มี"
                    {...register("q4_chronic_disease")}
                    className="w-5 h-5 text-green-600"
                  />
                  <span className="ml-3 text-gray-700">มี</span>
                </label>
              </div>
            </div>
          </div>

          {/* Dietary Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-green-700 mb-6 pb-3 border-b-2 border-green-200">
              ส่วนที่ 2: พฤติกรรมการบริโภคอาหาร (Dietary Behavior)
            </h2>

            {/* Q5: Meals per day */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                5. จำนวนมื้ออาหารต่อวัน
              </label>
              <select
                {...register("q5_meals_per_day")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl"
              >
                <option value="">เลือก...</option>
                <option value="แทบไม่ได้">แทบไม่ได้กินอาหาร</option>
                <option value="1">1 มื้อ</option>
                <option value="2">2 มื้อ</option>
                <option value="3">3 มื้อ</option>
                <option value=">3">มากกว่า 3 มื้อ</option>
              </select>
            </div>

            {/* Q6: Portion size */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                6. ปริมาณอาหารที่ทานต่อมื้อ (เปรียบเทียบกับปกติ)
              </label>
              <select
                {...register("q6_portion_size")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl"
              >
                <option value="">เลือก...</option>
                <option value="25">25%</option>
                <option value="50">50%</option>
                <option value="75">75%</option>
                <option value="100">100%</option>
                <option value=">100">มากกว่า 100%</option>
              </select>
            </div>

            {/* Q7: Food texture */}
            <div className="mb-8">
              <label className="block text-gray-800 font-bold text-lg mb-3">
                7. ลักษณะอาหารที่ทาน
              </label>
              <select
                {...register("q7_food_texture")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl"
              >
                <option value="">เลือก...</option>
                <option value="เหลว">เหลว (น้ำ นม)</option>
                <option value="อ่อน">อ่อน (โจ๊ก)</option>
                <option value="ปกติ">ปกติ (ข้าวสวย)</option>
              </select>
            </div>

            {/* Q8-Q16: Simplified inputs for remaining dietary questions */}
            {[
              {
                key: "q8_rice_starch",
                label: "8. ข้าว/แป้ง (กำปั้น/วัน)",
                options: ["0", "1-3", "4-6", "7-9", ">9"],
              },
              {
                key: "q9_protein",
                label: "9. เนื้อสัตว์ (ฝ่ามือ/วัน)",
                options: ["0", "1-2", "3-5", "6-8", ">8"],
              },
              { key: "q10_milk", label: "10. นม (แก้ว/วัน)", options: ["<1", "1", "2", "3", "4"] },
              {
                key: "q11_fruits",
                label: "11. ผลไม้ (กำปั้น/วัน)",
                options: ["0", "1-2", "3-5", "6-8", ">8"],
              },
              {
                key: "q12_vegetables",
                label: "12. ผัก (อึงมือ/วัน)",
                options: ["0", "0-1", "2-3", "4", ">4"],
              },
              {
                key: "q13_water",
                label: "13. น้ำเปล่า (แก้ว/วัน)",
                options: ["แทบไม่ได้", "1-3", "4-6", "7-8", ">8"],
              },
              {
                key: "q14_sweet_drinks",
                label: "14. เครื่องดื่มชนิด 3in1 (แก้ว/วัน)",
                options: ["0", "1", "2", "3", ">3"],
              },
              {
                key: "q15_cooking_method",
                label: "15. วิธีปรุงอาหาร",
                options: ["ต้ม/นึ่ง", "ผัด", "แกงกะทิ", "ทอด"],
              },
              {
                key: "q16_oil_coconut",
                label: "16. น้ำมัน/กะทิที่ใช้ (นิ้วหัวแม่มือ/วัน)",
                options: ["0", "1-2", "3-4", "5-6", ">6"],
              },
            ].map((q) => (
              <div key={q.key} className="mb-8">
                <label className="block text-gray-800 font-bold text-lg mb-3">{q.label}</label>
                <select
                  {...register(q.key as any)}
                  className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl"
                >
                  <option value="">เลือก...</option>
                  {q.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          {/* Buttons */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="flex-1 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-bold text-lg"
              >
                ← ย้อนกลับ
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl hover:from-green-700 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-400 font-bold text-lg shadow-lg"
              >
                {loading ? "กำลังบันทึก..." : "ดำเนินการต่อ →"}
              </button>
            </div>
          </div>
        </form>

        {/* Progress */}
        <div className="mt-8 text-center text-gray-600">
          <p className="text-sm">ขั้นตอนที่ 2 จาก 3 | แบบประเมิน SANSA</p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-green-600 to-teal-600 h-2 rounded-full"
              style={{ width: "66%" }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
