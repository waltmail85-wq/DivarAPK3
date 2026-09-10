from pathlib import Path

p = Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s = p.read_text()
start = s.index('    void parseSearch(){')
end = s.index('    String unquote(', start)
new = '''    void parseSearch(){String js="(function(){let out=new Set();document.querySelectorAll('[href]').forEach(x=>{let u=x.getAttribute('href')||x.href||'';if(u.includes('/v/')){try{u=new URL(u,location.href).href;}catch(e){}out.add(u.split('#')[0].split('?')[0]);}});let h=document.documentElement?document.documentElement.outerHTML:'';let re=/(?:https?:\\/\\/(?:www\\.)?divar\\.ir)?\\/v\\/[A-Za-z0-9_-]+/g,m;while((m=re.exec(h))!==null){let u=m[0].replace(/\\\\/g,'/');if(u.startsWith('/v/'))u='https://divar.ir'+u;out.add(u);}return JSON.stringify(Array.from(out).slice(0,60));})()";web.evaluateJavascript(js,val->{String s=unquote(val);Matcher m=Pattern.compile("(?:https?://(?:www\\.)?divar\\.ir)?/v/[A-Za-z0-9_-]+").matcher(s);while(m.find()&&links.size()<40){String u=m.group();if(u.startsWith("/v/"))u="https://divar.ir"+u;if(!links.contains(u))links.add(u);}if(links.isEmpty()){summary.setText("آگهی‌ها پیدا شدند ولی لینک جزئیات از صفحه خوانده نشد؛ در حال تلاش دوباره…");web.postDelayed(this::parseSearch,2500);return;}summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد…");running=true;processNext();});}\n'''
s = s[:start] + new + s[end:]
p.write_text(s)
