# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:06:16 2019
@author: Ankur.Parmar@shell.com
@author : Sundar Raman Subramanian@shell.com
"""

from handlers.libraries import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

print(config_path)
# [print(file) for file in glob.glob(os.path.join(config_path, '*.json'))]
valves = [file.split("\\")[-1].split('.')[0] for file in glob.glob(os.path.join(config_path, '*.json'))]
print(valves)
filter_options = ['>', '<', '==', ">=", "<=", "!="]
model_options = ['lasso', 'ridge', 'elasticnet', 'Randomforest']
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

colors = {
    'background1': '#111111',
    'floralwhite': '#FFFAF0',
    'text_y': '#FFC125',
    'text_r': '#FF3030',
    'gold1': '#FFD700',
    'green3': '#00CD00',
    'deepsky1': '#00BFFF',
    'ghostwhite': '#F8F8FF'
}


app = dash.Dash(__name__, show_undo_redo=True)
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.layout = html.Div([html.Div('SHELL-PAM Predictive Analytics Admin Console for PDO-Qarn Alarm Steam-Control Valves',
                                style={'textAlign': 'center', 'backgroundColor': colors['green3'],
                                       'color': colors['floralwhite'], 'font_family': 'Georgia',
                                       'font-size': '20px', 'margin-left': '20px'}),
                       html.Div([html.Div([html.Div(children='Select Control Valve',
                                                    style={'color': colors['text_r'], 'text-align': 'center',
                                                           'left': '50%', 'margin-top': '20px'}),
                                           html.Div([dcc.Dropdown(id='cv',
                                                                  options=[{'label': i, 'value': i} for i in valves],
                                                                  value=valves[0])],
                                                    style={'width': '100%', 'float': 'right', 'left': '50%',
                                                           'margin-top': '0px'})],
                                          className='three columns'),
                                 html.Div([html.Div(children='Last Modified Timestamp',
                                                    style={'color': colors['text_r'], 'padding': '0px',
                                                           'margin-top': '20px'}),
                                           html.Div(id='last_modified', style={'margin-top': '0px'})],
                                          className='three columns')], className="row"),
                       html.H1('Valve Attributes',
                               style={'textAlign': 'center', 'backgroundColor': colors['green3'],
                                      'margin-top': '10px', 'font-size': '20px',
                                      'color': colors['floralwhite']}, className='row'),
                       html.Div([html.Div(children='Type', style={'color': colors['text_r'], 'padding': '0px'}),
                                 html.Div([dcc.Input(id='type', type='text')],
                                          style={'width': '100%', 'float': 'left', 'margin': '0px', 'font-size': '15px'}
                                          )], className='three columns', style={'margin': '0px'}),
                       html.Div([html.Div(children='Location', style={'color': colors['text_r'], 'padding': '0px'}),
                                 html.Div([dcc.Input(id='location', type='text')],
                                          style={'width': '100%', 'float': 'left', 'margin': '0px', 'font-size': '15px'}
                                          )], className='three columns', style={'margin': '0px'}),
                       html.Div([html.Div(children='ValvePlant', style={'color': colors['text_r'], 'padding': '0px'}),
                                 html.Div([dcc.Input(id='valve_plant', type='text')],
                                          style={'width': '100%', 'float': 'left', 'margin': '0px', 'font-size': '15px'}
                                          )], className='three columns', style={'margin': '0px'}),
                       html.Div([html.Div(children='Output PI Tag', style={'color': colors['text_r'], 'padding': '0px'}
                                          ),
                                 html.Div([dcc.Input(id='op_pi_tag', type='text')],
                                          style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                className='three columns', style={'margin': '0px'}),
                       html.Div([html.Div([html.Div(children='Description',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='desc', type='text',
                                                               style={'width': '100%'})],
                                                    className='six columns',
                                                    style={'width': '100%', 'font-size': '15px',
                                                           'padding': '0px', 'margin': '0px'})],
                                          className='six columns', style={'margin': '0px'}),
                                 html.Div([], className="row"),
                                 html.H1('Model Attributes',
                                         style={'textAlign': 'center', 'backgroundColor': colors['green3'],
                                                'margin-top': '20px', 'font-size': '20px',
                                                'color': colors['floralwhite']},
                                         className='row'),
                                 html.Div([html.Div(children='Model',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Dropdown(id='model',
                                                                  options=[{'label': i, 'value': i}
                                                                           for i in model_options],
                                                                  value='ridge')],
                                                    style={'width': '100%', 'margin': '0px', 'padding': '0px',
                                                           'font-size': '15px'})],
                                          className='three columns', style={'margin-left': '0px'}),
                                 html.Div([html.Div(children='Maximum Features',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='maximum_features', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})], className="row"),
                       html.Div([html.Div([html.Div(children='Training Period Start',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='training_period_start', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px',
                                                           'margin': '0px', 'padding': '0px'})],
                                          className='three columns'),
                                 html.Div([html.Div(children='Training Period End',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='training_period_end', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Testing Period Start',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='testing_period_start', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Testing Period End',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='testing_period_end', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})],
                                className="row"),
                       html.H1('Mode Filters',
                               style={'textAlign': 'center', 'backgroundColor': colors['green3'],
                                      'margin-top': '20px', 'font-size': '20px',
                                      'color': colors['floralwhite']}, className='row'),
                       html.Div([html.Div([html.Div(children='Mode PI Tag',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='mode_pi_tag_1', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Filter Condition',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Dropdown(id='filter_condition_1',
                                                                  options=[{'label': i, 'value': i}
                                                                           for i in filter_options],
                                                                  value=filter_options[0])],
                                                    className='six columns')],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Filter Value',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='filter_value_1', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})], className="row"),
                       html.Div([html.Div([html.Div(children='Filter PI tags',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='filter_pi_tags', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Filter Conditions',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='filter_conditions', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})],
                                className="row"),
                       html.H1('Other Filters',
                               style={'textAlign': 'center', 'backgroundColor': colors['green3'],
                                      'margin-top':'20px', 'font-size':'20px', 'color': colors['floralwhite']},
                               className='row'),
                       html.Div([html.Div([html.Div(children='Exclusion PI Tags',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='exclusion_pi_tags', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Band Pass Lower Limit',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='band_pass_lower_limit', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Band Pass Upper Limit',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='band_pass_upper_limit', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})],
                                className="row"),
                       html.H1('Alarm',
                               style={'textAlign': 'center', 'backgroundColor': colors['green3'], 'margin-top':'20px',
                                      'font-size':'20px', 'color': colors['floralwhite']},
                               className='row'),
                       html.Div([html.Div([html.Div(children='Deviation Threshold',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='deviation_threshold', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Alarm Trigger',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='alarm_trigger', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Alarm Stop',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='alarm_stop', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})],
                                className="row"),
                       html.H1('PI Details',
                               style={'textAlign': 'center', 'backgroundColor': colors['green3'], 'margin-top':'20px',
                                      'font-size':'20px', 'color': colors['floralwhite']},
                               className='row'),
                       html.Div([html.Div([html.Div(children='PiServerName',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='piservername', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'margin': '0px',
                                                           'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='Interval',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='interval', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='PI Write Back Tag for Prediction',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='pi_write_back_tag1', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'}),
                                 html.Div([html.Div(children='PI Write back Tag for KPI',
                                                    style={'color': colors['text_r'], 'padding': '0px'}),
                                           html.Div([dcc.Input(id='pi_write_back_tag2', type='text')],
                                                    style={'width': '100%', 'float': 'left', 'font-size': '15px'})],
                                          className='three columns', style={'margin': '0px'})],
                                className="row"),
                       html.H1('',
                               style={'textAlign': 'center', 'backgroundColor': colors['deepsky1'], 'margin-top':'20px',
                                      'font-size':'20px', 'color': colors['floralwhite']},
                               className='row'),
                       html.Div([html.Button('Update Config', id='button',
                                             style={'color': colors['deepsky1'], 'position': 'center', 'margin': '10px',
                                                    'margin-left': '550px'},
                                             className='three columns')
                                    # ,
                                 # html.Button('Train Valve Model', id='button1',
                                 #             style={'color': colors['deepsky1'], 'position': 'center', 'margin': '10px',
                                 #                    'margin-left':'550px'},
                                 #             className='three columns')
                                 ],
                                className='row'),
                       html.Div(id='out1')])

@app.callback([
        Output('piservername','value'),Output('valve_plant','value'),
        Output('desc','value'),Output('location','value'),
        Output('alarm_stop','value'),Output('alarm_trigger','value'),
        Output('band_pass_lower_limit','value'),Output('band_pass_upper_limit','value'),
        Output('deviation_threshold','value'),Output('interval','value'),
        Output('maximum_features','value'),Output('type','value'),
        Output('exclusion_pi_tags','value'),Output('filter_conditions','value'),
        Output('pi_write_back_tag2','value'),Output('mode_pi_tag_1','value'),
        Output('op_pi_tag','value'),Output('filter_pi_tags','value'),
        Output('pi_write_back_tag1','value'),Output('training_period_start','value'),
        Output('training_period_end','value'),Output('testing_period_start','value'),
        Output('testing_period_end','value'),Output('last_modified','children')],
        [Input('cv', 'value')])

def update_read(val):
    p = config_path+'/'+val+'.json'
    with open(p) as json_file:
        data = json.load(json_file)
        
    t = datetime.utcfromtimestamp(os.path.getmtime(p))
    t = t.replace(tzinfo=from_zone)
    t = t.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')  
        
    return(data['PIServerName'],data['ValvePlant']
           ,data['description'],data['location'],
           data['alarm_stop'],data['alarm_trigger'],
           data['band_pass_lower_limit'],data['band_pass_upper_limit'],
           data['deviation_threshold'],data['interval'],
           data['maximum_features'],data['type'],
           str(data['exclusion_pi_tags']),str(data['filter_conditions']),
           data['pi_write_back_tag'][1],data['mode_pi_tag'],
           data['op_pi_tag'],data['filter_pi_tags'],
           data['pi_write_back_tag'][0],data['training_period'][0],
           data['training_period'][1],data['testing_period'][0],
           data['testing_period'][1],t
           
           )


@app.callback(dash.dependencies.Output('out1','children'),
    [dash.dependencies.Input('button', 'n_clicks'),   #n_clicks
    dash.dependencies.Input("piservername",'value'),#1
    dash.dependencies.Input("valve_plant",'value'),#2
    dash.dependencies.Input("desc",'value'),  #3
    dash.dependencies.Input("location",'value'),#4
    dash.dependencies.Input("alarm_stop",'value'),#5
    dash.dependencies.Input("alarm_trigger",'value'),#6
    dash.dependencies.Input("band_pass_lower_limit",'value'),#7
    dash.dependencies.Input("band_pass_upper_limit",'value'),#8
    dash.dependencies.Input("deviation_threshold",'value'),#9
    dash.dependencies.Input("interval",'value'),#10
    dash.dependencies.Input("maximum_features",'value'),#11
    dash.dependencies.Input("type",'value'),#12
    dash.dependencies.Input("exclusion_pi_tags",'value'),#13
    dash.dependencies.Input("filter_conditions",'value'),#14
    dash.dependencies.Input("pi_write_back_tag2",'value'),#15
    dash.dependencies.Input("op_pi_tag",'value'),#16
    dash.dependencies.Input("filter_pi_tags",'value'),#17
    dash.dependencies.Input("pi_write_back_tag1",'value'),#18
    dash.dependencies.Input("model",'value'),#19
    dash.dependencies.Input("training_period_start",'value'),#20
    dash.dependencies.Input("training_period_end",'value'),#21
    dash.dependencies.Input("testing_period_start",'value'),#22
    dash.dependencies.Input("testing_period_end",'value'),#23
    dash.dependencies.Input("filter_condition_1",'value'),#24
    dash.dependencies.Input("filter_value_1",'value'),#25
    dash.dependencies.Input("cv",'value'),#26
    dash.dependencies.Input("mode_pi_tag_1",'value')#27
    ])

def update(n_clicks,val1,val2,val3,val4,val5,val6,val7,val8,val9,val10,val11,val12,val13,val14,val15,val16,val17,val18,val19,val20,val21,val22,val23,val24,val25,val26,val27):
    if str(n_clicks).isnumeric():
        if str(val25).isnumeric():
            val25_split = int(val25)
            v = str([str(val24),[val25_split]])
        else: 
            val25_split = str(val25).split(',') 
            val25_split = [str("'" + i + "'")  for i in val25_split]
            val25_split = [i.replace("\\",'') for i in val25_split]
            v = [str(val24),val25_split]
        l1 = [val1,val2,val3,val4,val5,val6,val7,val8,val9,val10,val11,val12,[val13[2:-2]],[val14[2:-2]],val27,val16,val17,[val18,val15],val19,[val20,val21],[val22,val23],v]
        l2 = ['PIServerName', 'ValvePlant', 'description', 'location', 'alarm_stop', 'alarm_trigger', 'band_pass_lower_limit',
              'band_pass_upper_limit', 'deviation_threshold', 'interval', 'maximum_features', 'type', 'exclusion_pi_tags', 'filter_conditions',
              'mode_pi_tag', 'op_pi_tag', 'filter_pi_tags', 'pi_write_back_tag', 'model', 'training_period', 'testing_period', 'f']
        my_details = dict(zip(l2, l1))
        path = model_path + val26 + '.json'
        with open(path, 'w') as json_file:
            json.dump(my_details, json_file)
    return ''

if __name__ == '__main__':
    app.run_server(debug=False)                                  
