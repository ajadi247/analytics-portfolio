"""Rebuild the housing analysis from preserved source snapshots. Run: python analysis.py."""
from pathlib import Path
import json, sqlite3, itertools, math, os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'images').mkdir(exist_ok=True)

def payment(value, rate):
    """Monthly principal and interest, 80% loan-to-value, 360 payments. Rate in percent."""
    r=np.asarray(rate)/1200
    return np.asarray(value)*.8*r/(1-(1+r)**-360)

def burden(v,r,i): return 12*payment(v,r)/i

def run():
    z=pd.read_csv(RAW/'County_zhvi.csv',dtype={'StateCodeFIPS':str,'MunicipalCodeFIPS':str}).copy()
    z['county_fips']=z.StateCodeFIPS.str.zfill(2)+z.MunicipalCodeFIPS.str.zfill(3)
    assert z.county_fips.str.fullmatch(r'\d{5}').all()
    assert not z.county_fips.duplicated().any()
    dates=[c for c in z if len(c)==10 and c[:4].isdigit() and 2015<=int(c[:4])<=2025]
    assert len(dates)==132
    m=z.melt(id_vars=['county_fips','RegionName','State'],value_vars=dates,var_name='date',value_name='home_value')
    m['year']=m.date.str[:4].astype(int)
    annual=m.groupby(['county_fips','RegionName','State','year'],as_index=False).agg(home_value=('home_value','mean'),months_available=('home_value','count'))
    annual=annual.rename(columns={'RegionName':'county','State':'state'})
    annual['housing_eligible']=annual.months_available.eq(12)
    rows=[]
    for y in range(2015,2025):
        for line in (RAW/f'saipe_{y}.txt').read_text().splitlines():
            st=line[0:2]; co=line[3:6].strip().zfill(3)
            if st=='00' or co=='000': continue
            num=lambda s: pd.to_numeric(s.strip(),errors='coerce')
            rows.append(dict(county_fips=st+co,year=y,median_household_income=num(line[133:139]),income_lower=num(line[140:146]),income_upper=num(line[147:153]),census_county=line[193:238].strip(),census_state=line[239:241]))
    income=pd.DataFrame(rows)
    assert not income.duplicated(['county_fips','year']).any()
    valid_income=income.dropna(subset=['median_household_income','income_lower','income_upper'])
    assert (valid_income.income_lower.le(valid_income.median_household_income)&valid_income.income_upper.ge(valid_income.median_household_income)).all()
    w=pd.read_csv(RAW/'mortgage_rates.csv',parse_dates=['observation_date'])
    w['year']=w.observation_date.dt.year
    w.MORTGAGE30US=pd.to_numeric(w.MORTGAGE30US,errors='coerce')
    rates=w[w.year.between(2015,2025)].groupby('year',as_index=False).agg(avg_mortgage_rate=('MORTGAGE30US','mean'),rate_observations=('MORTGAGE30US','count'))
    assert rates.rate_observations.between(52,53).all()
    d=annual.merge(income,on=['county_fips','year'],how='left',validate='one_to_one').merge(rates,on='year',validate='many_to_one')
    d['income_eligible']=d.median_household_income.gt(0)&d.income_lower.gt(0)
    d['eligible']=d.housing_eligible&d.income_eligible
    d['monthly_payment']=payment(d.home_value,d.avg_mortgage_rate)
    d['price_to_income_ratio']=d.home_value/d.median_household_income
    d['payment_to_income_ratio']=12*d.monthly_payment/d.median_household_income
    d['burden_income_lower_bound']=12*d.monthly_payment/d.income_upper
    d['burden_income_upper_bound']=12*d.monthly_payment/d.income_lower
    d=d.sort_values(['county_fips','year'])
    for source,target in [('home_value','home_value_yoy_growth'),('median_household_income','income_yoy_growth')]:
        d[target]=d.groupby('county_fips')[source].pct_change(fill_method=None)
        prev=d.groupby('county_fips').housing_eligible.shift(1).fillna(False)
        d.loc[~(d.housing_eligible&prev),target]=np.nan
    eligible=d[d.eligible].copy()
    balanced_ids=eligible.groupby('county_fips').year.nunique().loc[lambda x:x==10].index
    d['balanced_panel']=d.county_fips.isin(balanced_ids)&d.year.le(2024)
    panel=d[d.balanced_panel].copy()
    assert panel.eligible.all()
    summary=panel.groupby('year',as_index=False).agg(counties=('county_fips','nunique'),home_value=('home_value','median'),median_household_income=('median_household_income','median'),monthly_payment=('monthly_payment','median'),payment_to_income_ratio=('payment_to_income_ratio','median'),price_to_income_ratio=('price_to_income_ratio','median'),avg_mortgage_rate=('avg_mortgage_rate','first'))
    base=panel[panel.year.eq(2015)].set_index('county_fips'); end=panel[panel.year.eq(2024)].set_index('county_fips')
    change=end[['county','state','home_value','median_household_income','payment_to_income_ratio']].copy()
    for c in ['home_value','median_household_income','monthly_payment']:
        change[c+'_growth']=end[c]/base[c]-1
    change['burden_change_pp']=(end.payment_to_income_ratio-base.payment_to_income_ratio)*100
    # Shapley allocation averages all six orders of changing price, rate and income.
    b=[base.home_value.values,base.avg_mortgage_rate.values,base.median_household_income.values]
    e=[end.home_value.values,end.avg_mortgage_rate.values,end.median_household_income.values]
    contrib=np.zeros((len(base),3))
    for order in itertools.permutations(range(3)):
        cur=b.copy()
        for k in order:
            old=burden(*cur); cur=cur.copy();cur[k]=e[k]
            contrib[:,k]+=(burden(*cur)-old)*100/6
    for k,name in enumerate(['price_contribution_pp','rate_contribution_pp','income_contribution_pp']):change[name]=contrib[:,k]
    assert np.allclose(contrib.sum(axis=1),change.burden_change_pp,atol=1e-9)
    assert abs(float(payment(300000,6))-1438.9212603666)<.0001
    # Independent amortization: remaining loan balance must reach zero after 360 payments.
    bal=240000.;p=float(payment(300000,6))
    for _ in range(360):bal=bal*1.005-p
    assert abs(bal)<1e-6
    sensitivity=[]
    for threshold in [10,11,12]:
        s=d[d.months_available.ge(threshold)&d.income_eligible&d.year.le(2024)]
        ids=s.groupby('county_fips').year.nunique().loc[lambda x:x==10].index
        s=s[s.county_fips.isin(ids)]
        sensitivity.append({'minimum_months':threshold,'balanced_counties':len(ids),'median_burden_2015':s[s.year.eq(2015)].payment_to_income_ratio.median(),'median_burden_2024':s[s.year.eq(2024)].payment_to_income_ratio.median()})
    d.to_csv(OUT/'county_year_audit.csv',index=False)
    d[d.eligible].to_csv(OUT/'housing_affordability.csv',index=False)
    d[d.year.eq(2025)&d.housing_eligible].to_csv(OUT/'housing_2025_context.csv',index=False)
    change.reset_index().to_csv(OUT/'county_changes_2015_2024.csv',index=False)
    summary.to_csv(OUT/'balanced_panel_summary.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'coverage_sensitivity.csv',index=False)
    rates.to_csv(OUT/'annual_mortgage_rates.csv',index=False)
    unmatched=d[d.year.le(2024)&d.housing_eligible&~d.income_eligible][['county_fips','county','state','year']]
    unmatched.to_csv(OUT/'unmatched_income.csv',index=False)
    checks={'raw_counties':len(z),'county_years':len(d),'eligible_county_years':int(d.eligible.sum()),'balanced_counties':len(balanced_ids),'unmatched_income_county_years':len(unmatched),'excluded_incomplete_housing_county_years_2015_2024':int((d.year.le(2024)&~d.housing_eligible).sum()),'checks_passed':['unique FIPS and county-year keys','132 study months','52-53 weekly rates per year','income bounds ordered','mortgage reference value','360-month balance reconciliation','Shapley contributions reconcile','balanced panel has ten eligible years'],'sensitivity':sensitivity,'mean_contributions_pp':dict(zip(['price','rate','income'],contrib.mean(axis=0))), 'median_county_home_growth':float(change.home_value_growth.median()),'median_county_income_growth':float(change.median_household_income_growth.median()),'median_county_payment_growth':float(change.monthly_payment_growth.median()),'share_burden_increased':float(change.burden_change_pp.gt(0).mean())}
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2))
    with sqlite3.connect(ROOT/'housing.sqlite') as db:
        d.to_sql('county_year',db,if_exists='replace',index=False)
        change.reset_index().to_sql('county_changes',db,if_exists='replace',index=False)
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS county_year_key ON county_year(county_fips,year)')
        db.execute('CREATE INDEX IF NOT EXISTS county_year_state ON county_year(state,year)')
        assert db.execute('SELECT COUNT(*) FROM county_year WHERE eligible=1').fetchone()[0]==int(d.eligible.sum())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,5));ax.plot(summary.year,summary.payment_to_income_ratio*100,color='#125a71',lw=3,marker='o');ax.set(xlabel='Year',ylabel='Principal & interest / household income (%)',title='Mortgage payment burden rose after 2021');ax.grid(axis='y',alpha=.2);fig.text(.12,.01,f'Unweighted median of {len(balanced_ids):,} consistently observed counties. 20% down; 30-year fixed. Excludes taxes and insurance.',fontsize=8);fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(ROOT/'images/burden_trend.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    for c,label,color in [('home_value','Home value','#125a71'),('median_household_income','Household income','#b47d24'),('monthly_payment','Mortgage payment','#cb5347')]:
        indexed=panel.pivot(index='county_fips',columns='year',values=c); vals=indexed.div(indexed[2015],axis=0).median()*100
        ax.plot(vals.index,vals.values,label=label,color=color,lw=3)
    ax.legend(frameon=False);ax.set(ylabel='Median county index (2015 = 100)',xlabel='Year',title='Home values and mortgage payments outpaced incomes');ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(ROOT/'images/growth.png',dpi=160);plt.close(fig)
    print(json.dumps(checks,indent=2));print(summary.to_string(index=False));print(change.sort_values('burden_change_pp',ascending=False).head(5).to_string())
    return d,summary,change,checks

if __name__=='__main__':run()
