import apiClient from "@/lib/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

const foodDiarySchema = z.object({
  entry_date: z.string().min(1, "กรุณาเลือกวันที่"),
  entry_time: z.string().optional(),
  meal_type: z.enum([
    "breakfast",
    "morning_snack",
    "lunch",
    "afternoon_snack",
    "dinner",
    "before_bed",
    "other",
  ]),
  menu_name: z.string().min(1, "กรุณาระบุชื่อเมนู"),
  description: z.string().optional(),
  portion_description: z.string().optional(),
});

type FoodDiaryForm = z.infer<typeof foodDiarySchema>;

interface FoodDiaryEntry {
  id: number;
  entry_date: string;
  entry_time: string;
  meal_type: string;
  menu_name: string;
  description: string;
  portion_description: string;
  photos: Array<{
    id: number;
    file_path: string;
    original_filename: string;
  }>;
}

export default function FoodDiaryPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();
  const [entries, setEntries] = useState<FoodDiaryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [visitId, setVisitId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FoodDiaryForm>({
    resolver: zodResolver(foodDiarySchema),
    defaultValues: {
      entry_date: new Date().toISOString().split("T")[0],
      entry_time: new Date().toTimeString().slice(0, 5),
      meal_type: "breakfast",
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get respondent to find visit
        const respondentRes = await apiClient.get(`/respondents/${respondentCode}`);
        const respondent = respondentRes.data;

        // Get visits for this respondent
        const visitsRes = await apiClient.get(`/visits/respondent/${respondent.id}`);
        if (visitsRes.data.length > 0) {
          const latestVisit = visitsRes.data[0];
          setVisitId(latestVisit.id);

          // Get food diary entries (endpoint needs to be created)
          try {
            const entriesRes = await apiClient.get(`/food-diary/visit/${latestVisit.id}`);
            setEntries(entriesRes.data);
          } catch (err) {
            // No entries yet or endpoint doesn't exist
            setEntries([]);
          }
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("ไม่สามารถโหลดข้อมูลได้");
      } finally {
        setLoading(false);
      }
    };

    if (respondentCode) {
      fetchData();
    }
  }, [respondentCode]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const onSubmit = async (data: FoodDiaryForm) => {
    if (!visitId) {
      setError("ไม่พบข้อมูล visit กรุณาลองใหม่");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create food diary entry
      const entryRes = await apiClient.post("/food-diary", {
        visit_id: visitId,
        ...data,
      });

      const entryId = entryRes.data.id;

      // Upload photos if any
      if (selectedFiles.length > 0) {
        const formData = new FormData();
        selectedFiles.forEach((file) => {
          formData.append("files", file);
        });

        await apiClient.post(`/food-diary/${entryId}/photos`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      // Refresh entries
      const entriesRes = await apiClient.get(`/food-diary/visit/${visitId}`);
      setEntries(entriesRes.data);

      // Reset form
      reset();
      setSelectedFiles([]);
      setShowAddForm(false);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(errorMessage || "ไม่สามารถบันทึกข้อมูลได้");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (entryId: number) => {
    if (!confirm("ต้องการลบรายการนี้?")) return;

    try {
      await apiClient.delete(`/food-diary/${entryId}`);
      setEntries(entries.filter((e) => e.id !== entryId));
    } catch (err: unknown) {
      setError("ไม่สามารถลบรายการได้");
    }
  };

  const getMealTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      breakfast: "🌅 มื้อเช้า",
      morning_snack: "☕ ของว่างเช้า",
      lunch: "🍱 มื้อกลางวัน",
      afternoon_snack: "🍪 ของว่างบ่าย",
      dinner: "🌙 มื้อเย็น",
      before_bed: "🌃 ก่อนนอน",
      other: "🍽️ อื่นๆ",
    };
    return labels[type] || type;
  };

  if (loading && !showAddForm) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">⏳</div>
          <p className="text-xl text-gray-600">กำลังโหลดข้อมูล...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center">
              <span className="text-3xl">📔</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-800">บันทึกการกินอาหาร</h1>
              <p className="text-gray-600 mt-1">Food Diary - บันทึกอาหารประจำวัน</p>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-4 mt-4">
            <p className="text-gray-700">
              รหัสผู้เข้าร่วม:{" "}
              <span className="font-mono font-bold text-primary-600 text-xl">{respondentCode}</span>
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-5 bg-red-50 border-l-4 border-red-500 rounded-lg">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {/* Add Entry Button */}
        {!showAddForm && (
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <button
              onClick={() => setShowAddForm(true)}
              className="w-full py-4 bg-gradient-to-r from-primary-600 to-teal-600 text-white rounded-xl hover:from-primary-700 hover:to-teal-700 font-bold text-lg shadow-lg flex items-center justify-center gap-2"
            >
              <span className="text-2xl">➕</span>
              <span>เพิ่มรายการอาหารใหม่</span>
            </button>
          </div>
        )}

        {/* Add Entry Form */}
        {showAddForm && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-primary-700 mb-6 pb-3 border-b-2 border-primary-200">
              เพิ่มรายการอาหาร
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Date and Time */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-gray-800 font-bold mb-2">วันที่ *</label>
                  <input
                    type="date"
                    {...register("entry_date")}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                  />
                  {errors.entry_date && (
                    <p className="text-red-600 text-sm mt-1">{errors.entry_date.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-gray-800 font-bold mb-2">เวลา</label>
                  <input
                    type="time"
                    {...register("entry_time")}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Meal Type */}
              <div>
                <label className="block text-gray-800 font-bold mb-2">มื้ออาหาร *</label>
                <select
                  {...register("meal_type")}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                >
                  <option value="breakfast">🌅 มื้อเช้า</option>
                  <option value="morning_snack">☕ ของว่างเช้า</option>
                  <option value="lunch">🍱 มื้อกลางวัน</option>
                  <option value="afternoon_snack">🍪 ของว่างบ่าย</option>
                  <option value="dinner">🌙 มื้อเย็น</option>
                  <option value="before_bed">🌃 ก่อนนอน</option>
                  <option value="other">🍽️ อื่นๆ</option>
                </select>
              </div>

              {/* Menu Name */}
              <div>
                <label className="block text-gray-800 font-bold mb-2">ชื่อเมนู *</label>
                <input
                  type="text"
                  {...register("menu_name")}
                  placeholder="เช่น ข้าวผัดกะเพรา, ส้มตำ, ข้าวเหนียวมะม่วง"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                />
                {errors.menu_name && (
                  <p className="text-red-600 text-sm mt-1">{errors.menu_name.message}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-gray-800 font-bold mb-2">รายละเอียด</label>
                <textarea
                  {...register("description")}
                  rows={3}
                  placeholder="ระบุส่วนประกอบหรือวิธีการปรุง"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Portion */}
              <div>
                <label className="block text-gray-800 font-bold mb-2">ปริมาณ</label>
                <input
                  type="text"
                  {...register("portion_description")}
                  placeholder="เช่น 1 จาน, 2 ชาม, 5 ชิ้น"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Photo Upload */}
              <div>
                <label className="block text-gray-800 font-bold mb-2">รูปภาพอาหาร</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleFileChange}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                />
                {selectedFiles.length > 0 && (
                  <p className="text-sm text-gray-600 mt-2">
                    เลือกแล้ว {selectedFiles.length} ไฟล์
                  </p>
                )}
              </div>

              {/* Buttons */}
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false);
                    reset();
                    setSelectedFiles([]);
                  }}
                  className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-semibold"
                >
                  ยกเลิก
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-3 bg-gradient-to-r from-primary-600 to-teal-600 text-white rounded-xl hover:from-primary-700 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-400 font-semibold shadow-lg"
                >
                  {loading ? "กำลังบันทึก..." : "บันทึก"}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Entries List */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <h2 className="text-2xl font-bold text-primary-700 mb-6 pb-3 border-b-2 border-primary-200">
            รายการบันทึก ({entries.length} รายการ)
          </h2>

          {entries.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4">📝</div>
              <p className="text-lg">ยังไม่มีรายการบันทึก</p>
              <p className="text-sm">เริ่มบันทึกอาหารของคุณได้เลย</p>
            </div>
          ) : (
            <div className="space-y-4">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="border-2 border-gray-200 rounded-xl p-6 hover:border-primary-400 transition-all"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{getMealTypeLabel(entry.meal_type)}</span>
                        <h3 className="text-xl font-bold text-gray-800">{entry.menu_name}</h3>
                      </div>
                      <div className="text-sm text-gray-600 flex gap-4">
                        <span>📅 {new Date(entry.entry_date).toLocaleDateString("th-TH")}</span>
                        {entry.entry_time && <span>🕐 {entry.entry_time}</span>}
                        {entry.portion_description && <span>📏 {entry.portion_description}</span>}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(entry.id)}
                      className="text-red-600 hover:text-red-800 p-2"
                      title="ลบรายการ"
                    >
                      🗑️
                    </button>
                  </div>

                  {entry.description && <p className="text-gray-700 mb-4">{entry.description}</p>}

                  {entry.photos && entry.photos.length > 0 && (
                    <div className="flex gap-2 flex-wrap">
                      {entry.photos.map((photo) => (
                        <img
                          key={photo.id}
                          src={`${import.meta.env.VITE_API_URL}${photo.file_path}`}
                          alt={photo.original_filename}
                          className="w-24 h-24 object-cover rounded-lg border-2 border-gray-200 hover:border-primary-400 cursor-pointer"
                          onClick={() =>
                            window.open(
                              `${import.meta.env.VITE_API_URL}${photo.file_path}`,
                              "_blank"
                            )
                          }
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <button
            onClick={() => navigate("/")}
            className="w-full py-3 border-2 border-primary-600 text-primary-700 rounded-xl hover:bg-primary-50 font-bold text-lg"
          >
            ← กลับหน้าหลัก
          </button>
        </div>
      </div>
    </div>
  );
}
