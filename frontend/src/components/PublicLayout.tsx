import { ReactNode } from 'react';
import { Link } from 'react-router-dom';
export default function PublicLayout({title,children}:{title:string;children:ReactNode}) {
  const participantCode=sessionStorage.getItem('participantCode');
  const home=participantCode?`/participant/${encodeURIComponent(participantCode)}`:'/';
  return <div className="sansa-public-page min-h-screen"><header className="sansa-public-header"><Link to={home} className="text-primary-700 font-semibold">← หน้าหลัก</Link><h1 className="font-bold text-lg">{title}</h1><span className="hidden sm:block text-primary-600 font-bold">SANSA</span></header><main className="max-w-6xl mx-auto px-5 py-8">{children}</main></div>;
}
