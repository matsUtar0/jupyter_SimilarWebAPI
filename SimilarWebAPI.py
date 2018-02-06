
# coding: utf-8

# # SimilarWebの数値取得

# ## ライブラリの呼び出し

# In[30]:


import sys,json,os,subprocess
import urllib.request
import pandas as pd
from dotenv import load_dotenv, find_dotenv


# ## 環境変数の呼び出し

# In[2]:


#  ディレクトリから.envファイルを探す
dotenv_path = find_dotenv()

# 環境変数をロード
load_dotenv(dotenv_path)

# API_KEYに環境変数を代入
API_KEY = os.environ.get("SimilarWeb_API_KEY")


# ## 引数の取得

# In[ ]:


args = sys.argv
domain = args[1]
start_date = args[2]
end_date = args[3]


# ## パラメータを渡して、APIコール用のURLを返す関数

# In[3]:


def get_call_url(version,domain,endpoint_group,endpoint,API_KEY,start_date,end_date):
    url_format = 'https://api.similarweb.com/{}/website/{}/{}/{}?api_key={}&start_date={}&end_date={}&main_domain_only=false&granularity=monthly&country=JP'
    url = url_format.format(version,domain,endpoint_group,endpoint,API_KEY,start_date,end_date)
    return(url)


# ## APIコール用のURLを渡して、レスポンスをjson形式で返す関数

# In[4]:


def get_api_data(url):
    # APIコールし、HTTPレスポンスをresponseに格納
    response = urllib.request.urlopen(url)

    # HTTPレスポンスをjsonにパース
    read = response.read()
    data = json.loads(read)

    # APIコールが失敗した場合はEmptyを返す
    if data['meta']['status'] != 'Success':
        return('Empty')
    return(data)


# ## json形式のレスポンスを渡して、インデックス（デバイス、ドメイン、期間の幅、期間）を返す関数

# In[5]:


def get_index_data(data,device):
    # 結果格納用のリスト
    meta = json_for_index['meta']
    index = []

    # 結果の格納
    for visit in json_for_index['visits']:

        # 期間ごとにリストに格納
        single = [device, meta['request']['domain'], meta['request']['granularity'],visit['date']]

        # 期間ごとのリストを結果に格納
        index.append(single)
        
    df_index = pd.DataFrame(index,columns=['デバイス','ドメイン','期間の幅','期間'])
    return(df_index)


# ## json形式のレスポンスを渡して、指標を返す関数

# In[6]:


def get_metrics(data,metrics):
    # 結果格納用のリスト
    meta = data['meta']
    result = []

    # 結果の格納
    for metric in data[metrics]:

        # 期間ごとにリストに格納
        single = []
        for val in metric.values():

            single.append(val)

        # 期間ごとのリストを結果に格納
        result.append(single)
    
    de_metric = pd.DataFrame(result,columns=['期間',metrics])
    return(de_metric)


# ## APIセットの定義

# In[7]:


# total用のAPIセット
api_set_total = {'version': 'v1',
                        'endpoint_group': 'total-traffic-and-engagement',
                        'endpoint': ['visits','pages-per-visit','average-visit-duration','bounce-rate']
                        }

# desktop用のAPIセット
api_set_desktop = {'version': 'v1',
                        'endpoint_group': 'traffic-and-engagement',
                        'endpoint': ['visits','pages-per-visit','average-visit-duration','bounce-rate']
                        }

# mobile用のAPIセット
api_set_mobile = {'version': 'v2',
                        'endpoint_group': 'mobile-web',
                        'endpoint': ['visits','pages-per-visit','average-visit-duration','bounce-rate']
                        }

# 各デバイスのAPIセットを結合
api_set = {
    'total': api_set_total,
    'desktop':api_set_desktop,
    'mobile':api_set_mobile
}


# ## パラメータを渡してコールURLのリストを取得する関数

# In[13]:


def param_get(api_set,device,domain,API_KEY,start_date,end_date):
    url_dict = {}
    version = api_set[device]['version']
    endpoint_group = api_set[device]['endpoint_group']
    for point in api_set[device]['endpoint']:
        endpoint = point
        url_dict[point] = get_call_url(version,domain,endpoint_group,endpoint,API_KEY,start_date,end_date)
    return(url_dict)


# ## 結果の取得・csvへの格納

# In[26]:


# 空のデータフレーム
result_df = pd.DataFrame(index=[],columns=[])

# 取得するデバイス
devices = ['total','desktop','mobile']

for device in devices:

    # パラメータを渡して、APIコール用のURLを辞書に格納
    url_dict = param_get(api_set,device,domain,API_KEY,start_date,end_date)

    # インデックスのデータフレームを取得
    json_for_index = get_api_data(url_dict['visits'])
    index = get_index_data(json_for_index,device)

    # 指標のデータフレームを取得
    for endpoint,call_url in url_dict.items():
        json_result = get_api_data(call_url)
        endpoint = endpoint.replace('-','_')
        metrics = get_metrics(json_result,endpoint)
        index = pd.merge(index, metrics, on='期間')
    
    # デバイスごとのインデックス、指標をデータフレームに追加
    result_df = result_df.append(index)


# In[27]:


# 結果の描画
result_df


# In[28]:


# csvに格納
result_df.to_csv("result.csv", index=False, mode='a', header=False)


# In[31]:


# pyファイルに変換して保存
subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'ファイル名.ipynb'])

