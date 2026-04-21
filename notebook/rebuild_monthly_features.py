"""
按月重建 user_features_month{4,5,6}.csv
特征区间 = 当月第一天 ~ 当月最后一天
逻辑与 02_Feature_Engineering.ipynb 中 build_features 对齐，但按月切片。
"""
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'online_data.csv')
OUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'features')

FIXED_DISCOUNT_CONST = 0.001


def parse_date(series):
    uniq = series.dropna().unique()
    m = {v: pd.to_datetime(str(int(v)), format='%Y%m%d', errors='coerce') for v in uniq}
    return series.map(m)


def convert_discount_rate(rate):
    if pd.isna(rate) or str(rate).strip() == '':
        return np.nan
    s = str(rate).strip().lower()
    if ':' in s:
        try:
            t, d = s.split(':')
            t, d = float(t), float(d)
            if t <= 0:
                return np.nan
            return round(1.0 - d / t, 6)
        except Exception:
            return FIXED_DISCOUNT_CONST
    if s in ('fixed', 'nan', 'none', ''):
        return FIXED_DISCOUNT_CONST
    try:
        v = float(s)
        if 0 < v <= 1:
            return v
        if v > 1:
            return round(v / 100.0, 6)
        return FIXED_DISCOUNT_CONST
    except Exception:
        return FIXED_DISCOUNT_CONST


def load_df():
    df = pd.read_csv(RAW_PATH)
    df.columns = df.columns.str.lower()
    df['date'] = parse_date(df['date'])
    df['date_received'] = parse_date(df['date_received'])
    df['user_id'] = df['user_id'].astype(str)
    df['merchant_id'] = df['merchant_id'].astype(str)
    df['coupon_id'] = df['coupon_id'].fillna('').replace('', 'NO_COUPON').astype(str)
    df['discount_rate'] = df['discount_rate'].fillna('').replace('', None)
    df['discount_rate_num'] = df['discount_rate'].apply(convert_discount_rate)

    df['is_click'] = (df['action'] == 0).astype(int)
    df['is_purchase'] = (df['action'] == 1).astype(int)
    df['is_coupon_received'] = (df['action'] == 2).astype(int)
    df['is_coupon_purchase'] = ((df['action'] == 1) & (df['coupon_id'] != 'NO_COUPON')).astype(int)
    df['is_no_coupon_purchase'] = ((df['action'] == 1) & (df['coupon_id'] == 'NO_COUPON')).astype(int)
    df['is_coupon_not_used'] = ((df['action'] == 2) & df['date'].isna()).astype(int)
    return df


def extract_basic(feat):
    b = feat.groupby('user_id').agg({
        'is_purchase': 'sum', 'is_click': 'sum', 'is_coupon_received': 'sum',
        'is_coupon_purchase': 'sum', 'is_no_coupon_purchase': 'sum',
        'is_coupon_not_used': 'sum', 'merchant_id': 'nunique', 'coupon_id': 'nunique',
    }).reset_index()
    b.columns = ['user_id', 'total_purchases', 'total_clicks', 'total_coupon_rcvd',
                 'coupon_purchases', 'no_coupon_purchases', 'coupons_not_used',
                 'merchant_count', 'coupon_types_count']
    b['coupon_use_rate'] = b['coupon_purchases'] / b['total_coupon_rcvd'].replace(0, 1)
    b['coupon_abandon_rate'] = b['coupons_not_used'] / b['total_coupon_rcvd'].replace(0, 1)
    b['coupon_purchase_ratio'] = b['coupon_purchases'] / b['total_purchases'].replace(0, 1)
    b['click_to_buy_rate'] = b['total_purchases'] / b['total_clicks'].replace(0, 1)
    b['avg_purchase_per_merchant'] = b['total_purchases'] / b['merchant_count'].replace(0, 1)
    # 供 visualization 接口使用的别名
    b['frequency'] = b['total_purchases']
    b['total_coupons'] = b['total_coupon_rcvd']
    b['ctr'] = b['click_to_buy_rate']
    b['coupon_receive_rate'] = b['total_coupon_rcvd'] / (b['total_clicks'] + b['total_coupon_rcvd']).replace(0, 1)
    b['cvr'] = b['click_to_buy_rate']
    return b


def extract_um(feat):
    clk = feat[feat['is_click'] == 1]
    pur = feat[feat['is_purchase'] == 1]
    umc = clk.groupby(['user_id', 'merchant_id']).size().reset_index(name='um_click_count')
    ump = pur.groupby(['user_id', 'merchant_id']).size().reset_index(name='um_purchase_count')
    um = umc.merge(ump, on=['user_id', 'merchant_id'], how='outer').fillna(0)
    agg = um.groupby('user_id').agg({
        'merchant_id': 'count',
        'um_click_count': ['max', 'mean', 'sum'],
        'um_purchase_count': ['max', 'mean', 'sum'],
    })
    agg.columns = ['um_total_pairs', 'um_max_clicks', 'um_avg_clicks',
                   'um_total_clicks', 'um_max_purchases', 'um_avg_purchases', 'um_total_um_purch']
    agg = agg.reset_index()
    bp = um[um['um_purchase_count'] > 0].groupby('user_id').size().reset_index(name='um_purchase_pairs')
    agg = agg.merge(bp, on='user_id', how='left').fillna(0)
    agg['um_purchase_penetration'] = agg['um_purchase_pairs'] / agg['um_total_pairs'].replace(0, 1)
    return agg


