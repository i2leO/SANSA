import { Link } from 'react-router-dom';

const tiles = [
  { to: '/start?next=food-diary', icon: '📋', title: 'บันทึกการกิน', detail: 'บันทึกอาหารประจำวัน', color: '#fff7ed' },
  { to: '/knowledge', icon: '📖', title: 'ความรู้อาหาร', detail: 'เรียนรู้เรื่องโภชนาการ', color: '#ecfeff' },
  { to: '/start?next=satisfaction', icon: '⭐', title: 'ความพึงพอใจ', detail: 'ประเมินความพึงพอใจ', color: '#fff1f2' },
  { to: '/facilities', icon: '🏥', title: 'สถานบริการ', detail: 'ศูนย์บริการสาธารณสุข', color: '#f5f3ff' },
];

export default function HomePage() {
  return <div className="sansa-home min-h-screen">
    <header className="sansa-public-header">
      <Link to="/" className="flex items-center gap-3 text-2xl font-bold"><span className="sansa-brand-icon text-3xl" aria-hidden>ϟ</span>SANSA</Link>
      <Link to="/admin/login" className="font-semibold text-primary-700">ผู้ดูแลระบบ</Link>
    </header>
    <main className="mx-auto max-w-6xl px-5 pb-12">
      <section className="text-center py-10 md:py-12">
        <p className="inline-flex rounded-full bg-primary-50 px-5 py-2 text-sm font-semibold text-primary-700">🩺 ระบบคัดกรองภาวะโภชนาการ</p>
        <h1 className="mt-7 text-3xl md:text-5xl font-bold leading-relaxed">แบบคัดกรองและประเมิน<br /><span className="text-primary-600">ภาวะโภชนาการ</span></h1>
        <p className="mt-5 text-lg md:text-xl text-slate-500">ด้วยตนเองสำหรับผู้สูงอายุในชุมชน</p>
      </section>
      <section aria-label="ขั้นตอนการประเมิน" className="sansa-panel bg-gradient-to-br from-white to-primary-50 px-4 py-6 text-center">
        <h2 className="font-semibold text-primary-700 mb-5">ขั้นตอนการประเมิน</h2>
        <ol className="flex flex-wrap justify-center gap-3 md:gap-6">
          {['📝|ข้อมูลทั่วไป', '🍽️|SANSA', '📊|MNA', '⚖️|BIA', '⭐|พึงพอใจ', '📋|ผลลัพธ์'].map((step, index) => {
            const [icon, label] = step.split('|');
            return <li key={label} className="relative min-w-16 text-sm text-slate-500"><span aria-hidden className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-2xl">{icon}</span>{label}{index < 5 && <span aria-hidden className="hidden md:block absolute -right-4 top-3 text-primary-300 text-xl">›</span>}</li>;
          })}
        </ol>
      </section>
      <Link to="/start" className="sansa-banner my-7 flex items-center justify-between gap-4 p-7 md:p-10">
        <div className="relative"><h2 className="text-2xl md:text-3xl font-bold">เริ่มทำแบบคัดกรอง</h2><p className="mt-3 text-white/90 text-lg">ประเมินภาวะโภชนาการของคุณวันนี้</p></div>
        <span aria-hidden className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-white/20 text-3xl">→</span>
      </Link>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {tiles.map(tile => <Link key={tile.title} to={tile.to} className="sansa-panel sansa-tile p-5 md:p-7 text-center">
          <span aria-hidden style={{ background: tile.color }} className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl text-3xl">{tile.icon}</span>
          <h2 className="text-lg font-bold">{tile.title}</h2><p className="mt-2 text-sm text-slate-500">{tile.detail}</p>
        </Link>)}
      </div>
    </main>
  </div>;
}
