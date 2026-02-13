import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12">
          <div className="flex items-start justify-between gap-4">
            <div className="w-28" />
            <div className="flex-1 text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-primary-700 mb-4">SANSA</h1>
              <p className="text-xl md:text-2xl text-gray-600">
                Self-administered Nutrition Screening and Assessment Tool
              </p>
            </div>
            <div className="w-28 flex justify-end">
              <Link
                to="/admin/login"
                className="px-4 py-2 rounded-lg border-2 border-primary-600 text-primary-700 hover:bg-primary-50 font-semibold"
              >
                Admin Login
              </Link>
            </div>
          </div>
        </header>

        {/* Main Navigation Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {/* แบบคัดกรองและประเมินภาวะโภชนาการ */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">👴👵</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              แบบคัดกรองและประเมินภาวะโภชนาการ
            </h2>
            <p className="text-gray-600">ด้วยตนเองสำหรับผู้สูงอายุในชุมชน</p>
          </Link>

          {/* บันทึกการกิน */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">📔</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">บันทึกการกิน</h2>
            <p className="text-gray-600">บันทึกอาหารและเครื่องดื่มที่รับประทาน</p>
          </Link>

          {/* ประเมินความพึงพอใจ */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">💻</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">ประเมินความพึงพอใจ</h2>
            <p className="text-gray-600">แบบสอบถามความพึงพอใจต่อระบบ</p>
          </Link>
        </div>

        {/* Info Section */}
        <div className="mt-16 max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8 border-2 border-primary-200">
          <h3 className="text-2xl font-semibold text-primary-800 mb-4">
            ยินดีต้อนรับสู่ระบบ SANSA
          </h3>
          <div className="space-y-4 text-gray-600">
            <p>
              ระบบนี้ออกแบบมาเพื่อช่วยประเมินภาวะโภชนาการผ่านแบบสอบถามคัดกรอง
              และแบบประเมินพฤติกรรมการบริโภคอาหาร
            </p>
            <p>
              <strong>สำหรับผู้เข้าร่วม:</strong> เริ่มการประเมินโดยคลิกที่
              "แบบคัดกรองและประเมินภาวะโภชนาการ" คุณสามารถใช้รหัสผู้เข้าร่วมเดิม
              หรือสร้างรหัสใหม่ได้
            </p>
            <p>
              <strong>สำหรับเจ้าหน้าที่:</strong> เข้าสู่ระบบผ่าน Admin Login ที่มุมขวาบน
              เพื่อเข้าถึงการจัดการข้อมูล ฟังก์ชันส่งออกข้อมูล และเครื่องมือบริหารจัดการ
            </p>
            <p>ข้อมูลทั้งหมดถูกเก็บรักษาเป็นความลับและใช้เพื่อการวิจัยเท่านั้น</p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500">
          <p>© 2026 SANSA Research System. All rights reserved.</p>
          <p className="mt-2 text-sm">Version 1.0.0</p>
        </footer>
      </div>
    </div>
  );
}
