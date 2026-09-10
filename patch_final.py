from pathlib import Path
import base64,re

p=Path('app/src/main/java/com/divar/pricemeter/MainActivity.java')
s=p.read_text()

# Premium navy/gold theme
s=s.replace('getWindow().setStatusBarColor(Color.rgb(25,35,30));','getWindow().setStatusBarColor(Color.rgb(5,16,32));')
s=s.replace('root.setBackgroundColor(Color.rgb(245,247,246));root.setPadding(dp(14),dp(42),dp(14),dp(10));','root.setBackgroundColor(Color.rgb(5,18,35));root.setPadding(dp(12),dp(18),dp(12),dp(10));')
s=s.replace('t.setTextColor(Color.rgb(70,70,70));','t.setTextColor(Color.rgb(239,196,91));')
s=s.replace('e.setSingleLine(true);e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.WHITE,14));','e.setSingleLine(true);e.setTextColor(Color.WHITE);e.setHintTextColor(Color.rgb(150,162,180));e.setPadding(dp(12),0,dp(12),0);e.setBackground(bg(Color.rgb(11,29,51),14));')
s=s.replace('b.setTextColor(Color.WHITE);b.setBackground(bg(Color.rgb(45,125,95),18));','b.setTextColor(Color.rgb(7,22,40));b.setTypeface(null,1);b.setBackground(bg(Color.rgb(226,178,67),18));')
s=s.replace('results.setTextColor(Color.DKGRAY);','results.setTextColor(Color.rgb(235,238,244));')
s=s.replace('rs.setBackground(bg(Color.WHITE,16));','rs.setBackground(bg(Color.rgb(9,28,50),18));')

# Header with the original Shahran logo
old='TextView title=new TextView(this);title.setText("تحلیل قیمت دیوار");title.setTextSize(23);title.setTextColor(Color.WHITE);title.setGravity(Gravity.CENTER);title.setTypeface(null,1);title.setBackground(bg(Color.rgb(32,75,57),18));root.addView(title,new LinearLayout.LayoutParams(-1,dp(58)));'
new='LinearLayout brand=new LinearLayout(this);brand.setOrientation(LinearLayout.VERTICAL);brand.setGravity(Gravity.CENTER);brand.setPadding(dp(8),dp(8),dp(8),dp(8));brand.setBackground(bg(Color.rgb(7,27,49),22));ImageView logo=new ImageView(this);logo.setImageResource(com.divar.pricemeter.R.drawable.logo);logo.setScaleType(ImageView.ScaleType.CENTER_INSIDE);brand.addView(logo,new LinearLayout.LayoutParams(-1,dp(112)));TextView title=new TextView(this);title.setText("تحلیل قیمت دیوار");title.setTextSize(25);title.setTextColor(Color.rgb(239,196,91));title.setGravity(Gravity.CENTER);title.setTypeface(null,1);brand.addView(title,new LinearLayout.LayoutParams(-1,dp(48)));TextView sub=new TextView(this);sub.setText("تحلیل و استخراج اطلاعات آگهی‌های دیوار");sub.setTextSize(14);sub.setTextColor(Color.rgb(224,207,160));sub.setGravity(Gravity.CENTER);brand.addView(sub,new LinearLayout.LayoutParams(-1,dp(30)));root.addView(brand,new LinearLayout.LayoutParams(-1,dp(200)));'
s=s.replace(old,new)

# Make category spinner dark/gold
s=s.replace('category.setBackground(bg(Color.WHITE,14));','category.setBackground(bg(Color.rgb(11,29,51),14));')

