from pathlib import Path
p=Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s=p.read_text()
a='    void collect(int n){'
b='    void parseSearch(){'
i=s.index(a); j=s.index(b,i)
new='''    void collect(int n){
        if(n>=180){parseSearch();return;}
        String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.indexOf('/v/')>=0);return [...new Set(a)].join('\\\\n');})()";
        web.evaluateJavascript(js,val->{
            String z=unquote(val);
            for(String u:z.split("\\\\n")){u=u.trim();if(u.contains("/v/")&&!links.contains(u)&&links.size()<1200)links.add(u);}
            summary.setText("آگهی‌های پیدا شده: "+links.size()+" / 1200");
            web.evaluateJavascript("window.scrollBy(0,Math.max(window.innerHeight*0.82,520));",x->web.postDelayed(()->collect(n+1),260));
        });
    }
'''
p.write_text(s[:i]+new+s[j:])
