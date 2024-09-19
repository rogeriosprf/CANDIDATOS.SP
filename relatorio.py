import os
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from PIL import Image
import base64
from io import BytesIO
from flask import Flask, Response

# Criar a aplicação Dash
app = Dash(__name__)

# Define a função de formatação com suporte para milhões, milhares e valores menores
def format_value(valor):
    if valor >= 1e12:
        return "{:,.0f}T".format(valor / 1e12).replace(',', '.')  # Trilhões
    elif valor >= 1e9:
        return "{:,.0f}B".format(valor / 1e9).replace(',', '.')   # Bilhões
    elif valor >= 1e6:
        return "{:,.0f}M".format(valor / 1e6).replace(',', '.')   # Milhões
    elif valor >= 1e3:
        return "{:,.0f}k".format(valor / 1e3).replace(',', '.')   # Milhares
    return "{:,.0f}".format(valor).replace(',', '.')             # Valores menores

def apply_mask(valor):
    """Aplica máscara para o valor no padrão brasileiro com R$"""
    try:
        valor_num = float(valor.replace('.', '').replace(',', '.'))
        return "R$ {:,.2f}".format(valor_num).replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        return valor

def encode_image(image_file):
    pil_img = Image.open(image_file)
    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def convert_to_float(value_str):
    value_str = value_str.replace('.', '').replace(',', '.')
    try:
        return float(value_str)
    except ValueError:
        print(f"Erro ao converter o valor: {value_str}")
        return None

def generate_graphs(subfolder):
    df_receitas = pd.read_excel(os.path.join(subfolder, "receitas.xlsx"), sheet_name="Receitas")
    df_despesas = pd.read_csv(os.path.join(subfolder, "despesas.csv"), delimiter=";")

    # Converte a coluna 'Valor' usando a função convert_to_float
    df_receitas['Valor'] = df_receitas['Valor'].astype(str).apply(convert_to_float)
    df_despesas['Valor'] = df_despesas['Valor'].str.replace(',', '.')
    df_despesas['Valor'] = pd.to_numeric(df_despesas['Valor'], errors='coerce')

    # Agrupa e soma os valores
    receita_agrupada = df_receitas.groupby('Nome do Doador')['Valor'].sum().reset_index()
    despesa_agrupada = df_despesas.groupby('Nome do Fornecedor')['Valor'].sum().reset_index()

    # Calcula o total de receitas e despesas
    total_receitas = df_receitas['Valor'].sum()
    total_despesas = df_despesas['Valor'].sum()

    # Formata os valores para exibição nos rótulos e tooltips
    rótulos_receitas_formatados = receita_agrupada['Valor'].apply(format_value)
    rótulos_despesas_formatados = despesa_agrupada['Valor'].apply(format_value)

    # Formata o total de receitas e despesas
    total_receitas_formatado = format_value(total_receitas)
    total_despesas_formatado = format_value(total_despesas)

    # Carregar a imagem
    image_file = os.path.join(subfolder, 'foto.jpg')
    img_encoded = encode_image(image_file)

    # Cria o gráfico de receitas
    if len(receita_agrupada) > 15:
        receita_agrupada_limited = receita_agrupada.nlargest(15, 'Valor')
        link = f"/mostrar_todos_receitas/{subfolder.replace('/', '_')}"
        title = f"Top 15 Receitas ({total_receitas_formatado}) - <a href='{link}' target='_blank'>Mostrar Todos</a>"
    else:
        receita_agrupada_limited = receita_agrupada
        title = f"Receita Total ({total_receitas_formatado})"

    bar_chart_receitas = go.Figure([go.Bar(
        x=receita_agrupada_limited['Nome do Doador'],
        y=receita_agrupada_limited['Valor'],
        name='Receitas',
        text=rótulos_receitas_formatados,
        textposition='auto',
        hovertemplate="<b>Doador:</b> %{x}<br><b>Valor:</b> %{y:,.0f}<extra></extra>",
    )])
    bar_chart_receitas.update_layout(
        title=title,
        yaxis=dict(showticklabels=True, title=''),
        xaxis=dict(showticklabels=True, title=''),
    )

    # Cria o gráfico de despesas
    if len(despesa_agrupada) > 15:
        despesa_agrupada_limited = despesa_agrupada.nlargest(15, 'Valor')
        link = f"/mostrar_todos_despesas/{subfolder.replace('/', '_')}"
        title = f"Top 15 Despesas ({total_despesas_formatado}) - <a href='{link}' target='_blank'>Mostrar Todos</a>"
    else:
        despesa_agrupada_limited = despesa_agrupada
        title = f"Despesa Total ({total_despesas_formatado})"

    bar_chart_despesas = go.Figure([go.Bar(
        x=despesa_agrupada_limited['Nome do Fornecedor'],
        y=despesa_agrupada_limited['Valor'],
        name='Despesas',
        text=rótulos_despesas_formatados,
        textposition='auto',
        hovertemplate="<b>Fornecedor:</b> %{x}<br><b>Valor:</b> %{y:,.0f}<extra></extra>",
        marker_color='lightcoral'
    )])
    bar_chart_despesas.update_layout(
        title=title,
        yaxis=dict(showticklabels=True, title=''),
        xaxis=dict(showticklabels=True, title=''),
    )

    # Cria o gráfico de totais
    bar_chart_totais = go.Figure([go.Bar(
        x=['Receitas', 'Despesas'],
        y=[total_receitas, total_despesas],
        name='Totais',
        text=[total_receitas_formatado, total_despesas_formatado],
        textposition='auto',
        marker_color=['dodgerblue', 'lightcoral']
    )])
    bar_chart_totais.update_layout(
        title=f"Totais",
        yaxis=dict(showticklabels=True, title=''),
        xaxis=dict(showticklabels=True, title=''),
    )

    return img_encoded, bar_chart_receitas, bar_chart_despesas, bar_chart_totais

