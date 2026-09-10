package com.divar.pricemeter;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.view.Gravity;
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
        web.postDelayed(() -> collect(0), 7000);
    }
    void collect(int n){ if(n>=12){ parsePage(); return; } web.evaluateJavascript("window.scrollTo(0,document.body.scrollHeight);", x -> web.postDelayed(() -> collect(n+1),500)); }
    void parsePage(){
        web.evaluateJavascript("(function(){let out=[]; document.querySelectorAll('a[href*=/v/]').forEach(a=>out.push(a.innerText+'\\n'+a.href)); return JSON.stringify(out);})()", val -> {
            String t=val; t=t.replace("\\\"", "\"").replace("\\n","\n"); Matcher m=Pattern.compile("https://divar\\.ir/v/[^\\\" ]+").matcher(t); LinkedHashSet<String> links=new LinkedHashSet<>(); while(m.find()) links.add(m.group());
            if(links.isEmpty()){ summary.setText("آگهی قابل استخراج پیدا نشد؛ ممکن است دیوار نیاز به ورود یا تغییر ساختار داشته باشد."); return; }
            rows.clear(); int i=1; for(String link:links){ rows.add(new String[]{String.valueOf(i++),link,"","",""}); if(rows.size()>=80) break; }
            StringBuilder sb=new StringBuilder(); for(String[] r:rows) sb.append(r[0]).append(" - ").append(r[1]).append("\n"); results.setText(sb.toString()); summary.setText("تعداد آگهی‌های پیدا شده: "+rows.size()+"\nبرای تحلیل دقیق‌تر، لینک‌ها و متن آگهی‌ها در نسخه بعدی قابل تکمیل است.");
        });
    }
    void exportXls(){
        if(rows.isEmpty()){ Toast.makeText(this,"ابتدا جستجو کنید",Toast.LENGTH_SHORT).show(); return; }
        Intent in=new Intent(Intent.ACTION_CREATE_DOCUMENT); in.setType("application/vnd.ms-excel"); in.putExtra(Intent.EXTRA_TITLE,"divar_price_analysis.xls"); startActivityForResult(in,900);
    }
    @Override protected void onActivityResult(int r,int c,Intent d){ super.onActivityResult(r,c,d); if(r==900&&c==RESULT_OK&&d!=null){ try(OutputStream o=getContentResolver().openOutputStream(d.getData())){ StringBuilder h=new StringBuilder("<html><meta charset='UTF-8'><table border='1'><tr><th>#</th><th>Link</th><th>Area</th><th>Price</th><th>Price/m2</th></tr>"); for(String[] x:rows) h.append("<tr>"); for(String[] x:rows) h.append("<td>").append(x[0]).append("</td><td>").append(x[1]).append("</td><td></td><td></td><td></td></tr>"); h.append("</table></html>"); o.write(h.toString().getBytes(StandardCharsets.UTF_8)); Toast.makeText(this,"فایل ذخیره شد",Toast.LENGTH_LONG).show(); }catch(Exception e){ Toast.makeText(this,"خطا در ذخیره: "+e.getMessage(),Toast.LENGTH_LONG).show(); }} }
}
