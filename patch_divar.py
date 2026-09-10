from pathlib import Path

p = Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s = p.read_text()
start = s.index('    void parseSearch(){')
end = s.index('    String unquote(', start)
new = '''    void parseSearch(){String js="(function(){let a=[...document.querySelectorAll('[href]')].map(x=>x.getAttribute('href')||x.href||'').filter(x=>x.includes('/v/'));return JSON.stringify([...new Set(a)].slice(0,60));})()";web.evaluateJavascript(js,val->{String s=unquote(val);Matcher m=Pattern.compile("(?:https?://(?:www\\\\.)?divar\\\\.ir)?/v/[A-Za-z0-9_-]+").matcher(s);while(m.find()&&links.size()<40){String u=m.group();if(u.startsWith("/v/"))u="https://divar.ir"+u;if(!links.contains(u))links.add(u);}if(links.isEmpty()){summary.setText("آگهی‌ها پیدا شدند ولی لینک جزئیات خوانده نشد؛ در حال تلاش دوباره…");web.postDelayed(this::parseSearch,2500);return;}summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد…");running=true;processNext();});}
'''
s = s[:start] + new + s[end:]
p.write_text(s)