def extract_window(feat, feat_end, windows=(7, 14, 30)):
    base = pd.DataFrame({'user_id': feat['user_id'].unique()})
    for w in windows:
        start = feat_end - pd.Timedelta(days=w)
        wd = feat[feat['date'] >= start]
        st = wd.groupby('user_id').agg({
            'is_purchase': 'sum', 'is_click': 'sum', 'is_coupon_received': 'sum',
        }).reset_index()
        st.columns = ['user_id', f'purchases_{w}d', f'clicks_{w}d', f'coupons_{w}d']
        base = base.merge(st, on='user_id', how='left')
    fc = [c for c in base.columns if c != 'user_id']
    base[fc] = base[fc].fillna(0)
    return base


def extract_rfm(feat, feat_end):
    pur = feat[feat['is_purchase'] == 1].copy()
    if len(pur) == 0:
        return pd.DataFrame({'user_id': feat['user_id'].unique()})
    r = pur.groupby('user_id').agg({'date': ['min', 'max', 'count']})
    r.columns = ['first_purchase_date', 'last_purchase_date', 'rfm_frequency']
    r = r.reset_index()
    r['recency'] = (feat_end - r['last_purchase_date']).dt.days
    r['lifetime'] = (r['last_purchase_date'] - r['first_purchase_date']).dt.days
    r['purchase_frequency_daily'] = r['rfm_frequency'] / r['lifetime'].replace(0, 1)
    return r[['user_id', 'recency', 'lifetime', 'rfm_frequency', 'purchase_frequency_daily']]


def extract_coupon(feat):
    cp = feat[feat['is_coupon_purchase'] == 1].copy()
    if len(cp) == 0:
        return pd.DataFrame({'user_id': feat['user_id'].unique()})
    d = cp.groupby('user_id').agg({'discount_rate_num': ['mean', 'median', 'std', 'min', 'max']})
    d.columns = ['avg_discount', 'median_discount', 'std_discount', 'min_discount', 'max_discount']
    d = d.reset_index()
    used = feat[feat['is_coupon_purchase'].eq(1) & feat['date_received'].notna()].copy()
    if len(used) > 0:
        used['days_to_use'] = (used['date'] - used['date_received']).dt.days
        ds = used.groupby('user_id').agg({'days_to_use': ['mean', 'max']})
        ds.columns = ['avg_days_to_use', 'max_days_to_use']
        ds = ds.reset_index()
        d = d.merge(ds, on='user_id', how='left')
    return d


def extract_time_pref(feat):
    pur = feat[feat['is_purchase'] == 1].copy()
    if len(pur) == 0:
        return pd.DataFrame({'user_id': feat['user_id'].unique()})
    pur['weekday'] = pur['date'].dt.weekday
    wd = pur[pur['weekday'] < 5].groupby('user_id').size().reset_index(name='weekday_purchases')
    we = pur[pur['weekday'] >= 5].groupby('user_id').size().reset_index(name='weekend_purchases')
    base = pd.DataFrame({'user_id': feat['user_id'].unique()})
    base = base.merge(wd, on='user_id', how='left').merge(we, on='user_id', how='left')
    base[['weekday_purchases', 'weekend_purchases']] = base[['weekday_purchases', 'weekend_purchases']].fillna(0)
    base['weekend_purchase_ratio'] = base['weekend_purchases'] / (
        base['weekday_purchases'] + base['weekend_purchases']).replace(0, 1)
    return base


def build_month(df, month):
    feat_start = pd.Timestamp(f'2016-{month:02d}-01')
    feat_end = (feat_start + pd.offsets.MonthEnd(0))
    feat = df[
        ((df['date'] >= feat_start) & (df['date'] <= feat_end)) |
        ((df['date_received'] >= feat_start) & (df['date_received'] <= feat_end))
    ].copy()
    active = pd.DataFrame({'user_id': feat['user_id'].unique()})
    # 新老用户标记：该月之前是否出现过购买
    prior_buyers = set(df[(df['date'] < feat_start) & df['is_purchase'].eq(1)]['user_id'].unique())
    active['is_new_user'] = (~active['user_id'].isin(prior_buyers)).astype(int)

    parts = [
        extract_basic(feat),
        extract_um(feat),
        extract_window(feat, feat_end),
        extract_rfm(feat, feat_end),
        extract_coupon(feat),
        extract_time_pref(feat),
    ]
    result = active
    for p in parts:
        result = result.merge(p, on='user_id', how='left')
    num = result.select_dtypes(include=np.number).columns
    result[num] = result[num].fillna(0)
    return result, feat_start.date(), feat_end.date()


def main():
    print('加载原始数据...')
    df = load_df()
    print(f'行数: {len(df):,}  唯一用户: {df["user_id"].nunique():,}')
    os.makedirs(OUT_DIR, exist_ok=True)
    for m in [4, 5, 6]:
        print(f'\n== 构建 month={m} ==')
        feats, s, e = build_month(df, m)
        out = os.path.join(OUT_DIR, f'user_features_month{m}.csv')
        feats.to_csv(out, index=False)
        print(f'  区间 {s} ~ {e}  shape={feats.shape}  '
              f'recency均值={feats["recency"].mean():.2f}  '
              f'new_user比例={feats["is_new_user"].mean():.3f}')
        print(f'  -> {out}')


if __name__ == '__main__':
    main()
