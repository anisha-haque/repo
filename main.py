
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc

# Load data
df = pd.read_csv(r'/Users/anisha/Downloads/processed_login_data.csv')
df_registration=pd.read_csv(r'/Users/anisha/Downloads/thedealspoint.csv',low_memory=False)
df_redemption=pd.read_csv(r'/Users/anisha/Downloads/r.csv',low_memory=False)

df['logged_on'] = pd.to_datetime(df['logged_on'])
total_logins = len(df)
unique_logins = df['decrypt(u.login)'].nunique()
login_by_location = df.groupby('location').size().reset_index(name='login_count_by_location')
top_locations = login_by_location.nlargest(7, 'login_count_by_location')
df['gender'] = df['gender'].replace({'Male': 'Male', 'Female': 'Female', 'undisclosed': 'Undisclosed'})
df['gender'].fillna('Undisclosed', inplace=True)
total_registration=len(df_registration)
active_employees=len(df_registration[df_registration['status']==1])
total_redemption=len(df_redemption[df_redemption['Amazon_Store']==1])+len(df_redemption[df_redemption['Merchandise']==1])+len(df_redemption[df_redemption['Experience']==1])
#print(total_redemption)

# Replace platform_type labels
df['platform_type'] = df['platform_type'].replace({'android': 'Android', 'ios': 'iOS', 'web': 'Web', 'others': 'Others'})
df['platform_type'].fillna('Undisclosed', inplace=True)

# Calculate login counts by age
login_by_age = df.groupby('age_range').size().reset_index(name='login_count_by_age')
#redemption_by_age=df_redemption.groupby('')
# Calculate login counts by gender
login_by_gender = df.groupby('gender').size().reset_index(name='login_count_by_gender')

# Calculate login counts by platform type
login_by_platform_type = df.groupby('platform_type').size().reset_index(name='login_count_by_platform_type')

df_filtered = df_redemption[(df_redemption['Amazon_Store'] > 0) | (df_redemption['Merchandise'] > 0) | (df_redemption['Experience'] > 0)]

# Calculate redemptions by age
redemption_by_age = df_filtered.groupby('age_range').size().reset_index(name='redemption_by_age')

# Calculate redemptions by gender
redemption_by_gender = df_filtered.groupby('gender_x').size().reset_index(name='redemption_by_gender')
redemption_by_category = df_filtered[['Amazon_Store', 'Merchandise', 'Experience']].sum().reset_index()
redemption_by_category.columns = ['Category', 'Redemptions']


custom_colors = ['#5156BD', '#FBB446', '#1ACF98', '#C2C2C2', '#6540B7']

def create_donut_chart(data, logo_path):

    fig = px.pie(data, values=data.columns[1], names=data.columns[0], hole=0.8, color_discrete_sequence=custom_colors)
    fig.update_traces(textinfo='none')
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0,
        xanchor="right",
        x=0,
        font=dict(size=10)
    ), autosize=False, width=250, height=180, margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=4
    ))
    fig.add_layout_image(
        dict(source=logo_path,
             x=0.4,
             y=0.6,
             sizex=0.2,
             sizey=0.2,
             xref="paper",
             yref="paper",
             opacity=1.0,
             layer="above")
    )

    return dcc.Graph(figure=fig,config={
        'displayModeBar': False},style={"margin-right": "20px"})


def create_donut_chart_with_divider(data, logo_path):
    # Create a list of components with badges and dividers
    components = [
        create_donut_chart(data, logo_path),
        dmc.Divider(orientation="vertical", style={"height":160}),
        create_donut_chart(data, logo_path),
        dmc.Divider(orientation="vertical", style={"height":160}),
        create_donut_chart(data, logo_path)
    ]

    # Wrap the list of components in a dmc.Group
    return dmc.Group(components)