# Replace collector so it scrolls the actual Divar scroll container and harvests hidden /v/ URLs.
start=s.index('    void collect(int n){')
end=s.index('    void parseSearch(){',start)
collect=r'''    void collect(int n){
        if(n>=180){parseSearch();return;}
        String js="(function(){const out=new Set();document.querySelectorAll('a[href]').forEach(a=>{let h=a.href||'';if(h.includes('/v/'))out.add(h);});const html=document.documentElement.outerHTML||'';const rx=/https?:\\/\\/divar\\.ir\\/v\\/[A-Za-z0-9_-]+/g;let m;while((m=rx.exec(html))!==null)out.add(m[0]);document.querySelectorAll('button').forEach(b=>{let t=(b.innerText||'').trim();if(/بیشتر|نمایش بیشتر|آگهی/.test(t)&&t.length<80){try{b.click()}catch(e){}}});let els=[document.scrollingElement,...document.querySelectorAll('*')].filter(e=>e&&e.scrollHeight>e.clientHeight+150).sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight)).slice(0,8);els.forEach(e=>{try{e.scrollTop=Math.min(e.scrollHeight,e.scrollTop+Math.max(e.clientHeight*.9,600))}catch(x){}});window.scrollBy(0,Math.max(window.innerHeight*.9,600));return JSON.stringify([...out]);})()";
        web.evaluateJavascript(js,val->{
            String z=unquote(val);
            Matcher m=Pattern.compile("https://divar\\.ir/v/[A-Za-z0-9_-]+").matcher(z);
            while(m.find()&&links.size()<1200) if(!links.contains(m.group())) links.add(m.group());
            summary.setText("آگهی‌های پیدا شده: "+links.size()+" / 1200");
            web.postDelayed(()->collect(n+1),220);
        });
    }
'''
s=s[:start]+collect+s[end:]

# Replace parser with a version that also harvests relative URLs from the DOM/HTML.
start=s.index('    void parseSearch(){')
end=s.index('    String unquote',start)
parse=r'''    void parseSearch(){
        String js="(function(){const out=new Set();document.querySelectorAll('a[href]').forEach(a=>{let h=a.href||'';if(h.includes('/v/'))out.add(h)});let html=document.documentElement.outerHTML||'';let rx=/(?:https?:\\/\\/divar\\.ir)?\\/v\\/[A-Za-z0-9_-]+/g,m;while((m=rx.exec(html))!==null){let h=m[0];if(h.startsWith('/'))h='https://divar.ir'+h;out.add(h)}return JSON.stringify([...out]);})()";
        web.evaluateJavascript(js,val->{
            String z=unquote(val);
            Matcher m=Pattern.compile("https://divar\\.ir/v/[A-Za-z0-9_-]+").matcher(z);
            while(m.find()&&links.size()<1200) if(!links.contains(m.group())) links.add(m.group());
            if(links.isEmpty()){summary.setText("لینک آگهی‌ها استخراج نشد؛ صفحه دیوار یا اتصال اینترنت را بررسی کنید.");return;}
            summary.setText("تعداد "+links.size()+" آگهی پیدا شد؛ استخراج جزئیات شروع شد…");
            running=true;processNext();
        });
    }
'''
s=s[:start]+parse+s[end:]

# Replace sequential detail navigation with fast same-origin fetch batches. This is not an anti-bot bypass; it uses the loaded Divar session normally.
start=s.index('    void processNext(){')
end=s.index('    Listing parse(',start)
proc=r'''    void processNext(){
        if(!running)return;
        if(detailIndex>=links.size()){running=false;showResults();return;}
        int from=detailIndex,to=Math.min(detailIndex+12,links.size());
        ArrayList<String> batch=new ArrayList<>(links.subList(from,to));
        StringBuilder arr=new StringBuilder("[");for(int i=0;i<batch.size();i++){if(i>0)arr.append(',');arr.append("\\\"").append(batch.get(i).replace("\\\"","\\\\\\\"")).append("\\\"");}arr.append(']');
        String js="(async function(urls){let out=[];for(let u of urls){try{let r=await fetch(u,{credentials:'include'});let h=await r.text();let d=new DOMParser().parseFromString(h,'text/html');out.push({u:u,t:(d.querySelector('h1')||{}).innerText||'',b:d.body?d.body.innerText:''});}catch(e){out.push({u:u,t:'',b:''});}}return JSON.stringify(out);})("+arr+")";
        detailWeb.evaluateJavascript(js,val->{
            try{
                String raw=unquote(val);
                org.json.JSONArray a=new org.json.JSONArray(raw);
                for(int j=0;j<a.length();j++){org.json.JSONObject o=a.getJSONObject(j);rows.add(parse(o.optString("u"),o.optString("t"),o.optString("b")));}
            }catch(Exception e){for(String u:batch){Listing l=new Listing();l.link=u;rows.add(l);}}
            detailIndex=to;summary.setText("در حال دریافت جزئیات: "+detailIndex+" / "+links.size());detailWeb.postDelayed(this::processNext,180);
        });
    }

'''
s=s[:start]+proc+s[end:]

