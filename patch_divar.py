from pathlib import Path

p = Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s = p.read_text()

def replace_between(src, start_marker, end_marker, replacement):
    a = src.index(start_marker)
    b = src.index(end_marker, a)
    return src[:a] + replacement + src[b:]

s = replace_between(s, '    void collect(int n){', '    void parseSearch(){', '''    void collect(int n){
        if(n>=120){parseSearch();return;}
        web.evaluateJavascript("window.scrollBy(0,Math.max(window.innerHeight*0.9,500));",x->web.postDelayed(()->collect(n+1),350));
    }
''')

s = replace_between(s, '    void parseSearch(){', '    String unquote(', '''    void parseSearch(){
        String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.indexOf('/v/')>=0);return [...new Set(a)].join('\\n');})()";
        web.evaluateJavascript(js,val->{
            String s=unquote(val);
            for(String u:s.split("\\n")){
                u=u.trim();
                if(u.contains("/v/")&&!links.contains(u)&&links.size()<1200)links.add(u);
            }
            if(links.isEmpty()){summary.setText("لینک آگهی‌ها پیدا نشد؛ در حال تلاش دوباره…");web.postDelayed(this::parseSearch,2500);return;}
            summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد…");running=true;processNext();
        });
    }
''')

s = replace_between(s, '    void processNext(){', '    void extract(int i){', '''    void processNext(){
        if(!running)return;
        if(detailIndex>=links.size()){running=false;showResults();return;}
        final int i=detailIndex;detailWeb.loadUrl(links.get(i));detailWeb.postDelayed(()->extract(i),1800);
    }
''')

s = replace_between(s, '    void extract(int i){', '    Listing parse(', '''    void extract(int i){
        detailWeb.evaluateJavascript("(document.querySelector('h1')||{}).innerText||''",tv->{
            String title=unquote(tv);
            detailWeb.evaluateJavascript("document.body?document.body.innerText:''",bv->{
                String body=unquote(bv);rows.add(parse(links.get(i),title,body));detailIndex++;
                summary.setText("در حال دریافت جزئیات: "+detailIndex+" / "+links.size());processNext();
            });
        });
    }
''')

p.write_text(s)
