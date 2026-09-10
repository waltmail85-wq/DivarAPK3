from pathlib import Path
import base64

p=Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s=p.read_text()

# Theme
s=s.replace('root.setBackgroundColor(Color.rgb(245,247,246));root.setPadding(dp(14),dp(42),dp(14),dp(10));','root.setBackgroundColor(Color.rgb(6,22,43));root.setPadding(dp(14),dp(18),dp(14),dp(10));')
s=s.replace('getWindow().setStatusBarColor(Color.rgb(25,35,30));','getWindow().setStatusBarColor(Color.rgb(6,18,35));')
s=s.replace('t.setTextColor(Color.rgb(70,70,70));','t.setTextColor(Color.rgb(232,190,90));')
s=s.replace('e.setSingleLine(true);e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.WHITE,14));','e.setSingleLine(true);e.setTextColor(Color.WHITE);e.setHintTextColor(Color.rgb(155,165,180));e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.rgb(15,31,54),14));')
s=s.replace('b.setTextColor(Color.WHITE);b.setBackground(bg(Color.rgb(45,125,95),18));','b.setTextColor(Color.rgb(10,25,45));b.setTypeface(null,1);b.setBackground(bg(Color.rgb(224,177,70),18));')

# Replace title header with logo brand block if original exists.
old='TextView title=new TextView(this);title.setText("تحلیل قیمت دیوار");title.setTextSize(23);title.setTextColor(Color.WHITE);title.setGravity(Gravity.CENTER);title.setTypeface(null,1);title.setBackground(bg(Color.rgb(32,75,57),18));root.addView(title,new LinearLayout.LayoutParams(-1,dp(58)));'
new='LinearLayout brand=new LinearLayout(this);brand.setOrientation(LinearLayout.VERTICAL);brand.setGravity(Gravity.CENTER);brand.setBackground(bg(Color.rgb(8,29,52),20));ImageView logo=new ImageView(this);logo.setImageResource(com.divar.pricemeter.R.drawable.logo);logo.setScaleType(ImageView.ScaleType.CENTER_INSIDE);brand.addView(logo,new LinearLayout.LayoutParams(-1,dp(105)));TextView title=new TextView(this);title.setText("دیوار قیمت یاب");title.setTextSize(24);title.setTextColor(Color.rgb(238,194,88));title.setGravity(Gravity.CENTER);title.setTypeface(null,1);brand.addView(title,new LinearLayout.LayoutParams(-1,dp(48)));TextView sub=new TextView(this);sub.setText("تحلیل و استخراج اطلاعات آگهی‌های دیوار");sub.setTextSize(13);sub.setTextColor(Color.rgb(210,180,110));sub.setGravity(Gravity.CENTER);brand.addView(sub,new LinearLayout.LayoutParams(-1,dp(30)));root.addView(brand,new LinearLayout.LayoutParams(-1,dp(190)));'
s=s.replace(old,new)

# Correct search parser with valid Java escaping.
start=s.index('    void parseSearch(){')
end=s.index('    String unquote',start)
parse=r'''    void parseSearch(){
        String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.includes('/v/'));return JSON.stringify([...new Set(a)]);})()";
        web.evaluateJavascript(js,val->{
            String z=unquote(val);
            Matcher m=Pattern.compile("https://divar\\.ir/v/[^\"\\s\\]]+").matcher(z);
            while(m.find()&&links.size()<1200) if(!links.contains(m.group())) links.add(m.group());
            if(links.isEmpty()){summary.setText("آگهی‌ها پیدا نشد؛ صفحه دیوار را بررسی کنید.");return;}
            summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد...");
            running=true;processNext();
        });
    }
'''
s=s[:start]+parse+s[end:]

# Correct deep virtualized collection.
start=s.index('    void collect(int n){')
end=s.index('    void parseSearch(){',start)
collect=r'''    void collect(int n){
        if(n>=180){parseSearch();return;}
        String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.includes('/v/'));return JSON.stringify([...new Set(a)]);})()";
        web.evaluateJavascript(js,val->{
            String z=unquote(val);
            Matcher m=Pattern.compile("https://divar\\.ir/v/[^\"\\s\\]]+").matcher(z);
            while(m.find()&&links.size()<1200) if(!links.contains(m.group())) links.add(m.group());
            summary.setText("آگهی‌های پیدا شده: "+links.size());
            web.evaluateJavascript("window.scrollBy(0,Math.max(window.innerHeight*0.85,520));",x->web.postDelayed(()->collect(n+1),300));
        });
    }
'''
s=s[:start]+collect+s[end:]

# Make result area larger and fix any malformed ternary from earlier patches.
import re
s=re.sub(r'void showResults\(\)\{.*?\n    \}\n    void exportXlsx', '''void showResults(){
        double sum=0,min=Double.MAX_VALUE,max=0;int n=0;StringBuilder out=new StringBuilder();
        for(Listing l:rows){double p=num(l.pricePerSqm);if(p>0){sum+=p;n++;min=Math.min(min,p);max=Math.max(max,p);}if(out.length()<30000)out.append(l.title).append("\\n").append("قیمت: ").append(l.price).append(" | ").append(l.sqm).append(" متر | هر متر: ").append(l.pricePerSqm).append(" | تاریخ: ").append(l.postedDate).append("\\n").append("توضیحات: ").append(l.description).append("\\n\\n");}
        if(n>0) summary.setText("میانگین هر متر: "+fmt(sum/n)+" تومان | کمینه: "+fmt(min)+" | بیشینه: "+fmt(max)); else summary.setText("تعداد آگهی: "+rows.size());
        results.setText(out.toString());
    }
    void exportXlsx''', s, flags=re.S)

# Icon
logo_dir=Path('app/src/main/res/drawable');logo_dir.mkdir(parents=True,exist_ok=True)
if not (logo_dir/'logo.jpg').exists():
    q=Path('patch_divar.py').read_text(); marker='base64.b64decode("'; i=q.index(marker)+len(marker); j=q.index('")',i)
    (logo_dir/'logo.jpg').write_bytes(base64.b64decode(q[i:j]))

m=Path('app/src/main/AndroidManifest.xml');ms=m.read_text()
if 'android:icon=' not in ms:
    ms=ms.replace('android:label="تحلیل قیمت دیوار"','android:label="دیوار قیمت یاب" android:icon="@drawable/logo" android:roundIcon="@drawable/logo"')
m.write_text(ms)

g=Path('app/build.gradle');gs=g.read_text().replace("applicationId 'com.divar.pricemeter.v11'","applicationId 'com.divar.pricemeter.v12'").replace("versionCode 11","versionCode 12").replace("versionName '11.0'","versionName '12.0'")
g.write_text(gs)
