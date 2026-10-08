// Machine-specific paths are example inputs from the audited installation; adapt before reuse.
// Read a private copy of Vortex LevelDB; never open or modify the live database.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const dst=path.join(root,'private','vortex-state-copy');
fs.mkdirSync(dst,{recursive:true});
const src=path.join(process.env.APPDATA,'Vortex','state.v2');
const skipped=[];
for(const name of fs.readdirSync(src))if(name!=='LOCK'){
 try{fs.copyFileSync(path.join(src,name),path.join(dst,name));}catch(e){if(e.code==='EBUSY'||e.code==='EPERM'){skipped.push(name);continue;}throw e;}
}
fs.writeFileSync(path.join(root,'evidence','vortex-state-copy-limitations.json'),JSON.stringify({skipped,warning:'Live write-ahead log may be locked. Recovered SST state can be stale; deployment manifests remain authoritative for deployed ownership.'},null,2));
const b=require('C:/Program Files/Vortex/resources/app.asar.unpacked/node_modules/leveldown/prebuilds/win32-x64/node.napi.node');
const ctx=b.db_init();
function openCopy(){b.db_open(ctx,dst,{createIfMissing:false,errorIfExists:false},err=>{
 if(err)throw err;
 const it=b.iterator_init(ctx,{keys:true,values:true,keyAsBuffer:false,valueAsBuffer:false});
 const records=[];
 function next(){b.iterator_next(it,(err,arr,finished)=>{
  if(err)throw err;
  while(arr.length){const k=arr.pop(),v=arr.pop();records.push([String(k),String(v)]);}
  if(!finished)return next();
  b.iterator_end(it,()=>b.db_close(ctx,()=>{
   // Preserve only relevant branches, including profiles and configured staging.
   const profileIds=records.filter(([k,v])=>k.startsWith('persistent###profiles###')&&k.endsWith('###gameId')&&v==='"witcher3"').map(([k])=>k.split('###')[2]);
   const relevant=records.filter(([k,v])=>/witcher3/i.test(k+' '+v)||profileIds.some(id=>k.startsWith('persistent###profiles###'+id+'###')||k.startsWith('persistent###loadOrder###'+id+'###')));
   fs.writeFileSync(path.join(root,'evidence','vortex-state-relevant.json'),JSON.stringify(relevant,null,2));
   console.log(JSON.stringify({totalRecords:records.length,relevantRecords:relevant.length,keys:relevant.map(x=>x[0]).slice(0,30)}));
  }));
 });}next();
});}
if(skipped.length)b.repair_db(dst,err=>{if(err)throw err;openCopy();});else openCopy();