# Lista as subpastas dentro da pasta 'dados'
base_folder = 'dados'
subfolders = [os.path.join(base_folder, f) for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

# Define o layout do app
app.layout = html.Div(children=[
    html.H1(children='Relatório de Receitas e Despesas dos candidatos a prefeitura de São Paulo 2024'),
    dcc.Dropdown(
        id='subfolder-dropdown',
        options=[{'label': os.path.basename(f), 'value': f} for f in subfolders],
        value=subfolders[0] if subfolders else None
    ),
    html.Div(id='graph-container'),
])

@app.callback(
    Output('graph-container', 'children'),
    Input('subfolder-dropdown', 'value')
)
def update_graphs(subfolder):
    if not subfolder:
        return html.Div('Nenhuma pasta selecionada')

    # Gera gráficos para a subpasta selecionada
    img_encoded, bar_chart_receitas, bar_chart_despesas, bar_chart_totais = generate_graphs(subfolder)

    return html.Div(children=[
        html.Div(children=[
            html.Img(src=img_encoded, style={'height': '250px', 'width': 'auto', 'margin-right': '20px'}),
            html.H1(children=os.path.basename(subfolder), style={'display': 'inline'})
        ], style={'display': 'flex', 'align-items': 'center'}),

        dcc.Graph(id='Receitas', figure=bar_chart_receitas),
        dcc.Graph(id='Despesas', figure=bar_chart_despesas),
        dcc.Graph(id='Totais', figure=bar_chart_totais),
    ])

# Define as rotas para as páginas de mostrar todos os dados
@app.server.route('/mostrar_todos_receitas/<subfolder>')
def mostrar_todos_receitas(subfolder):
    subfolder = subfolder.replace('_', '/')
    df_receitas = pd.read_excel(os.path.join(subfolder, "receitas.xlsx"), sheet_name="Receitas")
    df_receitas = df_receitas[['Nome do Doador', 'Valor']]
    df_receitas['Valor'] = df_receitas['Valor'].apply(apply_mask)  # Aplica a máscara
    html_table = df_receitas.to_html(index=False, border=1, classes='dataframe', header=True)
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            .dataframe {{
                border-collapse: collapse;
                width: 100%;
            }}
            .dataframe th, .dataframe td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            .dataframe th {{
                background-color: #f2f2f2;
            }}
            h1 {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>Total de Receitas - {os.path.basename(subfolder)}</h1>
        {html_table}
    </body>
    </html>
    """
    return Response(html_content, content_type='text/html')

@app.server.route('/mostrar_todos_despesas/<subfolder>')
def mostrar_todos_despesas(subfolder):
    subfolder = subfolder.replace('_', '/')
    df_despesas = pd.read_csv(os.path.join(subfolder, "despesas.csv"), delimiter=";")
    df_despesas = df_despesas[['Nome do Fornecedor', 'Valor']]
    df_despesas['Valor'] = df_despesas['Valor'].apply(apply_mask)  # Aplica a máscara
    html_table = df_despesas.to_html(index=False, border=1, classes='dataframe', header=True)
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            .dataframe {{
                border-collapse: collapse;
                width: 100%;
            }}
            .dataframe th, .dataframe td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            .dataframe th {{
                background-color: #f2f2f2;
            }}
            h1 {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>Total de Despesas - {os.path.basename(subfolder)}</h1>
        {html_table}
    </body>
    </html>
    """
    return Response(html_content, content_type='text/html')

if __name__ == '__main__':
    app.run_server(debug=True)
