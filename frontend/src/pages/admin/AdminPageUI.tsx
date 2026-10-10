import AdminIcon from './AdminIcon';
import { ReactNode, useEffect, useState } from 'react';

export function AdminPageHeader({icon,title,description}:{icon:string;title:string;description:string}) {
  return <div className="sansa-page-heading"><span className="sansa-page-heading-icon"><AdminIcon name={icon} /></span><div><h1>{title}</h1><p>{description}</p></div></div>;
}

export function AdminCreatePanel({title,children,defaultOpen=false}:{title:string;children:ReactNode;defaultOpen?:boolean}) {
  const [open,setOpen]=useState(defaultOpen);
  useEffect(()=>{if(defaultOpen)setOpen(true);},[defaultOpen]);
  return <section className="sansa-panel sansa-create-panel">
    <button type="button" className="sansa-create-toggle" title={`${open?'ซ่อน':'เปิด'}แบบฟอร์ม${title}`} aria-expanded={open} onClick={()=>setOpen(value=>!value)}><span><b>＋</b>{title}</span><span aria-hidden>{open?'⌃':'⌄'}</span></button>
    {open && <div className="sansa-create-body">{children}</div>}
  </section>;
}

export function AdminListHeader({title,total,onRefresh}:{title:string;total:number;onRefresh:()=>void}) {
  return <div className="sansa-list-heading"><div><h2>{title}</h2><span>{total.toLocaleString()} รายการ</span></div><button type="button" title={`โหลด${title}ล่าสุดจากระบบ`} onClick={onRefresh} aria-label={`รีเฟรช${title}`}>↻ <span>รีเฟรช</span></button></div>;
}
