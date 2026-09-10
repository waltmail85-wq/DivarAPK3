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

public class MainActivity extends Activity {
    EditText city, area, minSqm, maxSqm, minPsm, maxPsm;
    Spinner category;
    TextView summary, results;
    WebView web;
    ArrayList<String[]> rows = new ArrayList<>();
    final String[] cats = {"buy-apartment", "rent-apartment", "buy-house-villa"};
    final NumberFormat nf = NumberFormat.getIntegerInstance(Locale.US);

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(12,12,12,12);
        ScrollView topScroll = new ScrollView(this);
        LinearLayout form = new LinearLayout(this); form.setOrientation(LinearLayout.VERTICAL);
        city = edit("شهر", "tabriz"); area = edit("محله", "نصر");
        category = new Spinner(this); category.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, cats));
        form.addView(city); form.addView(area); form.addView(category);
        LinearLayout r1 = new LinearLayout(this); r1.addView(editTo(r1,"حداقل متر", "")); r1.addView(editTo(r1,"حداکثر متر", "")); form.addView(r1);
        LinearLayout r2 = new LinearLayout(this); r2.addView(editTo(r2,"حداقل قیمت/متر", "")); r2.addView(editTo(r2,"حداکثر قیمت/متر", "")); form.addView(r2);
        minSqm = (EditText) r1.getChildAt(0); maxSqm=(EditText)r1.getChildAt(1); minPsm=(EditText)r2.getChildAt(0); maxPsm=(EditText)r2.getChildAt(1);
        Button search = new Button(this); search.setText("جستجو و تحلیل"); search.setOnClickListener(v -> loadDivar()); form.addView(search);
        summary = new TextView(this); summary.setText("آماده جستجو"); summary.setTextSize(16); summary.setPadding(4,8,4,8); form.addView(summary);
        Button export = new Button(this); export.setText("خروجی Excel"); export.setOnClickListener(v -> exportXls()); form.addView(export);
        topScroll.addView(form); root.addView(topScroll, new LinearLayout.LayoutParams(-1,0,0.45f));
        results = new TextView(this); results.setTextSize(14); ScrollView rs=new ScrollView(this); rs.addView(results); root.addView(rs,new LinearLayout.LayoutParams(-1,0,0.25f));
        web = new WebView(this); WebSettings s=web.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setUserAgentString("Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/125 Mobile Safari/537.36"); web.setWebViewClient(new WebViewClient()); root.addView(web,new LinearLayout.LayoutParams(-1,0,0.30f));
        setContentView(root);
    }
    EditText edit(String hint,String value){ EditText e=new EditText(this); e.setHint(hint); e.setText(value); e.setInputType(2); e.setSingleLine(); return e; }
    EditText editTo(LinearLayout p,String h,String v){ EditText e=edit(h,v); e.setLayoutParams(new LinearLayout.LayoutParams(0,-2,1)); return e; }
    void loadDivar(){
        String c=city.getText().toString().trim(); String a=area.getText().toString().trim(); String cat=cats[category.getSelectedItemPosition()];
        String url="https://divar.ir/s/"+Uri.encode(c)+"/"+cat+(a.isEmpty()?"":"?q="+Uri.encode(a)); rows.clear(); summary.setText("در حال بارگذاری دیوار..."); results.setText(""); web.loadUrl(url);
        web.postDelayed(() -> collect(0), 8000);
    }
    void collect(int n){ if(n>=10){ parsePage(); return; } web.evaluateJavascript("window.scrollTo(0,document.body.scrollHeight);", x -> web.postDelayed(() -> collect(n+1),700)); }
    String unescape(String s){ return s.replace("\\\"","\"").replace("\\n","\n").replace("\\u003C","<").replace("\\u003E",">").replace("\\u0026","&"); }
    double num(String s){ try { return Double.parseDouble(s.replace(",","").replace("٬","").replace("٫",".")); } catch(Exception e){ return 0; } }
    double firstNumber(String text, String regex){ Matcher m=Pattern.compile(regex).matcher(text); return m.find()?num(m.group(1)):0; }
    void parsePage(){
        String js="(function(){let out=[]; let seen=new Set(); document.querySelectorAll('a').forEach(a=>{let h=a.href||''; if(h.includes('/v/')){let x=(a.innerText||a.textContent||'').trim(); if(!seen.has(h)){seen.add(h);out.push(JSON.stringify({h:h,t:x}));}}}); return JSON.stringify(out);})()";
        web.evaluateJavascript(js, val -> {
            String t=unescape(val); Matcher m=Pattern.compile("\\{\\\"h\\\":\\\"(https://divar\\.ir/v/[^\\\"]+)\\\",\\\"t\\\":\\\"(.*?)\\\"\\}").matcher(t);
            LinkedHashMap<String,String> items=new LinkedHashMap<>(); while(m.find()) items.put(m.group(1),m.group(2));
            if(items.isEmpty()){ summary.setText("آگهی‌ها در صفحه دیده می‌شوند ولی لینک آن‌ها استخراج نشد؛ ساختار دیوار تغییر کرده است."); return; }
            double minS=parseFilter(minSqm), maxS=parseFilter(maxSqm), minP=parseFilter(minPsm), maxP=parseFilter(maxPsm);
            rows.clear(); double sum=0,min=Double.MAX_VALUE,max=0; int i=1;
            StringBuilder sb=new StringBuilder();
            for(Map.Entry<String,String> e:items.entrySet()){
                String text=e.getValue().replace("\\r"," ").replace("\\t"," ");
                double sqm=firstNumber(text,"(?:^|\\n| )([0-9]{2,4})\\s*(?:متر|مترمربع|m²|m2)");
                double price=firstNumber(text,"(?:قیمت|تومان|\\n)\\s*([0-9۰-۹,٬]+)");
                double psm=0; Matcher pm=Pattern.compile("([0-9۰-۹,٬]+)\\s*(?:تومان\\s*)?(?:/|به ازای)\\s*(?:متر|m²)").matcher(text); if(pm.find()) psm=num(pm.group(1));
                if(psm==0 && sqm>0 && price>0) psm=price/sqm;
                if((minS>0 && sqm>0 && sqm<minS)||(maxS>0 && sqm>maxS)||(minP>0 && psm>0 && psm<minP)||(maxP>0 && psm>maxP)) continue;
                rows.add(new String[]{String.valueOf(i++),e.getKey(),sqm>0?fmt(sqm):"",price>0?fmt(price):"",psm>0?fmt(psm):""});
                if(psm>0){sum+=psm; if(psm<min)min=psm; if(psm>max)max=psm;}
                if(rows.size()>=80) break;
            }
            for(String[] r:rows) sb.append(r[0]).append(" - ").append(r[3]).append(" تومان | ").append(r[2]).append(" متر | ").append(r[4]).append(" تومان/متر\n").append(r[1]).append("\n\n");
            results.setText(sb.toString());
            if(rows.isEmpty()){ summary.setText("آگهی پیدا شد اما با فیلترهای شما موردی باقی نماند."); }
            else { double avg=sum/(sum>0?countPsm():1); summary.setText("تعداد: "+rows.size()+"\nمیانگین قیمت/متر: "+fmt(avg)+"\nحداقل: "+fmt(min==Double.MAX_VALUE?0:min)+"\nحداکثر: "+fmt(max)); }
        });
    }
    int countPsm(){ int c=0; for(String[] r:rows) if(!r[4].isEmpty()) c++; return c; }
    double parseFilter(EditText e){ try{return num(e.getText().toString().trim());}catch(Exception x){return 0;} }
    String fmt(double x){ return nf.format(Math.round(x)); }
    void exportXls(){
        if(rows.isEmpty()){ Toast.makeText(this,"ابتدا جستجو کنید",Toast.LENGTH_SHORT).show(); return; }
        Intent in=new Intent(Intent.ACTION_CREATE_DOCUMENT); in.setType("application/vnd.ms-excel"); in.putExtra(Intent.EXTRA_TITLE,"divar_price_analysis.xls"); startActivityForResult(in,900);
    }
    @Override protected void onActivityResult(int r,int c,Intent d){ super.onActivityResult(r,c,d); if(r==900&&c==RESULT_OK&&d!=null){ try(OutputStream o=getContentResolver().openOutputStream(d.getData())){ StringBuilder h=new StringBuilder("<html><meta charset='UTF-8'><table border='1'><tr><th>#</th><th>Link</th><th>Area</th><th>Price</th><th>Price/m2</th></tr>"); for(String[] x:rows) h.append("<tr><td>").append(x[0]).append("</td><td>").append(x[1]).append("</td><td>").append(x[2]).append("</td><td>").append(x[3]).append("</td><td>").append(x[4]).append("</td></tr>"); h.append("</table></html>"); o.write(h.toString().getBytes(StandardCharsets.UTF_8)); Toast.makeText(this,"فایل ذخیره شد",Toast.LENGTH_LONG).show(); }catch(Exception e){ Toast.makeText(this,"خطا در ذخیره: "+e.getMessage(),Toast.LENGTH_LONG).show(); }} }
}
