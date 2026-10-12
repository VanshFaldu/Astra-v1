const assert=require('node:assert/strict');
const place=require('../web/tutorial-layout.js');
function check(t,w,h,vw,vh){
  const p=place(t,w,h,vw,vh);
  assert(p.left>=12&&p.top>=12&&p.left+w<=vw-12&&p.top+h<=vh-12);
  if(!p.docked)assert(p.left+w<=t.left||p.left>=t.right||p.top+h<=t.top||p.top>=t.bottom);
  return p;
}
assert.equal(check({left:800,right:1250,top:200,bottom:600,width:450,height:400},330,320,1440,900).docked,false);
assert.equal(check({left:30,right:400,top:100,bottom:600,width:370,height:500},330,320,1440,900).docked,false);
assert.equal(check({left:15,right:375,top:150,bottom:650,width:360,height:500},330,300,390,740).docked,true);
assert.equal(check({left:100,right:650,top:440,bottom:600,width:550,height:160},330,300,800,700).docked,false);
console.log('Tutorial positioning checks pass.');
