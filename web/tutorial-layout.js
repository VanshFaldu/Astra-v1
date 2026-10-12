(function(root){
  function place(t,w,h,vw,vh){
    const m=12,g=14,clamp=(v,a,b)=>Math.max(a,Math.min(v,b));
    const x=clamp(t.left+(t.width-w)/2,m,vw-w-m),y=clamp(t.top+(t.height-h)/2,m,vh-h-m);
    for(const p of [{left:t.left-w-g,top:y},{left:t.right+g,top:y},{left:x,top:t.top-h-g},{left:x,top:t.bottom+g}]){
      if(p.left>=m&&p.top>=m&&p.left+w<=vw-m&&p.top+h<=vh-m)return {...p,docked:false};
    }
    return {left:vw-w-m,top:vh-h-m,docked:true};
  }
  root.tutorialPlacement=place;
  if(typeof module!=='undefined')module.exports=place;
})(globalThis);
