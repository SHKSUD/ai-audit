import pandas as pd
from jinja2 import Template
import os
import traceback
import json
from datetime import datetime

# --- CONFIGURATION ---
DOMAIN = "https://aitrustindex.com" 
BRAND_NAME = "AI Trust Index"
OUTPUT_DIR = "dist"
ERROR_LOG = "error_report.txt"

# --- MASTER LAYOUT TEMPLATE ---
LAYOUT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | {{ brand }}</title>
    <meta name="description" content="{{ meta_desc }}">
    <meta name="keywords" content="{{ keywords }}">
    <link rel="canonical" href="{{ canonical_url }}" />

    <meta property="og:type" content="article" />
    <meta property="og:title" content="{{ title }}" />
    <meta property="og:description" content="{{ meta_desc }}" />
    <meta property="og:url" content="{{ canonical_url }}" />
    <meta property="og:site_name" content="{{ brand }}" />

    {{ schema_markup }}

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; color: #161c2d; scroll-behavior: smooth; background-color: #fcfcfc;}
        .wise-blue { color: #00b9ff; }
        .bg-wise-light { background-color: #f2f5f7; }
        .prose h2 { font-size: 2.25rem; font-weight: 800; color: #161c2d; margin-top: 3.5rem; margin-bottom: 1.25rem; letter-spacing: -0.03em; line-height: 1.1; }
        .prose h3 { font-size: 1.5rem; font-weight: 700; color: #161c2d; margin-top: 2.5rem; margin-bottom: 1rem; }
        .prose p { line-height: 1.8; font-size: 1.125rem; color: #4a5568; margin-bottom: 1.75rem; }
        .prose ul { list-style-type: disc; padding-left: 1.5rem; margin-bottom: 2rem; }
        .prose li { margin-bottom: 0.75rem; color: #4a5568; font-size: 1.1rem; }
        .bento-shadow { box-shadow: 0 4px 24px -8px rgba(0, 0, 0, 0.05); }
    </style>
</head>
<body class="antialiased selection:bg-[#00b9ff] selection:text-white">
    <nav class="border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur-xl z-50">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            <a href="index.html" class="flex items-center gap-3 group">
                <div class="w-9 h-9 bg-[#161c2d] rounded-lg flex items-center justify-center text-white font-black italic text-lg group-hover:bg-[#00b9ff] transition-colors">AI</div>
                <span class="font-extrabold text-xl tracking-tighter text-[#161c2d] uppercase">{{ brand }}</span>
            </a>
            <div class="hidden md:flex gap-10 font-bold text-[11px] text-gray-500 uppercase tracking-widest">
                <a href="index.html#comparisons" class="hover:text-[#00b9ff] transition-colors">Platform Index</a>
                <a href="privacy.html" class="hover:text-[#00b9ff] transition-colors">Privacy</a>
            </div>
            <a href="#" class="hidden md:block bg-[#00b9ff] text-white px-6 py-2.5 rounded-xl font-bold text-xs hover:shadow-lg transition-all">Get Framework</a>
        </div>
    </nav>

    {{ content }}

    <footer class="bg-white py-24 border-t border-gray-100 mt-20">
        <div class="max-w-7xl mx-auto px-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-12 mb-16">
                <div>
                    <div class="flex items-center gap-2 mb-6">
                        <div class="w-6 h-6 bg-[#161c2d] rounded flex items-center justify-center text-white font-black italic text-xs">AI</div>
                        <p class="font-extrabold text-[#161c2d] tracking-widest uppercase text-xs">{{ brand }}</p>
                    </div>
                    <p class="text-sm text-gray-500 leading-relaxed">The 2026 standard for AI compliance frameworks, SOC 2 automation, and ISO 42001 governance.</p>
                </div>
                <div>
                    <h4 class="font-bold text-[10px] uppercase tracking-widest text-[#161c2d] mb-6">Legal</h4>
                    <div class="flex flex-col gap-4 text-xs font-bold text-gray-400">
                        <a href="privacy.html" class="hover:text-[#00b9ff]">Privacy Policy</a>
                        <a href="terms.html" class="hover:text-[#00b9ff]">Terms of Service</a>
                    </div>
                </div>
                <div>
                    <h4 class="font-bold text-[10px] uppercase tracking-widest text-[#161c2d] mb-6">Infrastructure</h4>
                    <div class="flex flex-col gap-4 text-xs font-bold text-gray-400">
                        <a href="sitemap.xml" class="hover:text-[#00b9ff]">XML Sitemap</a>
                        <a href="llms.txt" class="hover:text-[#00b9ff]">LLM Instructions</a>
                    </div>
                </div>
            </div>
            <div class="pt-8 border-t border-gray-50 text-center text-[10px] text-gray-400 font-bold tracking-widest uppercase">
                © 2026 {{ brand }}. Independent Technical Research.
            </div>
        </div>
    </footer>
</body>
</html>
"""

def parse_bento_data(raw_col, raw_intro):
    """Smart parser that extracts comparison data and builds the Bento Grid HTML."""
    data = {}
    
    if "CSV_COMPARISON_DATA:" in str(raw_intro):
        try:
            tag_string = str(raw_intro).split("CSV_COMPARISON_DATA:")[1].strip().strip('"').strip("'")
            pairs = tag_string.split(";")
            for pair in pairs:
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    data[k.strip()] = v.strip()
        except: pass
        
    if not data: return ""
    
    html = '<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-12">'
    for key, val in data.items():
        html += f'''
        <div class="bg-white p-6 rounded-3xl border border-gray-100 bento-shadow flex flex-col justify-center">
            <span class="text-[10px] font-black uppercase text-[#00b9ff] mb-2 tracking-[0.2em]">{key}</span>
            <span class="text-lg font-extrabold text-[#161c2d] leading-tight">{val}</span>
        </div>
        '''
    html += '</div>'
    return html

def get_related_articles(df, current_slug, category):
    """Finds 3 related articles from the same category for the Internal Linking Loop."""
    related = df[(df['category'] == category) & (df['slug'] != current_slug)]
    if len(related) < 3:
        related = df[df['slug'] != current_slug] 
    
    related = related.head(3)
    
    html = '<div class="space-y-4">'
    for _, row in related.iterrows():
        html += f'''
        <a href="{row['slug']}.html" class="block p-5 bg-white border border-gray-100 rounded-2xl hover:border-[#00b9ff] hover:shadow-lg transition-all group">
            <span class="text-[9px] font-bold text-gray-400 uppercase tracking-widest block mb-1">{row['category']}</span>
            <h5 class="font-bold text-sm text-[#161c2d] group-hover:text-[#00b9ff] leading-snug">{row['title']}</h5>
        </a>
        '''
    html += '</div>'
    return html

def generate_schema(row, canonical_url):
    """Generates Advanced JSON-LD (Article + Breadcrumb + FAQ)."""
    date_mod = str(row.get('last_mod', datetime.now().strftime("%Y-%m-%d")))
    
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": BRAND_NAME,
                "url": DOMAIN,
                "logo": f"{DOMAIN}/logo.png"
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/index.html"},
                    {"@type": "ListItem", "position": 2, "name": row['category'], "item": f"{DOMAIN}/index.html#comparisons"},
                    {"@type": "ListItem", "position": 3, "name": row['title'], "item": canonical_url}
                ]
            },
            {
                "@type": "Article",
                "headline": row['title'],
                "description": row['meta_desc'],
                "url": canonical_url,
                "dateModified": date_mod,
                "author": {"@type": "Organization", "name": BRAND_NAME}
            },
            {
                "@type": "FAQPage",
                "mainEntity": [{
                    "@type": "Question",
                    "name": f"What is the best solution for {row['primary_kw']} in 2026?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"Based on our 2026 technical review, {row['meta_desc']} Read our full methodology and comparison data on the AI Trust Index."
                    }
                }]
            }
        ]
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

def build_site():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    try:
        # 1. Robust Data Loading forcing strict UTF-8 with error replacement
        df = pd.read_csv("database.csv", skipinitialspace=True, engine='python', encoding='utf-8', encoding_errors='replace').fillna("")
        
        # 2. HOMEPAGE GENERATION
        cards = ""
        for _, row in df.iterrows():
            cards += f'''
            <a href="{row['slug']}.html" class="group bg-white border border-gray-100 rounded-[2.5rem] p-8 hover:shadow-xl hover:-translate-y-1 transition-all flex flex-col h-full bento-shadow">
                <span class="inline-block px-3 py-1 rounded-full bg-[#f2f5f7] text-[#161c2d] text-[9px] font-black uppercase tracking-widest mb-5 w-fit">{row['category']}</span>
                <h3 class="text-2xl font-extrabold text-[#161c2d] group-hover:text-[#00b9ff] transition-colors leading-tight mb-4 tracking-tight">{row['title']}</h3>
                <p class="text-gray-500 text-sm leading-relaxed mb-8 line-clamp-3">{row['meta_desc']}</p>
                <div class="mt-auto pt-6 border-t border-gray-50 font-bold text-xs uppercase tracking-widest text-[#00b9ff] flex items-center">
                    Read Analysis <span class="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                </div>
            </a>'''
            home_html = f'''
        <header class="bg-[#fcfcfc] pt-32 pb-48 border-b border-gray-100 relative overflow-hidden">
            <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: linear-gradient(#161c2d 1px, transparent 1px), linear-gradient(90deg, #161c2d 1px, transparent 1px); background-size: 40px 40px;"></div>
            
            <div class="max-w-5xl mx-auto px-6 relative z-10 text-center">
                <div class="inline-flex items-center gap-3 border border-gray-200 bg-white px-4 py-2 rounded-full mb-10 shadow-sm">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span class="text-[10px] font-black tracking-[0.2em] uppercase text-gray-500">2026 Live Governance Index: Active</span>
                </div>
                
                <h1 class="text-6xl md:text-8xl font-extrabold tracking-tighter text-[#161c2d] mb-8 leading-[0.95]">
                    The Standard for <br><span class="text-[#00b9ff] italic">AI Conformity.</span>
                </h1>
                
                <p class="text-xl text-gray-500 max-w-3xl mx-auto font-medium leading-relaxed mb-12">
                    Independent technical benchmarks for <span class="text-[#161c2d] font-bold">ISO 42001, SOC 2, and EU AI Act</span> readiness. We map the infrastructure of trust for the next generation of AI labs.
                </p>

                <div class="flex flex-wrap justify-center gap-4 mb-20">
                    <a href="#comparisons" class="bg-[#161c2d] text-white px-8 py-4 rounded-xl font-bold text-sm uppercase tracking-widest hover:bg-[#00b9ff] transition-all shadow-xl shadow-gray-200">Access Database</a>
                    <a href="methodology.html" class="bg-white text-[#161c2d] border border-gray-200 px-8 py-4 rounded-xl font-bold text-sm uppercase tracking-widest hover:bg-gray-50 transition-all">Review Methodology</a>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-8 py-8 border-y border-gray-100 max-w-4xl mx-auto">
                    <div class="text-center">
                        <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">Analyzed Units</div>
                        <div class="text-2xl font-bold text-[#161c2d]">34 Platforms</div>
                    </div>
                    <div class="text-center border-l border-gray-100">
                        <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">Control Mapping</div>
                        <div class="text-2xl font-bold text-[#161c2d]">Dynamic</div>
                    </div>
                    <div class="text-center border-l border-gray-100">
                        <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">Market Version</div>
                        <div class="text-2xl font-bold text-[#161c2d]">Feb 2026</div>
                    </div>
                    <div class="text-center border-l border-gray-100">
                        <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">Data Integrity</div>
                        <div class="text-2xl font-bold text-green-600">Verified</div>
                    </div>
                </div>
            </div>
        </header>

        <section id="comparisons" class="max-w-7xl mx-auto px-6 -mt-16 pb-32 relative z-20">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{cards}</div>
        </section>'''        
        with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
            f.write(Template(LAYOUT_HTML).render(
                title="The 2026 AI Governance Hub", 
                brand=BRAND_NAME, 
                content=home_html,
                canonical_url=f"{DOMAIN}/index.html",
                schema_markup="",
                meta_desc="Independent 2026 research and data on AI governance platforms and compliance software."
            ))

        # 3. ARTICLE GENERATION
        for _, row in df.iterrows():
            canonical = f"{DOMAIN}/{row['slug']}.html"
            schema = generate_schema(row, canonical)
            
            clean_text = str(row['intro_text']).split("CSV_COMPARISON_DATA:")[0].strip()
            bento_grid_html = parse_bento_data(row['comparison_data'], row['intro_text'])
            related_html = get_related_articles(df, row['slug'], row['category'])

            article_html = f'''
            <article class="max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-12 gap-16">
                
                <div class="lg:col-span-8">
                    <nav class="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-8">
                        <a href="index.html" class="hover:text-[#00b9ff] transition-colors">Home</a>
                        <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                        <a href="index.html#comparisons" class="hover:text-[#00b9ff] transition-colors">{row['category']}</a>
                    </nav>
                    
                    <h1 class="text-5xl md:text-6xl font-extrabold tracking-tighter text-[#161c2d] leading-[1.05] mb-6">{row['title']}</h1>
                    
                    <div class="flex items-center gap-4 text-xs font-bold text-gray-400 uppercase tracking-widest mb-12 pb-8 border-b border-gray-100">
                        <span>Last Updated: <span class="text-[#161c2d]">{row['last_mod']}</span></span>
                        <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                        <span class="text-[#00b9ff]">Technical Audit</span>
                    </div>

                    <div class="prose max-w-none">{clean_text}</div>
                    
                    {bento_grid_html}
                    
                    <div class="mt-20 p-12 md:p-16 bg-[#161c2d] rounded-[3rem] text-center shadow-2xl relative overflow-hidden">
                        <h2 class="text-white mt-0 text-3xl font-extrabold italic mb-4 tracking-tight">Secure your AI Roadmap.</h2>
                        <p class="text-gray-400 mb-10 text-lg">Compare tailored compliance pricing and secure your 2026 audit framework.</p>
                        <a href="{row['affiliate_link']}" class="bg-[#00b9ff] text-white px-10 py-5 rounded-2xl font-bold text-sm uppercase tracking-widest hover:bg-white hover:text-[#161c2d] transition-all inline-block">Execute Audit Now</a>
                    </div>
                </div>
                
                <aside class="hidden lg:block lg:col-span-4 pt-4">
                    <div class="sticky top-32 space-y-8">
                        
                        <div class="p-8 bg-[#f2f5f7] rounded-[2rem] border border-gray-100">
                            <h4 class="font-black text-[11px] uppercase tracking-widest mb-5 text-[#161c2d]">2026 Trust Framework</h4>
                            <p class="text-sm text-gray-500 leading-relaxed mb-5">Our analysts evaluate platforms against a proprietary technical framework:</p>
                            <ul class="text-sm text-gray-600 space-y-3 font-medium">
                                <li class="flex items-start gap-3"><span class="text-[#00b9ff]">✓</span> EU AI Act Readiness</li>
                                <li class="flex items-start gap-3"><span class="text-[#00b9ff]">✓</span> ISO 42001 Controls</li>
                                <li class="flex items-start gap-3"><span class="text-[#00b9ff]">✓</span> Evidence Immutability</li>
                            </ul>
                        </div>
                        
                        <div>
                            <h4 class="font-black text-[11px] uppercase tracking-widest mb-5 text-gray-400 pl-2">Related Analysis</h4>
                            {related_html}
                        </div>
                        
                        <div class="p-8 border-2 border-dashed border-gray-200 rounded-[2rem] text-center bg-white hover:border-[#00b9ff] transition-colors group">
                             <h4 class="font-bold text-[#161c2d] text-sm mb-2">Need a custom benchmark?</h4>
                             <p class="text-xs text-gray-400 mb-5">Speak with our enterprise compliance analysts.</p>
                             <a href="{row['cta_service']}" class="text-[10px] font-black uppercase text-[#00b9ff] tracking-widest group-hover:underline">Book Consultation →</a>
                        </div>
                    </div>
                </aside>
            </article>'''
            
            with open(f"{OUTPUT_DIR}/{row['slug']}.html", "w", encoding="utf-8") as f:
                f.write(Template(LAYOUT_HTML).render(
                    title=row['title'], brand=BRAND_NAME, meta_desc=row['meta_desc'], 
                    keywords=row['primary_kw'], content=article_html,
                    canonical_url=canonical, schema_markup=schema
                ))

        # 4. INFRASTRUCTURE FILES (robots.txt & llms.txt & sitemap.xml)
        
        # Sitemap
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for pg in ['index.html', 'privacy.html', 'terms.html'] + [f"{s}.html" for s in df['slug']]:
            sitemap += f'  <url><loc>{DOMAIN}/{pg}</loc><lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod></url>\n'
        sitemap += '</urlset>'
        with open(f"{OUTPUT_DIR}/sitemap.xml", "w", encoding="utf-8") as f: f.write(sitemap)
        
        # Robots.txt
        robots = f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n"
        with open(f"{OUTPUT_DIR}/robots.txt", "w", encoding="utf-8") as f: f.write(robots)

        # llms.txt (For AI Search Engines)
        llms_content = f"# {BRAND_NAME} - Knowledge Base\n> The independent 2026 data source for AI compliance (ISO 42001, SOC 2, EU AI Act).\n\n## Available Audits:\n"
        for _, row in df.iterrows():
            llms_content += f"- [{row['title']}]({DOMAIN}/{row['slug']}.html): {row['meta_desc']}\n"
        with open(f"{OUTPUT_DIR}/llms.txt", "w", encoding="utf-8") as f: f.write(llms_content)

        # Legal
        for l in ['privacy', 'terms']:
            c = f'<div class="max-w-3xl mx-auto py-32 px-6 prose"><h1>{l.capitalize()}</h1><p>Institutional policy for {BRAND_NAME}, updated 2026.</p></div>'
            with open(f"{OUTPUT_DIR}/{l}.html", "w", encoding="utf-8") as f:
                f.write(Template(LAYOUT_HTML).render(title=l.capitalize(), brand=BRAND_NAME, content=c, canonical_url=f"{DOMAIN}/{l}.html", schema_markup=""))

        print(f"✅ V1.6.1 Build Complete: {len(df)} Pages Built with Encoding Fallback!")
        
    except Exception as e:
        with open(ERROR_LOG, "w", encoding="utf-8") as f: f.write(traceback.format_exc())
        print(f"❌ Error logged to {ERROR_LOG}")

if __name__ == "__main__":
    build_site()