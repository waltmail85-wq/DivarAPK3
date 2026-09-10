package com.divar.pricemeter;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.view.View;
import android.widget.*;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.NumberFormat;
import java.util.*;
import java.util.regex.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class MainActivity extends Activity {
    EditText city, area, minSqm, maxSqm, minPsm, maxPsm;
    Spinner category;
    TextView summary, results;
    WebView web, detailWeb;
    ArrayList<Listing> rows = new ArrayList<>();
    ArrayList<String[]> candidates = new ArrayList<>();
    int detailIndex = -1;
    boolean detailRunning = false;
    final String[] cats = {"buy-apartment", "rent-apartment", "buy-house-villa"};
    final NumberFormat nf = NumberFormat.getIntegerInstance(Locale.US);

    static class Listing {
        String title="", link="", price="", deposit="", rent="", sqm="", rooms="", floor="",
               totalFloors="", buildYear="", parking="", elevator="", storage="", address="",
               postedDate="", updatedDate="", ladder="", description="", type="", agency="",
               pricePerSqm="";
        String[] csv() {
            return new String[]{title, link, price, deposit, rent, sqm, rooms, floor, totalFloors,
                    buildYear, parking, elevator, storage, pricePerSqm, address, postedDate,
                    updatedDate, ladder, type, agency, description};
        }
    }

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(12,12,12,12);

        ScrollView topScroll = new ScrollView(this);
        LinearLayout form = new LinearLayout(this);
        form.setOrientation(LinearLayout.VERTICAL);
        city = edit("شهر", "tabriz"); area = edit("محله", "نصر");
        category = new Spinner(this);
        category.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, cats));
        form.addView(city); form.addView(area); form.addView(category);

        LinearLayout r1 = new LinearLayout(this);
        r1.addView(editTo(r1,"حداقل متر", ""));
        r1.addView(editTo(r1,"حداکثر متر", ""));
        form.addView(r1);
        LinearLayout r2 = new LinearLayout(this);
        r2.addView(editTo(r2,"حداقل قیمت/متر", ""));
        r2.addView(editTo(r2,"حداکثر قیمت/متر", ""));
        form.addView(r2);
        minSqm=(EditText)r1.getChildAt(0); maxSqm=(EditText)r1.getChildAt(1);
        minPsm=(EditText)r2.getChildAt(0); maxPsm=(EditText)r2.getChildAt(1);

        Button search = new Button(this);
        search.setText("جستجو و تحلیل");
        search.setOnClickListener(v -> loadDivar());
        form.addView(search);
        summary = new TextView(this);
        summary.setText("آماده جستجو"); summary.setTextSize(16); summary.setPadding(4,8,4,8);
        form.addView(summary);
        Button export = new Button(this);
        export.setText("خروجی Excel (XLSX)");
        export.setOnClickListener(v -> exportXls());
        form.addView(export);
        topScroll.addView(form);
        root.addView(topScroll, new LinearLayout.LayoutParams(-1,0,0.43f));

        results = new TextView(this); results.setTextSize(14);
        ScrollView rs=new ScrollView(this); rs.addView(results);
        root.addView(rs,new LinearLayout.LayoutParams(-1,0,0.27f));
        web = makeWeb(); root.addView(web,new LinearLayout.LayoutParams(-1,0,0.29f));
        detailWeb = makeWeb(); detailWeb.setVisibility(View.INVISIBLE);
        root.addView(detailWeb,new LinearLayout.LayoutParams(1,1));
        setContentView(root);
    }

    WebView makeWeb() {
        WebView w=new WebView(this);
        WebSettings s=w.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        s.setUserAgentString("Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/125 Mobile Safari/537.36");
        w.setWebViewClient(new WebViewClient()); return w;
    }

    EditText edit(String hint,String value){ EditText e=new EditText(this); e.setHint(hint); e.setText(value); e.setInputType(2); e.setSingleLine(); return e; }
    EditText editTo(LinearLayout p,String h,String v){ EditText e=edit(h,v); e.setLayoutParams(new LinearLayout.LayoutParams(0,-2,1)); return e; }

    void loadDivar(){
        String c=city.getText().toString().trim(); String a=area.getText().toString().trim();
        String cat=cats[category.getSelectedItemPosition()];
        String url="https://divar.ir/s/"+Uri.encode(c)+"/"+cat+(a.isEmpty()?"":"?q="+Uri.encode(a));
        rows.clear(); candidates.clear(); detailIndex=-1; detailRunning=false;
        summary.setText("در حال بارگذاری دیوار..."); results.setText(""); web.loadUrl(url);
        web.postDelayed(() -> collect(0), 7000);
    }

    void collect(int n){
        if(n>=12){ parseSearchPage(); return; }
        web.evaluateJavascript("window.scrollTo(0,document.body.scrollHeight);", x -> web.postDelayed(() -> collect(n+1),650));
    }

    String unescape(String s){
        return s.replace("\\\"","\"").replace("\\n","\n").replace("\\r","\r").replace("\\t","\t")
                .replace("\\u003C","<").replace("\\u003E",">").replace("\\u0026","&").replace("\\/","/");
    }
    String clean(String s){ if(s==null)return ""; return normalizeDigits(s).replace('\u200c',' ').replaceAll("[ \\t]+"," ").trim(); }
    String normalizeDigits(String s){
        if(s==null)return ""; StringBuilder b=new StringBuilder();
        for(char ch:s.toCharArray()){
            if(ch>='۰'&&ch<='۹')b.append((char)('0'+ch-'۰')); else if(ch>='٠'&&ch<='٩')b.append((char)('0'+ch-'٠')); else b.append(ch);
        } return b.toString();
    }
    double num(String s){ try{return Double.parseDouble(normalizeDigits(s).replace(",","").replace("٬","").replace(" ",""));}catch(Exception e){return 0;} }

    String amount(String s){
        if(s==null)return "";
        Matcher m=Pattern.compile("([0-9][0-9,٬. ]{0,30})\\s*(میلیارد|میلیون|هزار)?").matcher(normalizeDigits(s));
        if(!m.find())return ""; double v=num(m.group(1)); String u=m.group(2)==null?"":m.group(2);
        if("میلیارد".equals(u))v*=1000000000d; else if("میلیون".equals(u))v*=1000000d; else if("هزار".equals(u))v*=1000d;
        return v>0?fmt(v):"";
    }
    String near(String text,String labels){
        Matcher m=Pattern.compile("(?i)(?:"+labels+")\\s*[:：\\-]?\\s*([^\\n]{1,160})").matcher(normalizeDigits(text));
        return m.find()?clean(m.group(1)):"";
    }
    String nearAmount(String text,String labels){ String x=near(text,labels); return x.isEmpty()?"":amount(x); }
    String firstNumber(String text,String regex){ Matcher m=Pattern.compile(regex).matcher(normalizeDigits(text)); return m.find()?fmt(num(m.group(1))):""; }
    String findArea(String text){ return firstNumber(text,"(?<![0-9])([0-9]{2,4})\\s*(?:متر(?:مربع)?|m²|m2)"); }
    String findRooms(String text){ Matcher m=Pattern.compile("([0-9]{1,2})\\s*(?:خوابه?|خواب|اتاق)").matcher(normalizeDigits(text)); return m.find()?m.group(1):""; }
    String findFloor(String text){ Matcher m=Pattern.compile("(?:طبقه|واحد)\\s*[:：\\-]?\\s*(همکف|زیرزمین|منفی\\s*[0-9]+|[0-9]+)").matcher(normalizeDigits(text)); return m.find()?clean(m.group(1)):""; }
    String findYear(String text){ Matcher m=Pattern.compile("(?:ساخت|سال ساخت|بنا)\\s*[:：\\-]?\\s*(13[0-9]{2}|14[0-9]{2}|20[0-9]{2})").matcher(normalizeDigits(text)); return m.find()?m.group(1):""; }
    String feature(String text,String f){
        Matcher m=Pattern.compile("(?i)(?:"+f+")\\s*[:：\\-]?\\s*(دارد|ندارد|داره|نداره|بله|خیر)").matcher(normalizeDigits(text));
        if(m.find())return m.group(1); return normalizeDigits(text).contains(f)?"دارد":"";
    }
    String firstLine(String t){ for(String x:t.split("\\n"))if(clean(x).length()>3)return clean(x); return ""; }
    String description(String text){ String x=near(text,"توضیحات|شرح"); if(!x.isEmpty())return x; return text.length()>1500?text.substring(0,1500):text; }

    void parseSearchPage(){
        String js="(function(){let out=[];let seen=new Set();document.querySelectorAll('a').forEach(a=>{let h=a.href||'';if(h.includes('/v/')){let t=(a.innerText||a.textContent||'').trim();if(!seen.has(h)){seen.add(h);out.push(JSON.stringify({h:h,t:t}));}}});return JSON.stringify(out);})()";
        web.evaluateJavascript(js,val -> {
            String t=unescape(val);
            Matcher m=Pattern.compile("\\{\\\"h\\\":\\\"(https://divar\\.ir/v/[^\\\"]+)\\\",\\\"t\\\":\\\"(.*?)\\\"\\}").matcher(t);
            LinkedHashMap<String,String> items=new LinkedHashMap<>(); while(m.find())items.put(m.group(1),m.group(2));
            if(items.isEmpty()){summary.setText("آگهی‌ها دیده می‌شوند ولی لینک استخراج نشد؛ احتمالاً دیوار ساختار صفحه یا ضدربات را تغییر داده است.");return;}
            double minS=parseFilter(minSqm),maxS=parseFilter(maxSqm);
            for(Map.Entry<String,String> e:items.entrySet()){candidates.add(new String[]{e.getKey(),e.getValue(),String.valueOf(minS),String.valueOf(maxS)});if(candidates.size()>=50)break;}
            summary.setText("تعداد "+candidates.size()+" آگهی پیدا شد؛ در حال دریافت جزئیات..."); detailIndex=0; detailRunning=true; processNextDetail();
        });
    }

    void processNextDetail(){
        if(!detailRunning)return;
        if(detailIndex>=candidates.size()){detailRunning=false;applyFiltersAndShow();return;}
        String url=candidates.get(detailIndex)[0]; detailWeb.loadUrl(url); final int idx=detailIndex;
        detailWeb.postDelayed(() -> {if(detailRunning&&detailIndex==idx)extractDetail(idx);},4500);
    }

    void extractDetail(int idx){
        String js="(function(){let b=document.body?document.body.innerText:'';let h=document.querySelector('h1');let t=h?h.innerText:'';return JSON.stringify({title:t,body:b});})()";
        detailWeb.evaluateJavascript(js,val -> {
            String raw=unescape(val),title="",body="";
            Matcher mm=Pattern.compile("\\{\\\"title\\\":\\\"(.*?)\\\",\\\"body\\\":\\\"(.*)\\\"\\}",Pattern.DOTALL).matcher(raw);
            if(mm.find()){title=clean(mm.group(1));body=normalizeDigits(mm.group(2)).replace('\u200c',' ');} if(body.isEmpty())body=candidates.get(idx)[1];
            rows.add(parseListing(candidates.get(idx)[0],title,body)); detailIndex++;
            summary.setText("در حال دریافت جزئیات: "+detailIndex+" / "+candidates.size()); processNextDetail();
        });
    }

    Listing parseListing(String link,String title,String text){
        Listing l=new Listing(); l.link=link; l.title=title.isEmpty()?firstLine(text):title; l.sqm=findArea(text); l.rooms=findRooms(text); l.floor=findFloor(text); l.buildYear=findYear(text);
        l.price=nearAmount(text,"قیمت\\s*(?:کل|فروش)?|قیمت فروش");
        l.deposit=nearAmount(text,"ودیعه|رهن|پیش"); l.rent=nearAmount(text,"اجاره|اجاره ماهانه");
        l.pricePerSqm=nearAmount(text,"قیمت\\s*/\\s*متر|قیمت هر متر|هر متر");
        if(l.pricePerSqm.isEmpty()&&num(l.sqm)>0&&num(l.price)>0)l.pricePerSqm=fmt(num(l.price)/num(l.sqm));
        l.address=near(text,"آدرس|موقعیت|محله|نشانی"); l.postedDate=near(text,"تاریخ آگهی|زمان آگهی|منتشر شده|انتشار");
        l.updatedDate=near(text,"آخرین بروزرسانی|آخرین به‌روزرسانی|بروزرسانی|به‌روزرسانی"); l.ladder=near(text,"نردبان|ویژه|ارتقا|فوری");
        l.parking=feature(text,"پارکینگ"); l.elevator=feature(text,"آسانسور"); l.storage=feature(text,"انباری"); l.totalFloors=near(text,"تعداد طبقات|کل طبقات");
        l.type=near(text,"نوع ملک|نوع"); l.agency=near(text,"مشاور|آژانس|املاک"); l.description=description(text); return l;
    }

    void applyFiltersAndShow(){
        double minS=parseFilter(minSqm),maxS=parseFilter(maxSqm),minP=parseFilter(minPsm),maxP=parseFilter(maxPsm); ArrayList<Listing> filtered=new ArrayList<>();
        double sum=0,min=Double.MAX_VALUE,max=0; int count=0; StringBuilder sb=new StringBuilder();
        for(Listing l:rows){double s=num(l.sqm),p=num(l.pricePerSqm); if(minS>0&&s>0&&s<minS)continue; if(maxS>0&&s>maxS)continue; if(minP>0&&p>0&&p<minP)continue; if(maxP>0&&p>maxP)continue;
            filtered.add(l); if(p>0){sum+=p;count++;min=Math.min(min,p);max=Math.max(max,p);} if(sb.length()<9000)sb.append(l.title).append("\\n").append(l.price).append(" تومان | ").append(l.sqm).append(" متر | ").append(l.rooms).append(" خواب | ").append(l.pricePerSqm).append(" تومان/متر\\n\\n"); }
        rows=filtered; if(rows.isEmpty())summary.setText("آگهی‌ای مطابق فیلترها پیدا نشد."); else summary.setText("تعداد: "+rows.size()+"\\nمیانگین قیمت/متر: "+fmt(count>0?sum/count:0)+"\\nحداقل: "+fmt(min==Double.MAX_VALUE?0:min)+"\\nحداکثر: "+fmt(max));
        results.setText(sb.toString());
    }

    double parseFilter(EditText e){return num(e.getText().toString().trim());}
    String fmt(double x){return nf.format(Math.round(x));}
    String esc(String s){if(s==null)return "";return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;").replace("'","&apos;");}
    String col(int n){StringBuilder b=new StringBuilder();n++;while(n>0){int r=(n-1)%26;b.insert(0,(char)('A'+r));n=(n-1)/26;}return b.toString();}
    String cell(String ref,String value){return "<c r=\""+ref+"\" t=\"inlineStr\"><is><t xml:space=\"preserve\">"+esc(value==null?"":value)+"</t></is></c>";}

    void exportXls(){
        if(rows.isEmpty()){Toast.makeText(this,"ابتدا جستجو کنید",Toast.LENGTH_SHORT).show();return;}
        Intent in=new Intent(Intent.ACTION_CREATE_DOCUMENT);in.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");in.putExtra(Intent.EXTRA_TITLE,"divar_price_analysis.xlsx");startActivityForResult(in,900);
    }
    void writeEntry(ZipOutputStream z,String name,String text)throws Exception{z.putNextEntry(new ZipEntry(name));z.write(text.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
    String buildSheet(){
        String[] heads={"عنوان","لینک آگهی","قیمت کل","ودیعه/رهن","اجاره","متراژ","تعداد خواب","طبقه","تعداد طبقات","سال ساخت","پارکینگ","آسانسور","انباری","قیمت هر متر","آدرس","تاریخ آگهی","تاریخ بروزرسانی","نردبان/ویژه","نوع ملک","مشاور/آژانس","توضیحات"};
        int lastRow=rows.size()+1;StringBuilder s=new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/><selection pane=\"bottomLeft\" activeCell=\"A2\" sqref=\"A2\"/></sheetView></sheetViews><sheetData><row r=\"1\">");
        for(int i=0;i<heads.length;i++)s.append(cell(col(i)+"1",heads[i]));s.append("</row>");
        for(int r=0;r<rows.size();r++){s.append("<row r=\"").append(r+2).append("\">");String[] vals=rows.get(r).csv();for(int c=0;c<vals.length;c++)s.append(cell(col(c)+(r+2),vals[c]));s.append("</row>");}
        return s.append("</sheetData><autoFilter ref=\"A1:U").append(lastRow).append("\"/><pageMargins left=\"0.25\" right=\"0.25\" top=\"0.5\" bottom=\"0.5\" header=\"0\" footer=\"0\"/></worksheet>").toString();
    }

    @Override protected void onActivityResult(int r,int c,Intent d){
        super.onActivityResult(r,c,d);if(r==900&&c==RESULT_OK&&d!=null){
            try(OutputStream out=getContentResolver().openOutputStream(d.getData())){
                ZipOutputStream z=new ZipOutputStream(out);
                String types="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/></Types>";
                String rels="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";
                String wb="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"آگهی‌ها\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";
                String wbRels="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/></Relationships>";
                writeEntry(z,"[Content_Types].xml",types);writeEntry(z,"_rels/.rels",rels);writeEntry(z,"xl/workbook.xml",wb);writeEntry(z,"xl/_rels/workbook.xml.rels",wbRels);writeEntry(z,"xl/worksheets/sheet1.xml",buildSheet());z.finish();z.close();
                Toast.makeText(this,"فایل Excel با "+rows.size()+" آگهی و فیلتر ستونی ذخیره شد",Toast.LENGTH_LONG).show();
            }catch(Exception e){Toast.makeText(this,"خطا در ذخیره Excel: "+e.getMessage(),Toast.LENGTH_LONG).show();}
        }
    }
}
