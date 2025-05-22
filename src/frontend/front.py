import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, Input, Output

from src.database.data import Database
from src.pipeline.logger import Logger
from src.pipeline.exception import CustomException


class Dashboard:
    def __init__(self):
        self.app = Dash(__name__)
        self.db = Database()
        self.logger = Logger()
        self._setup_layout()
        self._setup_callbacks()

    def _load_data(self):
        try:
            columns, data = self.db.fetch_data()
            df = pd.DataFrame(data, columns=columns)
            df['action_date'] = pd.to_datetime(df['action_date'], errors='coerce')
            df.dropna(subset=['action_date'], inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return pd.DataFrame()

    def _setup_layout(self):
        df = self._load_data()

        layout_filters = html.Div([
            html.Label("Date Range:", style={'fontSize': '15px'}),
            dcc.DatePickerRange(
                id='date-range-picker',
                start_date=df['action_date'].min().date() if not df.empty else pd.to_datetime("2020-01-01"),
                end_date=df['action_date'].max().date() if not df.empty else pd.to_datetime("2025-12-31"),
                display_format='YYYY-MM-DD',
                style={'width': '100%', 'fontSize': '10px'}
            ),

            html.Label("Telegramers Name:", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='name-filter',
                options=[{'label': name, 'value': name} for name in sorted(df['name'].dropna().unique())],
                multi=True,
                style={'fontSize': '15px'}
            ),

            html.Label("Campaign_Name:", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='ts-name-filter',
                options=[{'label': ts, 'value': ts} for ts in sorted(df['ts_name'].dropna().unique())],
                multi=True,
                style={'fontSize': '15px'}
            ),

            html.Label("Partners Name:", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='partner-filter',
                options=[{'label': p, 'value': p} for p in sorted(df['partner'].dropna().unique())],
                multi=True,
                style={'fontSize': '15px'}
            ),

            html.Label("UserID:", style={'fontSize': '15px'}),
            dcc.Dropdown(
                id='uid-filter',
                options=[{'label': uid, 'value': uid} for uid in sorted(df['uid'].dropna().unique())],
                multi=True,
                style={'fontSize': '15px'}
            ),

            html.Button("Refresh Data", id='refresh-button', n_clicks=0,
                        style={'fontSize': '15px', 'width': '100%', 'marginTop': '5px'})
        ], style={
            'flex': '1',
            'minWidth': '150px',
            'maxWidth': '250px',
            'padding': '5px',
            'border': '1px solid #ccc',
            'borderRadius': '8px',
            'backgroundColor': '#f9f9f9',
            'boxSizing': 'border-box',
            'overflowY': 'auto',
            'fontSize': '10px'
        })

        layout_main = html.Div([
            html.Div(id='kpi-cards', style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'space-around',
                'gap': '10px',
                'marginBottom': '20px'
            }),

            html.H3("Pivot Table", style={'textAlign': 'center'}),
            dash_table.DataTable(id='pivot-table', style_table={'overflowX': 'auto', 'width': '100%'}),

            html.H3("Graph", style={'textAlign': 'center'}),
            dcc.Graph(id='pivot-graph', style={'width': '100%'}),

            html.Div([
                html.H3("All Orders Details", style={'textAlign': 'center'}),
                dash_table.DataTable(
                    id='full-data-table',
                    style_table={'overflowX': 'auto', 'width': '100%'},
                    page_size=100
                )
            ], style={
                'width': '100%',
                'padding': '10px',
                'boxSizing': 'border-box'
            })
        ], style={'flex': '3', 'padding': '10px', 'boxSizing': 'border-box'})

        self.app.layout = html.Div([
            html.H1("Hyyzo Telegramers CRM Dashboard", style={'textAlign': 'center'}),
            html.Div([layout_filters, layout_main], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'space-between',
                'gap': '10px',
                'alignItems': 'flex-start',
                'boxSizing': 'border-box'
            })
        ], style={'padding': '10px', 'boxSizing': 'border-box'})

    def _setup_callbacks(self):
        @self.app.callback(
            Output('pivot-table', 'data'),
            Output('pivot-table', 'columns'),
            Output('pivot-graph', 'figure'),
            Output('full-data-table', 'data'),
            Output('full-data-table', 'columns'),
            Output('kpi-cards', 'children'),
            Input('name-filter', 'value'),
            Input('ts-name-filter', 'value'),
            Input('partner-filter', 'value'),
            Input('uid-filter', 'value'),
            Input('refresh-button', 'n_clicks'),
            Input('date-range-picker', 'start_date'),
            Input('date-range-picker', 'end_date')
        )
        def update_dashboard(name_filter, ts_name_filter, partner_filter, uid_filter, n_clicks, start_date, end_date):
            df = self._load_data()

            if df.empty:
                return [], [], go.Figure(), [], [], []

            if start_date and end_date:
                df = df[(df['action_date'] >= pd.to_datetime(start_date)) &
                        (df['action_date'] <= pd.to_datetime(end_date))]
            if name_filter:
                df = df[df['name'].isin(name_filter)]
            if ts_name_filter:
                df = df[df['ts_name'].isin(ts_name_filter)]
            if partner_filter:
                df = df[df['partner'].isin(partner_filter)]
            if uid_filter:
                df = df[df['uid'].isin(uid_filter)]

            if df.empty:
                return [], [], go.Figure(), [], [], []

            payout_sum = df['payout'].sum()
            point_sum = df.get('point_post_payout', pd.Series(dtype='float')).sum()
            sale_sum = df.get('sale_amount', pd.Series(dtype='float')).sum()
            total_order = df['order_id'].nunique() if 'order_id' in df.columns else 0

            kpi_cards = [
                html.Div([html.H4("Payout Sum"), html.P(f"₹ {payout_sum:,.2f}")],
                         style={'flex': '1', 'minWidth': '180px', 'textAlign': 'center'}),
                html.Div([html.H4("Point Post Payout"), html.P(f"₹ {point_sum:,.2f}")],
                         style={'flex': '1', 'minWidth': '180px', 'textAlign': 'center'}),
                html.Div([html.H4("Sale Amount"), html.P(f"₹ {sale_sum:,.2f}")],
                         style={'flex': '1', 'minWidth': '180px', 'textAlign': 'center'}),
                html.Div([html.H4("Total Order"), html.P(f"{total_order:,}")],
                         style={'flex': '1', 'minWidth': '180px', 'textAlign': 'center'})
            ]

            df['action_date'] = df['action_date'].dt.date
            pivot = df.pivot_table(
                index=['ts_name', 'action_date'],
                values='payout',
                aggfunc=['sum', 'count'],
                fill_value=0
            ).reset_index()

            pivot.columns = ['ts_name', 'action_date', 'total_payout', 'total_orders']
            pivot_data = pivot.to_dict('records')
            pivot_columns = [{'name': col, 'id': col} for col in pivot.columns]

            fig = go.Figure()
            for ts in pivot['ts_name'].unique():
                subset = pivot[pivot['ts_name'] == ts]
                fig.add_trace(go.Scatter(
                    x=subset['action_date'],
                    y=subset['total_payout'],
                    name=f"{ts} - Payout",
                    line=dict(color='orange'),
                    mode='lines+markers+text',
                    text=subset['total_payout'],
                    textposition='top center'
                ))
                fig.add_trace(go.Scatter(
                    x=subset['action_date'],
                    y=subset['total_orders'],
                    name=f"{ts} - Orders",
                    line=dict(color='blue'),
                    mode='lines+markers+text',
                    text=subset['total_orders'],
                    textposition='bottom center',
                    yaxis='y2'
                ))

            fig.update_layout(
                xaxis=dict(title='Date'),
                yaxis=dict(title='Total Payout'),
                yaxis2=dict(title='Total Orders', overlaying='y', side='right'),
                title="Orders and Payout Over Time",
                hovermode='x unified'
            )

            full_data = df.head(10).to_dict('records')
            full_columns = [{'name': col, 'id': col} for col in df.columns]

            return pivot_data, pivot_columns, fig, full_data, full_columns, kpi_cards

    def run(self):
        self.logger.info("Starting Dash server...")
        self.app.run(debug=True)


dashboard = Dashboard()
app = dashboard.app  # <- expose Dash's internal Flask server

if __name__ == "__main__":
    dashboard.run()