def location_bar_chart(title, x, y, xaxis_title, yaxis_title, logo_path):
    fig = go.Figure(data=go.Bar(x=x, y=y, marker=dict(color=['#5156BD', '#686DCB', '#9295D0', '#C3C6F4',
                                                             '#D8C3FF', '#EFCCFF', '#FFD6F3'])))
    fig.update_layout(
        title=title,
        xaxis=dict(title=xaxis_title, showline=True, linecolor='rgba(0, 0, 0, 0.14)', linewidth=2),
        yaxis=dict(title=yaxis_title, griddash="dot", gridwidth=2, gridcolor='rgba(0, 0, 0, 0.14)'),
        bargap=0.1,
        margin=dict(l=150, r=150, t=33, b=30),
        title_x=0.07,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    fig.update_traces(width=0.2)
    fig.add_layout_image(
        dict(source=logo_path,
             x=-0.1,  # Adjust x-coordinate as needed
             y=1.09,  # Adjust y-coordinate as needed
             sizex=0.07,  # Adjust size as needed
             sizey=0.07,  # Adjust size as needed
             xref="paper",
             yref="paper",
             opacity=1.0,
             layer="above")
    )
    return fig

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                dbc.CardHeader(html.H4("Logins"), style={'background-color': '#9395D0',
                                                         'width': "200px",
                                                         'border-radius': '10px 10px 0px 0px'},
                              className="card-header-custom"),
                html.Br(),
                dbc.CardBody([
                    html.Div([
                        html.Span("Total Logins", className="total-login",
                                  style={'font-size': '13px', 'color': '#637180'}),
                        html.Div(f'{total_logins/1000:.2f}K' if total_logins >= 1000 else total_logins,
                                 style={'font-weight': 'bold', 'font-size': '16px'}),
                    ]),
                    html.Hr(),
                    html.Div([
                        html.Span("Unique Logins", style={'font-size': '13px', 'color': '#637180'}),
                        html.Div(f'{unique_logins/1000:.2f}K' if unique_logins >= 1000 else unique_logins,
                                 style={'font-weight': 'bold', 'font-size': '16px'}),
                    ]),
                ]),
            ],
                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '200px', 'height': '250px'},
            ),
            width=2
        ),
        dbc.Col(
            dbc.Card(children=[
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P("By Age", style={'text-align': 'center','font-size':'20px'}),
                            create_donut_chart_with_divider(login_by_age, "assets/age.png")
                        ], width=4),


                        dbc.Col([
                            html.P("By Gender", style={'text-align': 'center','font-size':'20px'}),
                            create_donut_chart_with_divider(login_by_gender, "assets/gender.png")
                        ], width=4),

                        dbc.Col([
                            html.P("By Platform Type", style={'text-align': 'center','font-size':'20px'}),
                            create_donut_chart(login_by_platform_type, "assets/platform.png")
                        ], width=4)
                    ]),
                ]),
            ], className='card', style={'border': '2px solid #ffffff',
                                        'border-radius': '10px',
                                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                                        'width': '100%', 'height': '250px'}),
            width=10
        ),
    ],style={'margin-bottom': '10px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                html.Br(),
                dbc.CardBody([
                    dcc.Graph(
                        figure=location_bar_chart('Login Count by Location (Top 7)', top_locations['location'], top_locations['login_count_by_location'],'By Location','Login',"assets/loc.png")

                    )
                ]),
            ],

                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '100%', 'height': '100%'},  # Adjusted width to 100%
            ),
            width=12  # Adjusted width to 12 (full width)
        ),
    ],style={'margin-bottom': '10px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                dbc.CardHeader(html.H4("Registration"), style={'background-color': '#9395D0',
                                                         'width': "200px",
                                                         'border-radius': '10px 10px 0px 0px'},
                               className="card-header-custom"),
                html.Br(),
                dbc.CardBody([
                    html.Div([
                        html.Span("Total Registration", className="total-registration",
                                  style={'font-size': '13px', 'color': '#637180'}),
                        html.Div(f'{total_registration / 1000:.2f}K' if total_registration >= 1000 else total_registration,
                                 style={'font-weight': 'bold', 'font-size': '16px'}),
                    ]),
                    html.Hr(),
                    html.Div([
                        html.Span("Active Employees", style={'font-size': '13px', 'color': '#637180'}),
                        html.Div(f'{active_employees / 1000:.2f}K' if active_employees >= 1000 else active_employees,
                                 style={'font-weight': 'bold', 'font-size': '16px'}),
                    ]),
                ]),
            ],
                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '200px', 'height': '250px'},
            ),
            width=2
        ),
