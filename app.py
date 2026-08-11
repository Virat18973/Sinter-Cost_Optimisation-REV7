import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

from optimizer import (
    TARGETS, FE_LOWER, FE_UPPER,
    get_default_chemistry, load_chemistry_from_excel,
    solve_blend_with_compensation, calculate_cost_breakdown,
    quality_checks, quality_table, redistribute_adjustment,
    what_if_analysis, compute_achieved,
)

st.set_page_config(page_title="Sinter Burden Control", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# PRODUCTION-GRADE INDUSTRIAL THEME
# -----------------------------------------------------------------------------
st.markdown(r"""
<style>
:root{
 --bg:#080d12; --bg2:#0d141b; --panel:#111a22; --panel2:#16212b; --panel3:#1b2833;
 --line:#2a3945; --line2:#344754; --text:#edf3f7; --muted:#8fa0ad; --steel:#4f8fb8;
 --steel2:#78b5d5; --green:#37c77a; --amber:#e6a63a; --orange:#e56d35; --red:#d95757;
 --iron:#4d8ed1; --flux:#43bf7a; --recycle:#e7a73c; --fuel:#dd5b50;
}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;}
.stApp{background:linear-gradient(135deg,#070b10 0%,#0b1218 52%,#0a1116 100%);color:var(--text);}
.block-container{max-width:1780px;padding:.65rem 1rem 2.5rem 1rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#101820,#0d141b);border-right:1px solid #263641;}
[data-testid="stSidebar"]>div:first-child{padding:.8rem .7rem 1.2rem .7rem;}
[data-testid="stSidebar"] .stButton>button{height:36px!important;margin:2px 0!important;background:transparent!important;border:1px solid transparent!important;text-align:left!important;padding-left:12px!important;color:#b7c3cc!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:#17232c!important;border-color:#2d414f!important;color:#fff!important;}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(90deg,#214f6c,#18394e)!important;border:1px solid #356a8a!important;color:#fff!important;box-shadow:inset 3px 0 0 #66a9cd!important;}
.brand{padding:.45rem .3rem .8rem;border-bottom:1px solid #263640;margin-bottom:.6rem;}
.brand-name{font-size:.9rem;font-weight:900;letter-spacing:.04em;color:#f4f7f9;}
.brand-sub{font-size:.59rem;color:#8193a0;margin-top:2px;}
.brand-jv{font-size:.56rem;color:#6fa7c5;margin-top:6px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;}
.nav-head{font-size:.58rem;color:#718491;letter-spacing:.16em;text-transform:uppercase;font-weight:900;margin:1rem .25rem .25rem;}
.side-status{background:#101a22;border:1px solid #273945;border-radius:9px;padding:.6rem;margin-top:1rem;font-size:.63rem;color:#a9b6bf;}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:1px;}
.green{background:#37c77a;box-shadow:0 0 8px #37c77a55}.amber{background:#e6a63a}.red{background:#d95757}
h1{font-size:1.95rem!important;letter-spacing:-.035em;margin-bottom:.1rem!important;}h2{font-size:1.28rem!important;}h3{font-size:1rem!important;}
.eyebrow{font-size:.61rem;letter-spacing:.16em;text-transform:uppercase;color:#6f8797;font-weight:900;}
.sub{font-size:.7rem;color:#8fa0ad;}
.header{display:flex;align-items:flex-end;justify-content:space-between;padding:.15rem .1rem .65rem;border-bottom:1px solid #23333e;margin-bottom:.75rem;}
.header-right{text-align:right;font-size:.62rem;color:#8ea0ac;line-height:1.5;}
.panel{background:linear-gradient(145deg,#111a22,#0f171e);border:1px solid #283945;border-radius:11px;padding:.72rem;box-shadow:0 8px 24px rgba(0,0,0,.12);}
.panel-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:.45rem;}
.panel-title{font-size:.64rem;letter-spacing:.13em;text-transform:uppercase;color:#90a4b1;font-weight:900;}
.panel-accent{color:#6eb4d9;}
.hero{background:linear-gradient(105deg,#121d25,#10202a 60%,#14232c);border:1px solid #304654;border-radius:12px;padding:.75rem .85rem;}
.control-note{font-size:.65rem;color:#8fa0ad;background:#0d151c;border:1px solid #293b47;border-radius:7px;padding:.38rem .5rem;}
.kpi{background:linear-gradient(145deg,#121d25,#10171e);border:1px solid #293b47;border-radius:10px;padding:.7rem .75rem;min-height:95px;position:relative;overflow:hidden;}
.kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--k,#4f8fb8);}
.kpi-label{font-size:.56rem;letter-spacing:.13em;text-transform:uppercase;color:#8297a5;font-weight:900;}.kpi-value{font-size:1.22rem;font-weight:900;margin-top:.3rem;color:#f5f8fa;}.kpi-sub{font-size:.61rem;color:#8395a2;margin-top:.18rem;}.kpi-steel{--k:#4f8fb8}.kpi-green{--k:#37c77a}.kpi-amber{--k:#e6a63a}.kpi-red{--k:#d95757}.kpi-orange{--k:#e56d35}.kpi-cyan{--k:#63b5d8}
.notice{border-radius:8px;padding:.48rem .62rem;font-size:.68rem;font-weight:800;background:#10291f;border:1px solid #245d42;color:#6fe19c;}.notice-warn{background:#2b2415;border-color:#6d5121;color:#f1c56b}.notice-bad{background:#30191b;border-color:#713034;color:#ff8a8a}
.badge{display:inline-flex;align-items:center;gap:5px;border-radius:999px;padding:3px 7px;font-size:.58rem;font-weight:900;border:1px solid #33424c;background:#17212a;color:#aab7c0;}.ok{color:#63df97;background:#10271e;border-color:#275c42}.out{color:#ff8b8b;background:#30191c;border-color:#713035}.warn{color:#f3c76b;background:#2a2213;border-color:#675021}.info{color:#79b9dc;background:#102330;border-color:#29516a}
.table-wrap{border:1px solid #2a3a46;border-radius:8px;overflow:auto;background:#0e151c;}
table.pretty{width:100%;border-collapse:collapse;font-size:.64rem;}table.pretty th{background:#17222b;color:#8fa3af;padding:7px 8px;text-align:left;text-transform:uppercase;letter-spacing:.06em;font-size:.55rem;white-space:nowrap;position:sticky;top:0;}table.pretty td{border-top:1px solid #21313b;padding:7px 8px;color:#dbe4e9;white-space:nowrap;}table.pretty tr:hover td{background:#14202a;}tr.group-iron td:first-child{border-left:3px solid var(--iron)}tr.group-flux td:first-child{border-left:3px solid var(--flux)}tr.group-recycle td:first-child{border-left:3px solid var(--recycle)}tr.group-fuel td:first-child{border-left:3px solid var(--fuel)}tr.total-row td{background:#192630!important;font-weight:900;border-top:2px solid #3a4b56!important;color:#fff!important}
.group-chip{display:inline-block;padding:2px 6px;border-radius:999px;font-size:.54rem;font-weight:900;background:#16232c;border:1px solid #2c404c;}.chip-iron{color:#77b4e5}.chip-flux{color:#63d998}.chip-recycle{color:#efbf63}.chip-fuel{color:#ef8b7f}
.quality-item{background:#101a22;border:1px solid #273944;border-radius:7px;padding:.43rem .5rem;margin-bottom:.32rem;}.quality-top{display:flex;justify-content:space-between;align-items:center;font-size:.62rem;}.quality-val{font-weight:900;color:#f0f4f6;}.quality-target{font-size:.56rem;color:#80929e;margin-top:2px;}.meter{height:5px;background:#26343d;border-radius:99px;margin-top:5px;overflow:hidden}.meter>div{height:100%;border-radius:99px;background:linear-gradient(90deg,#4f8fb8,#37c77a)}.meter.bad>div{background:#d95757}.meter.warn>div{background:#e6a63a}
.right-stack{display:flex;flex-direction:column;gap:.65rem}.mini-row{display:flex;justify-content:space-between;padding:.36rem 0;border-bottom:1px solid #24343e;font-size:.61rem}.mini-row:last-child{border-bottom:0}.mini-label{color:#8194a0}.mini-value{font-weight:800;color:#e8eef2}
.empty{background:linear-gradient(145deg,#101920,#0d151b);border:1px dashed #354754;border-radius:11px;padding:1.5rem;text-align:center;color:#8798a4}.empty-title{font-weight:900;color:#dbe4e9;margin-bottom:.25rem}.empty-sub{font-size:.68rem}
.stButton>button{border-radius:7px!important;background:#15212a!important;border:1px solid #2c414e!important;color:#e7eef2!important;font-weight:800!important;font-size:.67rem!important;min-height:34px!important}.stButton>button:hover{border-color:#4f8fb8!important;background:#1b2a35!important}.stButton>button[kind="primary"]{background:linear-gradient(135deg,#2e78ad,#22587f)!important;border-color:#4d93bd!important}
[data-testid="stDataEditor"]{border:1px solid #2a3b46;border-radius:8px;overflow:hidden;}.stSlider label{font-size:.65rem!important;color:#aab7c0!important}.stSlider [data-baseweb="slider"] div{height:4px;}.stFileUploader{font-size:.65rem!important;}
div[data-baseweb="tab-list"]{background:#0f171e;border:1px solid #263843;border-radius:8px;padding:3px;gap:2px}button[data-baseweb="tab"]{font-size:.62rem!important;color:#8fa0ad!important;border-radius:6px!important}button[data-baseweb="tab"][aria-selected="true"]{background:#1b2b36!important;color:#fff!important}
hr{border-color:#263640!important}.footer{margin-top:1.5rem;border-top:1px solid #1f303a;padding-top:.5rem;font-size:.55rem;color:#62737e;text-align:right}
</style>
""", unsafe_allow_html=True)

GROUP_ORDER=["Iron_ore","Flux","Recycle","Fuel"]
GROUP_LABEL={"Iron_ore":"Iron Ore","Flux":"Flux","Recycle":"Recycle","Fuel":"Fuel"}
GROUP_COLORS={"Iron_ore":"#4d8ed1","Flux":"#43bf7a","Recycle":"#e7a73c","Fuel":"#dd5b50"}

# -----------------------------------------------------------------------------
# STATE
# -----------------------------------------------------------------------------
def set_dataset(df, source):
    st.session_state.df=df.copy(); st.session_state.source_name=source
    st.session_state.availability={m:True for m in df.index}
    st.session_state.result=None; st.session_state.previous_cost=None
    st.session_state.inputs_changed=False; st.session_state.manual_base=None
    st.session_state.manual_adjusted=None; st.session_state.what_if=None
    st.session_state.run_count=0

if "df" not in st.session_state: set_dataset(get_default_chemistry(),"Built-in Master Chemistry")
for k,v in {"nav":"Dashboard","result":None,"previous_cost":None,"inputs_changed":False,"manual_base":None,"manual_adjusted":None,"what_if":None,"run_count":0}.items():
    if k not in st.session_state: st.session_state[k]=v

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def active_df():
    df=st.session_state.df.copy()
    for m in df.index:
        if not st.session_state.availability.get(m,True): df.loc[m,"Available_Tonnes"]=0
    return df

def quality_status(achieved):
    if achieved is None:return True,[]
    c=quality_checks(achieved,TARGETS); failed=[k for k,v in c.items() if not v]
    return not failed,failed

def chip(group):
    g=GROUP_LABEL.get(group,group); cls={"Iron_ore":"chip-iron","Flux":"chip-flux","Recycle":"chip-recycle","Fuel":"chip-fuel"}.get(group,"")
    return f'<span class="group-chip {cls}">{g}</span>'

def pretty_table(df, money_cols=None, status_col=None):
    money_cols=money_cols or set(); cols=list(df.columns); out=[]
    for _,row in df.iterrows():
        total=str(row.get("Material",""))=="TOTAL"; group=str(row.get("Group",""))
        cls="total-row" if total else {"Iron_ore":"group-iron","Flux":"group-flux","Recycle":"group-recycle","Fuel":"group-fuel"}.get(group,"")
        cells=[]
        for c in cols:
            v=row[c]
            if pd.isna(v): v=""
            if c=="Group" and v!="": v=chip(str(row[c]))
            elif c in money_cols and v!="": v=f"₹{float(v):,.2f}"
            elif isinstance(v,(float,int)) and not isinstance(v,bool): v=f"{float(v):,.2f}"
            if status_col==c:
                s=str(v); low=s.lower(); cl="ok" if any(x in low for x in ["ok","available","optimal","feasible"]) else "out" if any(x in low for x in ["out","unavailable","critical","no"]) else "warn"
                v=f'<span class="badge {cl}">● {s}</span>'
            cells.append(f"<td>{v}</td>")
        out.append(f'<tr class="{cls}">'+"".join(cells)+"</tr>")
    head="".join(f"<th>{c}</th>" for c in cols)
    return f'<div class="table-wrap"><table class="pretty"><thead><tr>{head}</tr></thead><tbody>'+"".join(out)+"</tbody></table></div>"

def breakdown(blend,df):
    bd,cost,burden=calculate_cost_breakdown(blend,df)
    bd["_o"]=bd["Group"].map({g:i for i,g in enumerate(GROUP_ORDER)}).fillna(99)
    bd=bd.sort_values(["_o","Material"]).drop(columns="_o")
    total=pd.DataFrame([{"Material":"TOTAL","Group":"","kg/t":burden,"% of Burden":100.0,"Cost Rs/t":cost,"% of Cost":100.0}])
    return pd.concat([bd,total],ignore_index=True),cost,burden

def run_optimizer(reference_blend=None):
    prev=st.session_state.result["cost"] if st.session_state.result else None
    res=solve_blend_with_compensation(active_df(),1000,TARGETS,baseline_blend=reference_blend)
    st.session_state.previous_cost=prev
    st.session_state.result={"status":res[0],"blend":res[1],"cost":res[2],"achieved":res[3],"diagnostics":res[4],"fallback":res[5],"df":active_df().copy()}
    st.session_state.inputs_changed=False; st.session_state.manual_base=res[1].copy() if res[1] else None; st.session_state.manual_adjusted=res[1].copy() if res[1] else None
    st.session_state.run_count += 1

def apply_editor_changes(ed):
    changed=False
    for _,r in ed.iterrows():
        m=r["Material"]
        p=float(r["Price (₹/t)"]); stock=float(r["RM Stock (t)"]); av=bool(r["Available"])
        if p!=float(st.session_state.df.loc[m,"Price_Rs_t"]):st.session_state.df.loc[m,"Price_Rs_t"]=p;changed=True
        if stock!=float(st.session_state.df.loc[m,"Available_Tonnes"]):st.session_state.df.loc[m,"Available_Tonnes"]=stock;changed=True
        if av!=bool(st.session_state.availability.get(m,True)):st.session_state.availability[m]=av;changed=True
    if changed:st.session_state.inputs_changed=True

def commercial_editor(key):
    rows=[]
    for m in st.session_state.df.index:
        rows.append({"Material":m,"Group":GROUP_LABEL.get(st.session_state.df.loc[m,"Group"],st.session_state.df.loc[m,"Group"]),"Available":bool(st.session_state.availability.get(m,True)),"Price (₹/t)":float(st.session_state.df.loc[m,"Price_Rs_t"]),"RM Stock (t)":float(st.session_state.df.loc[m,"Available_Tonnes"]),"Tech Max":float(st.session_state.df.loc[m,"Tech_Max"])})
    ed=st.data_editor(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=370,key=key,disabled=["Material","Group","Tech Max"],column_config={"Available":st.column_config.CheckboxColumn("Availability",help="Turn OFF to exclude material from optimization."),"Price (₹/t)":st.column_config.NumberColumn("Price ₹/t",min_value=0,step=1,format="₹ %.0f"),"RM Stock (t)":st.column_config.NumberColumn("RM Stock t",min_value=0,step=100,format="%.0f"),"Tech Max":st.column_config.NumberColumn("Tech Max",format="%.0f")})
    apply_editor_changes(ed)

def quality_panel(achieved):
    q=quality_table(achieved,TARGETS); rows=[]
    for _,r in q.iterrows():
        status=str(r["Status"]); ok=status=="OK"; rows.append(f'<div class="quality-item"><div class="quality-top"><span>{r["KPI"]}</span><span class="badge {"ok" if ok else "out"}">{status}</span></div><div class="quality-target">Achieved <b class="quality-val">{float(r["Achieved"]):.4f}</b> &nbsp; | &nbsp; Target {r["Target"]}</div><div class="meter {"" if ok else "bad"}"><div style="width:{min(100,max(8,100 if ok else 100))}%"></div></div></div>')
    return "".join(rows)

def donut(group_values, center, unit):
    d=pd.DataFrame({"Group":GROUP_ORDER,"Value":[float(group_values.get(g,0)) for g in GROUP_ORDER]})
    d=d[d["Value"]>0]
    fig=px.pie(d,names="Group",values="Value",hole=.64,color="Group",color_discrete_map=GROUP_COLORS)
    fig.update_traces(textposition="inside",textinfo="percent",textfont_size=10,hovertemplate="<b>%{label}</b><br>%{value:.1f} "+unit+"<extra></extra>")
    fig.update_layout(height=300,margin=dict(l=5,r=5,t=5,b=5),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#dfe8ed",size=10),legend=dict(orientation="v",x=1.0,y=.5,xanchor="right",font=dict(size=9)),showlegend=True)
    fig.add_annotation(text=f"<b>{center:,.1f}</b><br><span style='font-size:10px'>{unit}</span>",x=.5,y=.5,showarrow=False,font=dict(size=16,color="#f4f8fa"))
    return fig

def page_header(title, subtitle):
    st.markdown(f'<div class="eyebrow">HOSPET ALLOY STEEL PLANT</div><h2>{title}</h2><div class="sub">{subtitle}</div>',unsafe_allow_html=True)

def empty_state(title="No optimization result", subtitle="Run the optimizer to populate this workspace."):
    st.markdown(f'<div class="empty"><div class="empty-title">{title}</div><div class="empty-sub">{subtitle}</div></div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-name">BAJAJ MUKAND</div><div class="brand-sub">Alloy Steel Group • Hospet Plant</div><div class="brand-jv">Kalyani Steels × Mukand</div></div>',unsafe_allow_html=True)
    nav_groups=[("WORKSPACE",[("◉","Dashboard")]),("OPERATIONS",[("▦","RM Stock"),("◈","Optimization Results"),("⚙","Manual Adjustment")]),("ANALYSIS",[("◌","Burden Composition"),("₹","Cost Composition"),("◇","What-if Analysis"),("△","Bottleneck Analysis")]),("REPORTING",[("▤","Reports")]),("SYSTEM",[("⇧","Upload & Settings")])]
    for heading,items in nav_groups:
        st.markdown(f'<div class="nav-head">{heading}</div>',unsafe_allow_html=True)
        for icon,label in items:
            if st.button(f"{icon}  {label}",key="nav_"+label,use_container_width=True,type="primary" if st.session_state.nav==label else "secondary"):
                st.session_state.nav=label;st.rerun()
    st.markdown('<div class="side-status"><b>DATA STATUS</b><br><span class="dot green"></span> '+st.session_state.source_name+f'<br><span style="color:#6f8290">{len(st.session_state.df)} materials loaded</span><br><br><b>MODEL</b><br><span class="dot green"></span> Optimization engine ready</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
now=datetime.now(); result=st.session_state.result
ok,failed=quality_status(result["achieved"] if result else None)
status_text="QUALITY OK" if ok else "QUALITY ALERT"
status_cls="ok" if ok else "out"
st.markdown(f'<div class="header"><div><h1>SINTER BURDEN CONTROL</h1><div class="sub">Cost-optimal burden planning • quality assurance • raw material decision support</div></div><div class="header-right"><span class="badge {status_cls}">● {status_text}</span><br><b>PLANT: HOSPET</b> • {now:%d %b %Y %H:%M}</div></div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DASHBOARD
# -----------------------------------------------------------------------------
def dashboard():
    st.markdown('<div class="hero"><div class="panel-head"><div><div class="eyebrow">CONTROL ROOM</div><b style="font-size:.86rem">Optimization workspace</b><div class="sub">Built-in master chemistry is active. Commercial inputs can be edited before each run.</div></div><div style="text-align:right"><span class="badge info">● SYSTEM READY</span></div></div></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([4.5,2.1,1.6])
    with c1:
        st.markdown(f'<div class="control-note">DATA SOURCE &nbsp; <b>{st.session_state.source_name}</b> &nbsp; • &nbsp; {len(st.session_state.df)} materials &nbsp; • &nbsp; Price / RM Stock / Availability editable</div>',unsafe_allow_html=True)
    with c2:
        up=st.file_uploader("Master chemistry Excel",type=["xlsx"],label_visibility="collapsed",key="dashboard_upload")
        if up:
            try:
                loaded=load_chemistry_from_excel(up)
                if st.button("Activate uploaded chemistry",use_container_width=True): set_dataset(loaded,"Uploaded • "+up.name);st.rerun()
            except Exception as e: st.error(str(e))
    with c3:
        if st.button("🚀 RUN OPTIMIZER",type="primary",use_container_width=True):
            with st.spinner("Optimizing burden mix…"): run_optimizer()
            st.rerun()
    if st.session_state.inputs_changed: st.markdown('<div class="notice notice-warn" style="margin-top:.55rem">✎ Commercial inputs changed. Re-run the optimizer to refresh the solution.</div>',unsafe_allow_html=True)
    if not result or not result["blend"]:
        st.markdown('<div style="margin-top:.7rem">',unsafe_allow_html=True);empty_state("Optimization not yet run","Edit RM Stock / Price / Availability, then run the optimizer.");st.markdown('</div>',unsafe_allow_html=True)
        commercial_editor("dashboard_editor_empty");return
    df=result["df"]; blend=result["blend"]; ach=result["achieved"]; cost=result["cost"]
    bd,cost,burden=breakdown(blend,df); base=bd[bd.Material!="TOTAL"]
    group_b=base.groupby("Group")["kg/t"].sum().reindex(GROUP_ORDER).fillna(0); group_c=base.groupby("Group")["Cost Rs/t"].sum().reindex(GROUP_ORDER).fillna(0)
    delta="—" if st.session_state.previous_cost is None else f"{'↓' if cost-st.session_state.previous_cost<0 else '↑'} ₹{abs(cost-st.session_state.previous_cost):,.2f}/t"
    cards=[("kpi-steel","TOTAL COST",f"₹ {cost:,.2f}/t","Per tonne of sinter"),("kpi-green","TOTAL BURDEN",f"{burden:,.1f} kg/t","Optimized mix"),("kpi-amber","ACHIEVED Fe",f"{ach['Fe']:.2f}%",f"Target {FE_LOWER:.1f}–{FE_UPPER:.1f}%"),("kpi-cyan","SOLUTION",result["status"],f"Run #{st.session_state.run_count}"),("kpi-orange","COST CHANGE",delta,"vs previous run")]
    cols=st.columns(5)
    for col,(cl,l,v,s) in zip(cols,cards):
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="notice {"" if ok else "notice-bad"}" style="margin:.65rem 0">● {"QUALITY OK — All mandatory constraints satisfied" if ok else "QUALITY ALERT — "+", ".join(failed)}</div>',unsafe_allow_html=True)

    left,mid,right=st.columns([1.55,1.0,1.35])
    with left:
        st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title panel-accent">RAW MATERIAL COMMERCIAL INPUTS</div><span class="badge info">✎ EDITABLE</span></div><div class="control-note">Editable: <b>Price</b> • <b>RM Stock</b> • <b>Availability</b> &nbsp; | &nbsp; Read-only: Chemistry • Tech Max</div>',unsafe_allow_html=True)
        commercial_editor("dashboard_editor");st.markdown('</div>',unsafe_allow_html=True)
    with mid:
        st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title panel-accent">BURDEN MIX</div><span class="badge info">kg/t</span></div>',unsafe_allow_html=True)
        st.plotly_chart(donut(group_b,burden,"kg/t"),use_container_width=True,config={"displayModeBar":False})
        for g in GROUP_ORDER:
            pct=group_b[g]/burden*100 if burden else 0
            st.markdown(f'<div class="mini-row"><span>{chip(g)}</span><span>{group_b[g]:,.1f} kg/t • {pct:.1f}%</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title panel-accent">SINTER QUALITY GATE</div><span class="badge {"ok" if ok else "out"}">{"OK" if ok else "CHECK"}</span></div>',unsafe_allow_html=True)
        st.markdown(quality_panel(ach),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    left2,right2=st.columns([1.05,1.95])
    with left2:
        st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title">RAW MATERIAL CHEMISTRY</div><span class="badge info">MASTER DATA</span></div>',unsafe_allow_html=True)
        chem=df[["Group","Fe","SiO2","Al2O3","CaO","MgO","LOI"]].copy().reset_index().rename(columns={"index":"Material"});st.markdown(pretty_table(chem.round(3)),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    with right2:
        st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title">OPTIMAL BURDEN & COST BREAKDOWN</div><span class="badge info">IRON ORE → FLUX → RECYCLE → FUEL</span></div>',unsafe_allow_html=True)
        disp=bd.copy();st.markdown(pretty_table(disp.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    a,b,c,d=st.columns(4)
    for col,g,cl in zip([a,b,c,d],GROUP_ORDER,["kpi-steel","kpi-green","kpi-amber","kpi-red"]):
        val=float(group_c[g]);pct=val/cost*100 if cost else 0
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{GROUP_LABEL[g]} COST</div><div class="kpi-value">₹{val:,.2f}</div><div class="kpi-sub">{pct:.1f}% of total cost</div></div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# OTHER PAGES
# -----------------------------------------------------------------------------
def rm_stock():
    page_header("RM Stock & Commercial Inputs","Control the availability, stock and price assumptions used by the optimizer.")
    c1,c2,c3=st.columns(3)
    avail=sum(bool(v) for v in st.session_state.availability.values());total=len(st.session_state.df); low=sum(float(st.session_state.df.loc[m,"Available_Tonnes"])<1000 for m in st.session_state.df.index)
    for col,title,val,sub,cl in [(c1,"MATERIALS AVAILABLE",f"{avail}/{total}","Availability gate","kpi-green"),(c2,"LOW STOCK ITEMS",str(low),"Below 1,000 t reference","kpi-amber"),(c3,"EDIT MODE","ACTIVE","Price + stock + availability","kpi-steel")]:
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{title}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)
    st.write("");st.markdown('<div class="panel"><div class="panel-head"><div class="panel-title">COMMERCIAL MASTER</div><span class="badge info">✎ Editable inputs</span></div>',unsafe_allow_html=True);commercial_editor("rm_editor");st.markdown('</div>',unsafe_allow_html=True)
    if st.session_state.inputs_changed: st.markdown('<div class="notice notice-warn" style="margin-top:.5rem">Inputs changed — run the optimizer to apply them.</div>',unsafe_allow_html=True)

def burden_page():
    page_header("Burden Mix & Material Contribution","Understand how each material group contributes to the optimized sinter burden.")
    if not result or not result["blend"]: empty_state();return
    bd,cost,burden=breakdown(result["blend"],result["df"]); base=bd[bd.Material!="TOTAL"]; g=base.groupby("Group")["kg/t"].sum().reindex(GROUP_ORDER).fillna(0)
    l,r=st.columns([1.05,1.65])
    with l: st.markdown('<div class="panel"><div class="panel-title">BURDEN DISTRIBUTION</div>',unsafe_allow_html=True);st.plotly_chart(donut(g,burden,"kg/t"),use_container_width=True,config={"displayModeBar":False});st.markdown('</div>',unsafe_allow_html=True)
    with r:
        rows=[{"Material":GROUP_LABEL[x],"Group":x,"kg/t":g[x],"% of Burden":g[x]/burden*100 if burden else 0} for x in GROUP_ORDER];rows.append({"Material":"TOTAL","Group":"","kg/t":burden,"% of Burden":100})
        st.markdown('<div class="panel"><div class="panel-title">GROUP CONTRIBUTION</div>',unsafe_allow_html=True);st.markdown(pretty_table(pd.DataFrame(rows).round(2)),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    st.write("");st.markdown('<div class="panel"><div class="panel-title">MATERIAL-LEVEL BURDEN</div>',unsafe_allow_html=True);st.markdown(pretty_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

def cost_page():
    page_header("Cost Structure & Cost Drivers","See where the optimized sinter cost is concentrated and which material groups drive it.")
    if not result or not result["blend"]: empty_state();return
    bd,cost,burden=breakdown(result["blend"],result["df"]); base=bd[bd.Material!="TOTAL"];g=base.groupby("Group")["Cost Rs/t"].sum().reindex(GROUP_ORDER).fillna(0)
    l,r=st.columns([1.05,1.65])
    with l: st.markdown('<div class="panel"><div class="panel-title">COST DISTRIBUTION</div>',unsafe_allow_html=True);st.plotly_chart(donut(g,cost,"₹/t"),use_container_width=True,config={"displayModeBar":False});st.markdown('</div>',unsafe_allow_html=True)
    with r:
        rows=[{"Material":GROUP_LABEL[x],"Group":x,"Cost Rs/t":g[x],"% of Cost":g[x]/cost*100 if cost else 0} for x in GROUP_ORDER];rows.append({"Material":"TOTAL","Group":"","Cost Rs/t":cost,"% of Cost":100})
        st.markdown('<div class="panel"><div class="panel-title">GROUP COST STRUCTURE</div>',unsafe_allow_html=True);st.markdown(pretty_table(pd.DataFrame(rows).round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    st.write("");st.markdown('<div class="panel"><div class="panel-title">TOP MATERIAL COST DRIVERS</div>',unsafe_allow_html=True);top=base.sort_values("Cost Rs/t",ascending=False).head(8);st.markdown(pretty_table(top.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

def results_page():
    page_header("Optimized Sinter Recipe","Production-ready recipe, quality gate and cost contribution from the latest optimization run.")
    if not result or not result["blend"]: empty_state();return
    bd,cost,burden=breakdown(result["blend"],result["df"]);ach=result["achieved"];ok,_=quality_status(ach)
    a,b,c,d=st.columns(4)
    for col,t,v,s,cl in [(a,"TOTAL COST",f"₹{cost:,.2f}/t","Current optimum","kpi-steel"),(b,"TOTAL BURDEN",f"{burden:,.1f} kg/t","Optimized mix","kpi-green"),(c,"Fe",f"{ach['Fe']:.3f}%",f"Target {FE_LOWER:.1f}–{FE_UPPER:.1f}","kpi-amber"),(d,"QUALITY GATE","PASS" if ok else "REVIEW","Mandatory constraints","kpi-green" if ok else "kpi-red")]:
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>',unsafe_allow_html=True)
    st.write("");q1,q2=st.columns([1.0,2.0])
    with q1: st.markdown('<div class="panel"><div class="panel-title">QUALITY ASSURANCE</div>',unsafe_allow_html=True);st.markdown(quality_panel(ach),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    with q2: st.markdown('<div class="panel"><div class="panel-title">OPTIMIZED BURDEN & COST</div>',unsafe_allow_html=True);st.markdown(pretty_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

def manual_page():
    page_header("Manual Burden Control","Adjust Iron Ore and Flux quantities while preserving total burden; Recycle and Fuel remain fixed.")
    if not result or not result["blend"]: empty_state();return
    df=result["df"];base=st.session_state.manual_base or result["blend"].copy();st.session_state.manual_base=base.copy()
    adjustable=[m for m in base if df.loc[m,"Group"] in ("Iron_ore","Flux")];fixed=[m for m in base if df.loc[m,"Group"] in ("Recycle","Fuel")]
    st.markdown('<div class="control-note">Adjustment envelope: <b>Iron Ore ±15%</b> • <b>Flux ±10%</b> • Recycle/Fuel fixed • Total burden preserved by proportional redistribution.</div>',unsafe_allow_html=True)
    requested={};cols=st.columns(2)
    for i,m in enumerate(adjustable):
        b=float(base[m]);rng=.15 if df.loc[m,"Group"]=="Iron_ore" else .10;mn=max(0.0,b*(1-rng));mx=max(mn+1.0,b*(1+rng));key=f"manual_{m}"
        if key not in st.session_state or not (mn<=float(st.session_state[key])<=mx):st.session_state[key]=b
        with cols[i%2]: requested[m]=st.slider(f"{m} — kg/t",min_value=float(mn),max_value=float(mx),value=float(st.session_state[key]),step=.5,key=key,help=f"Baseline {b:.2f} kg/t • ±{rng*100:.0f}%")
    adjusted=redistribute_adjustment(base,df,requested)
    for m in fixed: adjusted[m]=base[m]
    st.session_state.manual_adjusted=adjusted
    ach=compute_achieved(adjusted,df,1000);adj_cost=sum(adjusted[m]*df.loc[m,"Price_Rs_t"]/1000 for m in adjusted);base_cost=result["cost"] or 0;delta=adj_cost-base_cost;burden=sum(adjusted.values());ok,_=quality_status(ach)
    st.write("");cards=[("BASE COST",f"₹{base_cost:,.2f}/t","Optimized","kpi-steel"),("ADJUSTED COST",f"₹{adj_cost:,.2f}/t",f"{delta:+,.2f}/t","kpi-orange"),("BURDEN",f"{burden:,.1f} kg/t","Total preserved","kpi-green"),("Fe",f"{ach['Fe']:.3f}%",f"Target {FE_LOWER:.1f}–{FE_UPPER:.1f}","kpi-amber"),("QUALITY","PASS" if ok else "REVIEW","After adjustment","kpi-green" if ok else "kpi-red")]
    cc=st.columns(5)
    for col,(t,v,s,cl) in zip(cc,cards):
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>',unsafe_allow_html=True)
    st.write("");q,b=st.columns([1.0,2.0])
    with q: st.markdown('<div class="panel"><div class="panel-title">ACHIEVED QUALITY AFTER ADJUSTMENT</div>',unsafe_allow_html=True);st.markdown(quality_panel(ach),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    with b: bd,_,_=breakdown(adjusted,df);st.markdown('<div class="panel"><div class="panel-title">ADJUSTED BURDEN & COST</div>',unsafe_allow_html=True);st.markdown(pretty_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    st.write("");x,y,z=st.columns(3)
    with x:
        if st.button("↩ RESET TO OPTIMIZED",use_container_width=True):
            for m in adjustable: st.session_state[f"manual_{m}"]=float(base[m])
            st.session_state.manual_adjusted=base.copy();st.rerun()
    with y:
        if st.button("✓ APPLY ADJUSTMENT",type="primary",use_container_width=True): st.session_state.active_manual=adjusted.copy();st.success("Manual burden is now the active recipe.")
    with z:
        if st.button("🚀 APPLY & RE-RUN OPTIMIZER",use_container_width=True):
            with st.spinner("Re-optimizing from adjusted burden…"):run_optimizer(reference_blend=adjusted)
            st.rerun()

def what_if_page():
    page_header("Scenario & Material Risk","Test the effect of material unavailability before it becomes a production constraint.")
    if st.button("▶ RUN MATERIAL SHORTAGE SCENARIOS",type="primary"):
        with st.spinner("Evaluating scenarios…"):st.session_state.what_if=what_if_analysis(active_df(),TARGETS)
    if st.session_state.what_if is None: empty_state("No scenario run yet","Evaluate missing-material scenarios to see feasibility and cost impact.");return
    wi=st.session_state.what_if.copy()
    if "Group" in wi: wi["_o"]=wi["Group"].map({g:i for i,g in enumerate(GROUP_ORDER)}).fillna(99);wi=wi.sort_values(["_o","Missing Material"]).drop(columns="_o")
    st.markdown('<div class="panel"><div class="panel-title">SCENARIO MATRIX</div>',unsafe_allow_html=True);st.markdown(pretty_table(wi.fillna("—")),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

def bottleneck_page():
    page_header("Quality Constraint Pressure","Identify which chemistry constraints are closest to their operating limits.")
    if not result or not result["achieved"]: empty_state();return
    ach=result["achieved"]
    q=quality_table(ach,TARGETS).copy()
    rows=[]
    for _,r in q.iterrows():
        k=r["KPI"];v=float(r["Achieved"]);status=r["Status"]
        rows.append({"KPI":k,"Achieved":v,"Target":r["Target"],"Status":status})
    st.markdown('<div class="panel"><div class="panel-title">CONSTRAINT PRESSURE</div>',unsafe_allow_html=True);st.markdown(pretty_table(pd.DataFrame(rows).round(4),status_col="Status"),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    if result["diagnostics"]:
        st.write("")
        for d in result["diagnostics"]: st.markdown(f'<div class="notice notice-warn">△ {d}</div>',unsafe_allow_html=True)

def reports_page():
    page_header("Reports & Export","Export the optimized recipe for review, production planning or management reporting.")
    if not result or not result["blend"]: empty_state();return
    bd,cost,burden=breakdown(result["blend"],result["df"]);st.markdown('<div class="panel"><div class="panel-title">OPTIMIZATION REPORT</div>',unsafe_allow_html=True);st.markdown(pretty_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)
    st.download_button("⬇ DOWNLOAD OPTIMIZATION REPORT",bd.to_csv(index=False).encode(),"sinter_optimization_report.csv","text/csv",use_container_width=True)

def settings_page():
    page_header("Upload & Settings","Manage master chemistry source and restore the built-in reference dataset when required.")
    c1,c2=st.columns([1.4,1])
    with c1:
        st.markdown('<div class="panel"><div class="panel-title">MASTER CHEMISTRY SOURCE</div>',unsafe_allow_html=True);st.markdown(f'<div class="kpi kpi-steel"><div class="kpi-label">ACTIVE SOURCE</div><div class="kpi-value" style="font-size:1rem">{st.session_state.source_name}</div><div class="kpi-sub">{len(st.session_state.df)} materials loaded</div></div>',unsafe_allow_html=True);up=st.file_uploader("Upload master chemistry Excel",type=["xlsx"],key="settings_upload")
        if up:
            try:
                loaded=load_chemistry_from_excel(up)
                if st.button("ACTIVATE UPLOADED EXCEL",type="primary",use_container_width=True):set_dataset(loaded,"Uploaded • "+up.name);st.rerun()
            except Exception as e:st.error(str(e))
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-title">SYSTEM ACTIONS</div>',unsafe_allow_html=True)
        if st.button("↺ RESTORE BUILT-IN MASTER CHEMISTRY",use_container_width=True):set_dataset(get_default_chemistry(),"Built-in Master Chemistry");st.rerun()
        st.markdown('<div class="control-note" style="margin-top:.6rem">The Excel upload is optional. The built-in master chemistry remains the standby source for development and testing.</div>',unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

def chemistry_page():
    page_header("Raw Material Chemistry","Read-only chemistry master used by the optimization engine.")
    df=st.session_state.df.copy().reset_index();df["Group"]=df["Group"].map(GROUP_LABEL);cols=["Material","Group","Fe","SiO2","Al2O3","CaO","MgO","LOI","Tech_Min","Tech_Max"]
    st.markdown('<div class="panel"><div class="panel-title">CHEMISTRY MASTER</div>',unsafe_allow_html=True);st.markdown(pretty_table(df[cols].round(3)),unsafe_allow_html=True);st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ROUTING
# -----------------------------------------------------------------------------
nav=st.session_state.nav
if nav=="Dashboard":dashboard()
elif nav=="RM Stock":rm_stock()
elif nav=="Burden Composition":burden_page()
elif nav=="Cost Composition":cost_page()
elif nav=="Optimization Results":results_page()
elif nav=="Manual Adjustment":manual_page()
elif nav=="What-if Analysis":what_if_page()
elif nav=="Bottleneck Analysis":bottleneck_page()
elif nav=="Reports":reports_page()
elif nav=="Upload & Settings":settings_page()

st.markdown('<div class="footer">Sinter Burden Control • Hospet Alloy Steel Plant • Decision-support interface • Model engine separated from UI</div>',unsafe_allow_html=True)
