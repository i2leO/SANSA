import { useAuthStore } from "@/stores/authStore";
import { Navigate, useNavigate } from "react-router-dom";

function AdminDashboard() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-primary-600">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-primary-700">SANSA Admin Dashboard</h1>
            <p className="text-sm text-gray-600">ระบบจัดการข้อมูลและการประเมิน</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">ผู้ใช้งาน</p>
              <p className="font-semibold text-gray-800">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-500">
                {user?.role === "admin" ? "ผู้ดูแลระบบ" : "เจ้าหน้าที่"}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              ออกจากระบบ
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">ยินดีต้อนรับ!</h2>
          <p className="text-gray-600">เลือกเมนูด้านล่างเพื่อจัดการข้อมูลและการตั้งค่าระบบ</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
            <div className="text-4xl mb-3">👥</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800">ผู้เข้าร่วมการประเมิน</h3>
            <p className="text-gray-600 mb-4">จัดการข้อมูลผู้เข้าร่วมและผลการประเมิน</p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              ดูทั้งหมด →
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800">ส่งออกข้อมูล</h3>
            <p className="text-gray-600 mb-4">ส่งออกข้อมูลสำหรับวิเคราะห์ใน SPSS</p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              ส่งออกข้อมูล →
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
            <div className="text-4xl mb-3">📚</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800">เนื้อหาความรู้</h3>
            <p className="text-gray-600 mb-4">จัดการบทความและข้อมูลความรู้</p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              จัดการ →
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
            <div className="text-4xl mb-3">🏥</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800">ศูนย์บริการสุขภาพ</h3>
            <p className="text-gray-600 mb-4">จัดการข้อมูลศูนย์บริการสาธารณสุข</p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              จัดการ →
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
            <div className="text-4xl mb-3">⚙️</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800">กฎการให้คะแนน</h3>
            <p className="text-gray-600 mb-4">ตั้งค่าเกณฑ์การประเมินผล</p>
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              ตั้งค่า →
            </button>
          </div>

          {user?.role === "admin" && (
            <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-primary-200 hover:border-primary-400 transition-all">
              <div className="text-4xl mb-3">👨‍💼</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">จัดการผู้ใช้</h3>
              <p className="text-gray-600 mb-4">จัดการบัญชีเจ้าหน้าที่และสิทธิ์</p>
              <button className="text-primary-600 hover:text-primary-700 font-medium">
                จัดการผู้ใช้ →
              </button>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="mt-12">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">สถิติรวม</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6 text-center border-l-4 border-primary-600">
              <p className="text-3xl font-bold text-primary-700">0</p>
              <p className="text-gray-600 mt-2">ผู้เข้าร่วมทั้งหมด</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center border-l-4 border-green-600">
              <p className="text-3xl font-bold text-green-700">0</p>
              <p className="text-gray-600 mt-2">การประเมินวันนี้</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center border-l-4 border-blue-600">
              <p className="text-3xl font-bold text-blue-700">0</p>
              <p className="text-gray-600 mt-2">บทความความรู้</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center border-l-4 border-orange-600">
              <p className="text-3xl font-bold text-orange-700">0</p>
              <p className="text-gray-600 mt-2">ศูนย์บริการ</p>
            </div>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-12 text-center">
          <button
            onClick={() => navigate("/")}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            ← กลับไปหน้าหลัก
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
