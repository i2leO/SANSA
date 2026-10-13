import { useState } from 'react';
export default function useTableRows<T>(items:T[], controlledSearch?:string, onControlledSearch?:(value:string)=>void) {
  const [internalSearch,setInternalSearch]=useState('');
  const search=controlledSearch ?? internalSearch;
  const setSearch=onControlledSearch ?? setInternalSearch;
  const [page,setPage]=useState(0);
  const [size,setSize]=useState(10);
  const filtered=items.filter(item=>JSON.stringify(item).toLowerCase().includes(search.toLowerCase()));
  const actualPage=Math.min(page,Math.max(0,Math.ceil(filtered.length/size)-1));
  return {rows:filtered.slice(actualPage*size,(actualPage+1)*size),controls:{search,onSearch:(s:string)=>{setSearch(s);setPage(0);},page:actualPage,onPage:setPage,size,onSize:(n:number)=>{setSize(n);setPage(0);},total:filtered.length}};
}
