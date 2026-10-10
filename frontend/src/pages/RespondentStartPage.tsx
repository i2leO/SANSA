import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrowserQRCodeReader, IScannerControls } from '@zxing/browser';
import apiClient from '@/lib/api';
import PublicLayout from '@/components/PublicLayout';
import { useAuthStore } from '@/stores/authStore';
import { User } from '@/types';

type QRLoginResponse =
  | { actor_type: 'participant'; access_token: string; respondent_code: string }
  | { actor_type: 'user'; access_token: string; refresh_token: string; user: User };

export default function RespondentStartPage() {
  const navigate=useNavigate();
  const staffLogin=useAuthStore(state=>state.login);
  const [value,setValue]=useState('');
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const [scan,setScan]=useState(false);
  const video=useRef<HTMLVideoElement>(null);
  const controls=useRef<IScannerControls>();
  const imageInput=useRef<HTMLInputElement>(null);
  const submitted=useRef(false);
  const login=useCallback(async(raw:string)=>{
    if(submitted.current)return;
    let secret=raw.trim();
    try { const url=new URL(secret); if(url.origin!==window.location.origin || !['/start','/login'].includes(url.pathname)) throw new Error(); secret=new URLSearchParams(url.hash.slice(1)).get('qr') || ''; } catch { if(secret.includes('://')){setError('กรุณาใช้ QR ของระบบ SANSA นี้');return;} }
    if(!/^[A-Za-z0-9_-]{43}$/.test(secret)){setError('QR ไม่ถูกต้อง กรุณาใช้ QR ที่ผู้ดูแลระบบออกให้');return;}
    submitted.current=true;setBusy(true);setError('');controls.current?.stop();setScan(false);
    try {const {data}=await apiClient.post<QRLoginResponse>('/participant-auth/login',{secret});if(data.actor_type==='user'){sessionStorage.removeItem('participantToken');sessionStorage.removeItem('participantCode');staffLogin(data.user,data.access_token,data.refresh_token);navigate('/admin/dashboard',{replace:true});return;}sessionStorage.setItem('participantToken',data.access_token);sessionStorage.setItem('participantCode',data.respondent_code);const next=new URLSearchParams(window.location.search).get('next'); if(next==='food-diary'){navigate(`/food-diary/${encodeURIComponent(data.respondent_code)}`,{replace:true});} else if(next==='satisfaction'){const r=await apiClient.get(`/respondents/${encodeURIComponent(data.respondent_code)}`);const v=await apiClient.get(`/visits/respondent/${r.data.id}`);navigate(v.data.length ? `/satisfaction/${v.data[0].id}` : `/general-info/${encodeURIComponent(data.respondent_code)}`,{replace:true});} else {navigate(`/participant/${encodeURIComponent(data.respondent_code)}`,{replace:true});}}
    catch {setError('QR ไม่ถูกต้องหรือถูกเปลี่ยนแล้ว กรุณาติดต่อผู้ดูแลระบบ');submitted.current=false;}
    finally {setBusy(false);setValue('');}
  },[navigate,staffLogin]);
  useEffect(()=>{const secret=new URLSearchParams(window.location.hash.slice(1)).get('qr');if(secret){window.history.replaceState(null,'',window.location.pathname+window.location.search);void login(secret);}},[login]);
  useEffect(()=>{
    if(!scan || !video.current)return;
    let cancelled=false;
    new BrowserQRCodeReader().decodeFromVideoDevice(undefined,video.current,(result)=>{if(result && !cancelled)void login(result.getText());}).then(c=>{if(cancelled)c.stop();else controls.current=c;}).catch(()=>{if(!cancelled){setError('เปิดกล้องไม่ได้ กรุณาอนุญาตกล้อง หรือวางลิงก์ QR ด้านล่าง');setScan(false);}});
    return()=>{cancelled=true;controls.current?.stop();};
  },[scan,login]);
  const decodeImage=async(event:React.ChangeEvent<HTMLInputElement>)=>{
    const file=event.target.files?.[0];
    if(!file)return;
    setBusy(true);setError('');
    const url=URL.createObjectURL(file);
    try {
      const reader=new BrowserQRCodeReader();
      let result;
      try {
        result=await reader.decodeFromImageUrl(url);
      } catch {
        const bitmap=await createImageBitmap(file,{imageOrientation:'from-image'});
        const maxSide=1800;
        const scale=Math.min(1,maxSide/Math.max(bitmap.width,bitmap.height));
        const canvas=document.createElement('canvas');
        canvas.width=Math.max(1,Math.round(bitmap.width*scale));
        canvas.height=Math.max(1,Math.round(bitmap.height*scale));
        const context=canvas.getContext('2d',{willReadFrequently:true});
        if(!context)throw new Error('canvas unavailable');
        context.fillStyle='#fff';context.fillRect(0,0,canvas.width,canvas.height);
        context.drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();
        result=reader.decodeFromCanvas(canvas);
      }
      await login(result.getText());
    } catch {
      setError('อ่าน QR จากรูปไม่ได้ กรุณาถ่ายให้เห็น QR ชัดเจนทั้งกรอบ หรือวางลิงก์ QR ด้านล่าง');
    } finally {
      URL.revokeObjectURL(url);event.target.value='';setBusy(false);
    }
  };
  return <PublicLayout title="เข้าสู่ระบบด้วย QR"><div className="max-w-xl mx-auto"><section className="text-center py-5"><span className="text-5xl" aria-hidden>👋</span><h2 className="text-3xl font-bold mt-5">เข้าสู่ระบบ SANSA</h2><p className="text-slate-500 mt-3">ผู้เข้าร่วม เจ้าหน้าที่ และผู้ดูแลระบบ ใช้ QR ส่วนตัวจากหน้านี้</p></section><div className="sansa-panel p-7 mt-5"><button className="sansa-primary-button w-full" disabled={busy} onClick={()=>setScan(!scan)}>{scan?'ปิดกล้อง':'สแกน QR ของฉัน'}</button>{scan && <video ref={video} className="w-full rounded-xl mt-5" autoPlay muted playsInline />}<input ref={imageInput} type="file" accept="image/*" capture="environment" className="hidden" onChange={decodeImage}/><button type="button" disabled={busy} onClick={()=>imageInput.current?.click()} className="mt-3 w-full rounded-xl border-2 border-primary-600 py-3 font-bold text-primary-700">📷 ถ่ายรูป / เลือกรูป QR</button><p className="mt-2 text-sm text-slate-500">ใช้ปุ่มนี้เมื่อทดสอบผ่านเครือข่ายภายในและ Chrome ไม่อนุญาตกล้องสด</p><form onSubmit={e=>{e.preventDefault();void login(value);}} className="mt-6"><label htmlFor="qr-link" className="block text-sm font-semibold mb-2">หรือวางลิงก์จาก QR</label><input id="qr-link" type="password" autoComplete="off" className="sansa-search" value={value} onChange={e=>setValue(e.target.value)} /><button disabled={busy || !value.trim()} className="sansa-primary-button w-full mt-4">{busy?'กำลังเข้าสู่ระบบ…':'เข้าสู่ระบบ'}</button></form>{error && <p role="alert" className="mt-4 text-red-700">{error}</p>}<p className="mt-6 text-sm text-slate-500">ยังไม่มี QR หรือทำหาย? ติดต่อผู้ดูแลระบบเพื่อออก QR ใหม่<br />กรุณาเก็บ QR เป็นความลับ สามารถใช้กับอุปกรณ์อื่นได้</p><button type="button" onClick={()=>navigate('/admin/login')} className="mt-5 w-full text-sm font-semibold text-slate-500 underline">เข้าสู่ระบบฉุกเฉินด้วยชื่อผู้ใช้และรหัสผ่าน</button></div></div></PublicLayout>;
}
