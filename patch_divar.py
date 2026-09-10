from pathlib import Path

p = Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s = p.read_text()

def replace_between(src, start_marker, end_marker, replacement):
    a = src.index(start_marker)
    b = src.index(end_marker, a)
    return src[:a] + replacement + src[b:]

s = replace_between(
    s,
    '    void collect(int n){',
    '    void parseSearch(){',
    '''    void collect(int n){
        if(n>=120){parseSearch();return;}
        web.evaluateJavascript("window.scrollBy(0,Math.max(window.innerHeight*0.9,500));",x->web.postDelayed(()->collect(n+1),350));
    }
'''
)

s = replace_between(
    s,
    '    void parseSearch(){',
    '    String unquote(',
    '''    void parseSearch(){
        String js="(function(){let out=new Set();document.querySelectorAll('[href]').forEach(x=>{let u=x.getAttribute('href')||x.href||'';if(u.includes('/v/')){try{u=new URL(u,location.href).href;}catch(e){}out.add(u.split('#')[0].split('?')[0]);}});let h=document.documentElement?document.documentElement.outerHTML:'';let re=/(?:https?:\\/\\/(?:www\\.)?divar\\.ir)?\\/v\\/[^\\\"'<>\\s]+/g,m;while((m=re.exec(h))!==null){let u=m[0].replace(/\\\\/g,'/');if(u.startsWith('/v/'))u='https://divar.ir'+u;out.add(u);}return JSON.stringify(Array.from(out).slice(0,1200));})()";
        web.evaluateJavascript(js,val->{
            String s=unquote(val);
            Matcher m=Pattern.compile("(?:https?://(?:www\\.)?divar\\.ir)?/v/[^\\\"'<>\\s]+",Pattern.CASE_INSENSITIVE).matcher(s);
            while(m.find()&&links.size()<1200){
                String u=m.group();
                if(u.startsWith("/v/"))u="https://divar.ir"+u;
                if(!links.contains(u))links.add(u);
            }
            if(links.isEmpty()){
                summary.setText("لینک آگهی‌ها پیدا نشد؛ صفحه دیوار هنوز کامل بارگذاری نشده است.");
                web.postDelayed(this::parseSearch,2000);
                return;
            }
            summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد…");
            running=true;
            processNext();
        });
    }
'''
)

s = replace_between(
    s,
    '    void processNext(){',
    '    void extract(int i){',
    '''    void processNext(){
        if(!running)return;
        if(detailIndex>=links.size()){running=false;showResults();return;}
        final int i=detailIndex;
        detailWeb.loadUrl(links.get(i));
        detailWeb.postDelayed(()->extract(i),1200);
    }
'''
)

s = replace_between(
    s,
    '    void extract(int i){',
    '    Listing parse(',
    '''    void extract(int i){
        detailWeb.evaluateJavascript("(document.querySelector('h1')||{}).innerText||''",tv->{
            String title=unquote(tv);
            detailWeb.evaluateJavascript("document.body?document.body.innerText:''",bv->{
                String body=unquote(bv);
                rows.add(parse(links.get(i),title,body));
                detailIndex++;
                summary.setText("در حال دریافت جزئیات: "+detailIndex+" / "+links.size());
                processNext();
            });
        });
    }
'''
)

s = replace_between(
    s,
    '    Listing parse(',
    '    void showResults(){',
    '''    Listing parse(String link,String title,String text){
        Listing l=new Listing();
        String t=norm(text);
        l.link=link;
        l.title=norm(title);
        l.sqm=area(t);
        l.rooms=rooms(t);
        l.floor=floor(t);
        l.price=nearAmount(t,"قیمت(?:\\s*(?:کل|فروش|تومان))?|قیمت فروش|قیمت کل");
        l.deposit=nearAmount(t,"ودیعه|رهن|پیش پرداخت|پیش");
        l.rent=nearAmount(t,"اجاره ماهانه|اجاره");
        l.pricePerSqm=nearAmount(t,"قیمت\\s*هر\\s*متر|قیمت\\s*/\\s*متر|هر متر|قیمت متری");
        if(l.pricePerSqm.isEmpty()&&num(l.sqm)>0&&num(l.price)>0)l.pricePerSqm=fmt(num(l.price)/num(l.sqm));
        l.address=near(t,"آدرس|موقعیت|محل آگهی|محله|نشانی");
        l.postedDate=near(t,"تاریخ آگهی|تاریخ انتشار|زمان انتشار|زمان آگهی|منتشر شده|انتشار|لحظاتی پیش|دقایقی پیش|ساعتی پیش|روز پیش");
        l.updatedDate=near(t,"آخرین بروزرسانی|آخرین به‌روزرسانی|بروزرسانی|به‌روزرسانی|ویرایش شده");
        l.ladder=near(t,"نردبان|ویژه|ارتقا|فوری");
        l.parking=feature(t,"پارکینگ");
        l.elevator=feature(t,"آسانسور");
        l.storage=feature(t,"انباری");
        l.totalFloors=near(t,"تعداد کل طبقات|تعداد طبقات|کل طبقات");
        l.buildYear=near(t,"سال ساخت|ساخت|بنا");
        l.type=near(t,"نوع ملک|نوع معامله|نوع");
        l.agency=near(t,"مشاور|آژانس|املاک|نوع آگهی دهنده");
        l.description=desc(t);
        Matcher dm=Pattern.compile("(?s)(?:توضیحات|شرح)\\s*[:：]?\\s*(.*?)(?=\\n(?:متراژ|تعداد اتاق|طبقه|سال ساخت|امکانات|آدرس|قیمت|قیمت هر متر|$))").matcher(t);
        if(dm.find()&&dm.group(1).trim().length()>l.description.length()/2)l.description=dm.group(1).trim();
        return l;
    }
'''
)

p.write_text(s)
