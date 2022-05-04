from flask import Flask, request, url_for, render_template, redirect, Blueprint
import sqlalchemy as dbb
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import plotly
from pmdarima.arima import ndiffs
import pmdarima as pm
import numpy as np


bp = Blueprint('main', __name__, url_prefix='/')



@bp.route('/')
def index():
    return render_template("index.html")



@bp.route('/login', methods=['POST'])
def login_():
    request.method = 'POST' 
    if request.form["id_"] == "asd" and request.form["pw_"] == "asd":
        return redirect(url_for("main.main"))
    else:
        return redirect(url_for("main.index"))


@bp.route('/main')
def main():
    return render_template("main.html")


@bp.route('/search', methods=['POST'])
def main_():
    request.method = 'POST' 
    name = request.form["search_"]
    start = request.form["start_date_"]
    end = request.form["end_date_"] 
    period_time = int(request.form["contact"])
    
    engine = dbb.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                                .format(host="ls-a20f4420f7aa9967e25c1e0aecf4d8b641af5f13.cgtgapkuvqbt.ap-northeast-2.rds.amazonaws.com",
                                        user="dbmasteruser",
                                        pw="r,3Ipn|O7mL2vL4S)9Q~;7QVdHMV6R9j",
                                        db="stock"))

    connection = engine.connect()
    metadata = dbb.MetaData()
    table = dbb.Table('date_index', metadata, autoload=True, autoload_with=engine)

    columns_pd = table.columns.keys()

    query = dbb.select([table])
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    
    date_index = pd.DataFrame(data=result_set, columns=columns_pd) 
    
    # 인덱스 가져오기
    ####################################################################################
    # 주식데이터 가져오기

    table = dbb.Table(name, metadata, autoload=True, autoload_with=engine)

    columns_pd = table.columns.keys()

    query = dbb.select([table])
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    stock_data = pd.DataFrame(data=result_set, columns=columns_pd)

    #인덱스와 머지
    globals()[name]=pd.merge(date_index, stock_data , how='left', on='date')

    start_date = start+" 09:00:00"
    end_date = end+" 09:00:00"

    #int64index기 때문에 list로 변환후 0번째로 꺼내서 숫자로 설정
    first = globals()[name].index[globals()[name]['date'] == start_date].tolist()[0]
    last = globals()[name].index[globals()[name]['date'] == end_date].tolist()[0]
    
    #1날짜까지짜르고 2앞의값으로채우고 3인덱스리셋 4date타입을 스트링으로변경(차트빈공간채우기위함)
    globals()[name]=globals()[name].iloc[first:last+382,:]
    globals()[name]=globals()[name].fillna(method='ffill')
    #globals()[name]['date'] = globals()[name]['date'].apply(lambda x : datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))              
    #globals()[name]=globals()[name].set_index('date')    

    #radio값에 맞춰서 분봉설정
    if period_time == 1:
        globals()[name]=globals()[name].iloc[::period_time,:]
    elif period_time == 5:
        globals()[name]=globals()[name].iloc[::period_time,:]
        #하루 단위로 끊어서 15시 15분까지, 15, 30, 35
    elif period_time == 60:
        globals()[name]=globals()[name].iloc[::period_time,:]
        #9 10 11 12 13 14 15 총 7개
    elif period_time == 382:
        globals()[name]=globals()[name].iloc[381::period_time,:]
        #종가


    ###최종 df
    each_df = globals()[name]


    y_train = each_df['close'].iloc[:len(each_df['close']) - round(len(each_df['close'])*0.3)] #기준행 1504 
    y_test = each_df['close'].iloc[len(each_df['close']) - round(len(each_df['close'])*0.3):] #70프로로 짜름
    y_train.plot()
    y_test.plot()



    #차분 차수 찾기
    kpss_diffs = ndiffs(y_train, alpha=0.05 , test='kpss', max_d = 6)
    adf_diffs = ndiffs(y_train, alpha=0.05, test='adf', max_d=6)
    n_diffs = max(adf_diffs,kpss_diffs)


    send_1 = f'{globals()[name]}의 적정 차분 차수는 {n_diffs}'


    model = pm.auto_arima(y=y_train,
                    d = 1,
                    start_p=0,
                    max_p=3,
                    start_q=0,
                    max_q=3,
                    seasonal=False,
                    stepwise=True,
                    trace = True)
    
    model.fit(y_train)    
    model.plot_diagnostics(figsize=(16,8))

    
    send_2 = model.summary()

    y_predict = model.predict(n_periods=len(y_test))
    y_predict = pd.DataFrame(y_predict, index=y_test.index, columns=['Prediction'])
    y_predict
    

    def forcast_one_step():
        fc, conf_int = model.predict(n_periods=1, return_conf_int=True)
        return (fc.tolist()[0] , np.asarray(conf_int).tolist()[0] )


    forcast_one_step()
    
    forcast_list=[]
    y_pred = []
    pred_upper=[]
    pred_lower = []

    for i in y_test:
        fc , conf = forcast_one_step()
        y_pred.append(fc)
        pred_upper.append(conf[1])
        pred_lower.append(conf[0])
        model.update(i)
    


    send_3 = f"평균 절대 비율 오차: {np.mean(np.abs((y_test - y_pred) / y_test)) * 100:.2f}%"
    send_4 = f"평균 괴리율: {np.mean((y_pred - y_test) / y_test) *100:.3f} %"

    
    import plotly.graph_objects as go
    fig = go.Figure([
        go.Scatter(x=y_train.index , y=y_train, name='Train', mode='lines',line=dict(color='royalblue')),
        #테스트데이터
        go.Scatter(x=y_test.index , y=y_test, name='Test', mode='lines',line=dict(color='red')),
        #predict 데이터
        go.Scatter(x=y_test.index , y=y_pred, name='Prediction', mode='lines',line=dict(color='yellow', dash='dot', width=3)),
        #신뢰구간
        go.Scatter(x=y_test.index.tolist() + y_test.index[::-1].tolist() ,
                y= pred_upper + pred_lower[::-1],
               fill='toself',
                fillcolor='rgba(0,0,30,0.1)',
                line={'color':'rgba(0,0,0,0)'},
                hoverinfo="skip",
                showlegend=True
              )
                ])
    fig.layout = dict(xaxis = dict(type="category", 
                                    categoryorder='category ascending'))
    fig.update_layout(height=400 , width=1000, title_text=globals()[name])
    fig.update_xaxes(nticks=5)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("stock.html", graphJSON=graphJSON, df=each_df, name=name, send_1=send_1, send_2=send_2, send_3=send_3, send_4=send_4) #, header=header,description=description)


#@app.route('/stock/주식코드명')
#def main():
    #return render_template("main.html", chart_iplot=asd)

