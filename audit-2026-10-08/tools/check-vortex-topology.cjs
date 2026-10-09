// Evaluate only the installed extension's pure installer functions on ZIP manifests.
// No Vortex API, staging mutation or deployment is performed.
const fs = require('fs');
const path = require('path').win32;
const crypto = require('crypto');
const [sourcePath, releasePath] = process.argv.slice(2);
if (!sourcePath || !releasePath) throw new Error('Usage: node check-vortex-topology.cjs installers.ts release-directory');
const source = fs.readFileSync(sourcePath, 'utf8');
const matrix = path.join('bin','config','r4game','user_config_matrix','pc');
function installer(name, next) {
  let code = source.slice(source.indexOf('export function '+name+'('), source.indexOf('export function '+next+'('));
  if (!code.startsWith('export function')) throw new Error('Installed installer source changed');
  code = code.replace('export function','function').replaceAll('files: string[]','files').replaceAll('destinationPath: string','destinationPath').replaceAll('const components: string[]','const components');
  return new Function('path','CONFIG_MATRIX_REL_PATH','PART_SUFFIX',code+'; return '+name)(path,matrix,'.part.txt');
}
const menu = installer('installMenuMod','testSupportedContent');
const top = installer('installTL','testDLCMod');
const manifest = JSON.parse(fs.readFileSync(path.join(releasePath,'validation.json'),'utf8'));
(async () => {
  const rows = [];
  for (const zip of manifest.archives) {
    const files = zip.files.map(x => x.path.replaceAll('/','\\'));
    const fn = files.some(x => x.startsWith(matrix+'\\')) ? menu : top;
    const result = await fn(files, 'Compatibility.installing');
    const copies = result.instructions.filter(x => x.type === 'copy');
    if (copies.length !== files.length || copies.some(x => x.source !== x.destination)) throw new Error('Unexpected install mapping: '+zip.name);
    rows.push({archive:zip.name,installer:fn===menu?'menu-root':'top-level',copies:copies.length,all_destinations_preserved:true,components:result.instructions.find(x=>x.key==='modComponents')?.value || []});
  }
  fs.writeFileSync(path.join(releasePath,'vortex-topology-validation.json'),JSON.stringify({source_sha256:crypto.createHash('sha256').update(source).digest('hex'),archives:rows,actual_import:false,actual_deployment:false},null,2));
  console.log(JSON.stringify(rows));
})().catch(e=>{console.error(e);process.exitCode=1;});
