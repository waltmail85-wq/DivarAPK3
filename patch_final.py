from pathlib import Path
import base64

p=Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s=p.read_text()
# Final visual theme
s=s.replace('root.setBackgroundColor(Color.rgb(245,247,246));root.setPadding(dp(14),dp(42),dp(14),dp(10));','root.setBackgroundColor(Color.rgb(6,22,43));root.setPadding(dp(14),dp(18),dp(14),dp(10));')
s=s.replace('TextView title=new TextView(this);title.setText("تحلیل قیمت دیوار");title.setTextSize(23);title.setTextColor(Color.WHITE);title.setGravity(Gravity.CENTER);title.setTypeface(null,1);title.setBackground(bg(Color.rgb(32,75,57),18));root.addView(title,new LinearLayout.LayoutParams(-1,dp(58)));','LinearLayout brand=new LinearLayout(this);brand.setOrientation(LinearLayout.VERTICAL);brand.setGravity(Gravity.CENTER);brand.setBackground(bg(Color.rgb(8,29,52),20));ImageView logo=new ImageView(this);logo.setImageResource(com.divar.pricemeter.R.drawable.logo);logo.setScaleType(ImageView.ScaleType.CENTER_INSIDE);brand.addView(logo,new LinearLayout.LayoutParams(-1,dp(105)));TextView title=new TextView(this);title.setText("دیوار قیمت یاب");title.setTextSize(24);title.setTextColor(Color.rgb(238,194,88));title.setGravity(Gravity.CENTER);title.setTypeface(null,1);brand.addView(title,new LinearLayout.LayoutParams(-1,dp(48)));TextView sub=new TextView(this);sub.setText("تحلیل و استخراج اطلاعات آگهی‌های دیوار");sub.setTextSize(13);sub.setTextColor(Color.rgb(210,180,110));sub.setGravity(Gravity.CENTER);brand.addView(sub,new LinearLayout.LayoutParams(-1,dp(30)));root.addView(brand,new LinearLayout.LayoutParams(-1,dp(190)));')
s=s.replace('t.setTextColor(Color.rgb(70,70,70));','t.setTextColor(Color.rgb(232,190,90));')
s=s.replace('e.setSingleLine(true);e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.WHITE,14));','e.setSingleLine(true);e.setTextColor(Color.WHITE);e.setHintTextColor(Color.rgb(155,165,180));e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.rgb(15,31,54),14));')
s=s.replace('b.setTextColor(Color.WHITE);b.setBackground(bg(Color.rgb(45,125,95),18));','b.setTextColor(Color.rgb(10,25,45));b.setTypeface(null,1);b.setBackground(bg(Color.rgb(224,177,70),18));')
s=s.replace('getWindow().setStatusBarColor(Color.rgb(25,35,30));','getWindow().setStatusBarColor(Color.rgb(6,18,35));')
# Remove hard limit of 40 in parseSearch and make collector continuously collect during scrolling.
a=s.index('    void parseSearch(){')
b=s.index('    String unquote',a)
new='''    void parseSearch(){String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.includes('/v/'));return JSON.stringify([...new Set(a)]);})()";web.evaluateJavascript(js,val->{String z=unquote(val);Matcher m=Pattern.compile("https://divar\\\\.ir/v/[^\\\\\"\\\\s\\\\]]+").matcher(z);while(m.find()&&links.size()<1200)if(!links.contains(m.group()))links.add(m.group());if(links.isEmpty()){summary.setText("آگهی‌ها پیدا نشد؛ صفحه دیوار را بررسی کنید.");return;}summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ دریافت جزئیات شروع شد…");running=true;processNext();});}\n'''
s=s[:a]+new+s[b:]
# Make collection much deeper and collect links at every scroll.
a=s.index('    void collect(int n){')
b=s.index('    void parseSearch(){',a)
new='''    void collect(int n){if(n>=180){parseSearch();return;}String js="(function(){let a=[...document.querySelectorAll('a')].map(x=>x.href||'').filter(x=>x.includes('/v/'));return JSON.stringify([...new Set(a)]);})()";web.evaluateJavascript(js,val->{String z=unquote(val);Matcher m=Pattern.compile("https://divar\\\\.ir/v/[^\\\\\"\\\\s\\\\]]+").matcher(z);while(m.find()&&links.size()<1200)if(!links.contains(m.group()))links.add(m.group());summary.setText("آگهی‌های پیدا شده: "+links.size());web.evaluateJavascript("window.scrollBy(0,Math.max(window.innerHeight*0.85,520));",x->web.postDelayed(()->collect(n+1),300));});}\n'''
s=s[:a]+new+s[b:]
# Show more result rows and include key fields.
s=s.replace('if(s.length()<9000)s.append(l.title).append("\\n").append("قیمت: ").append(l.price).append(" | ").append(l.sqm).append(" متر | هر متر: ").append(l.pricePerSqm).append("\\n\\n");','if(s.length()<30000)s.append(l.title).append("\\n").append("قیمت: ").append(l.price).append(" | ").append(l.sqm).append(" متر | هر متر: ").append(l.pricePerSqm).append(" | تاریخ: ").append(l.postedDate).append("\\n").append("توضیحات: ").append(l.description).append("\\n\\n");')
p.write_text(s)

# Installable icon: use the logo image already supplied in the project patch.
logo_dir=Path('app/src/main/res/drawable'); logo_dir.mkdir(parents=True,exist_ok=True)
# Existing patch_divar embeds the supplied logo as base64. Reuse its generated logo if present.
if not (logo_dir/'logo.jpg').exists():
    q=Path('patch_divar.py').read_text()
    marker='base64.b64decode("'
    i=q.index(marker)+len(marker); j=q.index('")',i)
    (logo_dir/'logo.jpg').write_bytes(base64.b64decode(q[i:j]))

m=Path('app/src/main/AndroidManifest.xml'); ms=m.read_text()
ms=ms.replace('android:label="تحلیل قیمت دیوار"','android:label="دیوار قیمت یاب" android:icon="@drawable/logo" android:roundIcon="@drawable/logo"')
m.write_text(ms)

g=Path('app/build.gradle'); gs=g.read_text().replace("applicationId 'com.divar.pricemeter.v11'","applicationId 'com.divar.pricemeter.v12'").replace("versionCode 11","versionCode 12").replace("versionName '11.0'","versionName '12.0'")
g.write_text(gs)