dbc.Col(
            dbc.Card(children=[
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P("By Age", style={'text-align': 'center','font-size':'20px'}),
                            create_donut_chart_with_divider(login_by_age, "assets/age.png")
                        ], width=4),
                        dbc.Col([
                            html.P("By Gender", style={'text-align': 'center','font-size':'20px'}),
                            create_donut_chart(login_by_gender, "assets/gender.png")
                        ], width=4),



                    ]),
                ]),
            ], className='card', style={'border': '2px solid #ffffff',
                                        'border-radius': '10px',
                                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                                        'width': '100%', 'height': '250px'}),
            width=10
        ),
    ],style={'margin-bottom': '10px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                html.Br(),
                dbc.CardBody([
                    dcc.Graph(
                        figure=location_bar_chart('Registration Count by Location', top_locations['location'], top_locations['login_count_by_location'], "By Location","Registration","assets/loc.png")

                    )
                ]),
            ],
                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '100%', 'height': '100%'},  # Adjusted width to 100%
            ),
            width=12  # Adjusted width to 12 (full width)
        ),
    ],style={'margin-bottom': '10px'}),
dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                dbc.CardHeader(html.H4("Redemption"), style={'background-color': '#9395D0',
                                                         'width': "200px",
                                                         'border-radius': '10px 10px 0px 0px'},
                               className="card-header-custom"),
                html.Br(),
                dbc.CardBody([
                    html.Div([
                        html.Span("Total Redemption", className="total-registration",
                                  style={'font-size': '13px', 'color': '#637180'}),
                        html.Div(f'{total_redemption / 1000:.2f}K' if total_redemption >= 1000 else total_redemption,
                                 style={'font-weight': 'bold', 'font-size': '16px'}),
                    ]),

                ]),
            ],
                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '200px', 'height': '250px'},
            ),
            width=2
        ),
dbc.Col(
            dbc.Card(children=[
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P("By Age", style={'text-align': 'center','font-size':'20px'}),
                         create_donut_chart_with_divider(redemption_by_age, "assets/age.png")],width=4),

                        dbc.Col([
                            html.P("By Gender",style={'text-align':'center','font-size':'20px'}),
                        create_donut_chart_with_divider(redemption_by_gender, "assets/gender.png")], width=4),
                        dbc.Col([html.P("By Category",style={'text-align':'center','font-size':'20px'}),
                        create_donut_chart(redemption_by_category,"assets/platform.png")], width=4),
                    ]),
                ]),
            ], className='card', style={'border': '2px solid #ffffff',
                                        'border-radius': '10px',
                                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                                        'width': '100%', 'height': '250px'}),
            width=10
        ),
    ],style={'margin-bottom': '10px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(children=[
                html.Br(),
                dbc.CardBody([
                    dcc.Graph(
                        figure=location_bar_chart('Redemption Count by Location', top_locations['location'], top_locations['login_count_by_location'],"By Location","Redemption", "assets/loc.png")

                    )
                ]),
            ],
                className='card',
                style={'border': '2px solid #ffffff',
                       'border-radius': '10px',
                       'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                       'width': '100%', 'height': '100%'},  # Adjusted width to 100%
            ),
            width=12  # Adjusted width to 12 (full width)
        ),
    ],style={'margin-bottom': '10px'})
    ], style={'padding': '15px 50px 15px 10px'})

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)