# Improve area extraction.
s=s.replace('String area(String t){Matcher m=Pattern.compile("(?<![0-9])([0-9]{2,4})\\\\s*(?:متر(?:مربع)?|m²|m2)").matcher(norm(t));return m.find()?m.group(1):"";}', 'String area(String t){Matcher m=Pattern.compile("(?<![0-9])([0-9]{2,4})(?:\\\\.\\\\d+)?\\\\s*(?:متر(?:مربع)?|متر|m²|m2)").matcher(norm(t));return m.find()?m.group(1):"";}')

# Save Excel directly into Downloads on Android 10+, avoiding the unreliable document-picker path.
start=s.index('    void exportXlsx(){')
end=s.index('    String esc(',start)
export=r'''    void exportXlsx(){
        if(rows.isEmpty()){Toast.makeText(this,"ابتدا جستجو و تحلیل را انجام دهید",Toast.LENGTH_LONG).show();return;}
        try{
            String name="DivarPriceAnalysis_"+new java.text.SimpleDateFormat("yyyyMMdd_HHmm",Locale.US).format(new java.util.Date())+".xlsx";
            if(Build.VERSION.SDK_INT>=29){
                android.content.ContentValues cv=new android.content.ContentValues();cv.put(android.provider.MediaStore.Downloads.DISPLAY_NAME,name);cv.put(android.provider.MediaStore.Downloads.MIME_TYPE,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");cv.put(android.provider.MediaStore.Downloads.RELATIVE_PATH,"Download");
                Uri u=getContentResolver().insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI,cv);if(u==null)throw new IOException("download uri null");OutputStream o=getContentResolver().openOutputStream(u);writeXlsx(o);o.close();Toast.makeText(this,"Excel در پوشه Download ذخیره شد",Toast.LENGTH_LONG).show();
            }else{Intent in=new Intent(Intent.ACTION_CREATE_DOCUMENT);in.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");in.putExtra(Intent.EXTRA_TITLE,name);startActivityForResult(in,91);}
        }catch(Exception e){Toast.makeText(this,"خطا در ساخت فایل Excel: "+e.getMessage(),Toast.LENGTH_LONG).show();}
    }
    @Override protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==91&&c==RESULT_OK&&d!=null){try{OutputStream o=getContentResolver().openOutputStream(d.getData());writeXlsx(o);o.close();Toast.makeText(this,"فایل Excel با موفقیت ذخیره شد",Toast.LENGTH_LONG).show();}catch(Exception e){Toast.makeText(this,"خطا در ذخیره Excel: "+e.getMessage(),Toast.LENGTH_LONG).show();}}}
'''
s=s[:start]+export+s[end:]

# Original Shahran logo asset from the supplied logo, embedded as a compact base64 JPEG.
logo_dir=Path('app/src/main/res/drawable');logo_dir.mkdir(parents=True,exist_ok=True)
asset=Path('assets/shahran_logo.b64')
if asset.exists():
    (logo_dir/'logo.jpg').write_bytes(base64.b64decode(asset.read_text().strip()))

# Force launcher icon/label regardless of previous patch state.
m=Path('app/src/main/AndroidManifest.xml');ms=m.read_text()
ms=re.sub(r'android:label="[^"]+"','android:label="دیوار قیمت یاب"',ms, count=1)
if 'android:icon=' in ms: ms=re.sub(r'android:icon="[^"]+"','android:icon="@drawable/logo"',ms, count=1)
else: ms=ms.replace('android:label="دیوار قیمت یاب"','android:label="دیوار قیمت یاب" android:icon="@drawable/logo"')
if 'android:roundIcon=' in ms: ms=re.sub(r'android:roundIcon="[^"]+"','android:roundIcon="@drawable/logo"',ms, count=1)
else: ms=ms.replace('android:icon="@drawable/logo"','android:icon="@drawable/logo" android:roundIcon="@drawable/logo"')
m.write_text(ms)

g=Path('app/build.gradle');gs=g.read_text()
gs=re.sub(r"applicationId '[^']+'","applicationId 'com.divar.pricemeter.v13'",gs)
gs=re.sub(r'versionCode \d+','versionCode 13',gs)
gs=re.sub(r"versionName '[^']+'","versionName '13.0'",gs)
g.write_text(gs)
