/* Regresiones de notación y presentación detectadas en Carbon. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'), path=require('node:path');
const WEB=path.join(__dirname,'../src/ui/web');
const leer=nombre=>fs.readFileSync(path.join(WEB,nombre),'utf8');

test('intervalos y semillas representan el signo menos de PDF igual que el ASCII',()=>{
  for(const modulo of ['regla-falsa','newton-raphson','secante']){
    const {leerNumero}=require(path.join(WEB,modulo+'.js'));
    for(const [s,n] of [['−1.5',-1.5],['–3/2',-1.5],['1/−2',-.5],['−1e−3',-.001]])
      assert.equal(leerNumero(s),n,modulo+': '+s);
    assert.ok(!Number.isFinite(leerNumero('0,5')),modulo);
  }
});
