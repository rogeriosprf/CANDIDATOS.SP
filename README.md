# CANDIDATOS.SP
 Relatório de receitas e despesas dos candidados a prefeitura de São Paulo em 2024.

Este projeto consiste em uma aplicação web desenvolvida com Dash que permite visualizar e analisar dados financeiros de receitas e despesas. A aplicação oferece gráficos interativos e a possibilidade de visualizar detalhes adicionais dos dados em uma página separada.

Funcionalidades
Gráficos Interativos: Visualize gráficos de receitas, despesas e totais, com opções de detalhamento.
Visualização de Dados: Acesso a detalhes adicionais através de links para páginas HTML com tabelas formatadas.
Suporte para Vários Formatos de Dados: Carregamento de arquivos CSV e XLSX para processamento de dados financeiros.
Formatação Brasileira: Valores são formatados no padrão brasileiro, incluindo o símbolo R$.

Estrutura do Projeto

Pasta dados:

Contém subpastas para cada conjunto de dados.
Cada subpasta deve incluir:
receitas.xlsx: Arquivo com receitas.
despesas.csv: Arquivo com despesas.
foto.jpg: Imagem para exibição.

Scripts:

app.py: Script principal que define a aplicação Dash e gera gráficos e páginas HTML.

Requisitos
Python: Versão 3.6 ou superior
Pacotes: Instale as dependências usando o seguinte comando:
bash
pip install dash pandas plotly pillow flask

Como Executar
Prepare os Dados:

Organize os dados em pastas conforme descrito acima.

Execute a Aplicação:

Navegue até o diretório contendo app.py e execute:
bash

python app.py
Acesse a aplicação no navegador em http://127.0.0.1:8050.
Interaja com a Aplicação:

Use o menu suspenso para selecionar uma subpasta e visualize os gráficos.
Clique em "Mostrar Todos" para acessar a tabela completa em uma nova aba.

Detalhes Técnicos

Formatação de Valores: Valores financeiros são formatados no padrão brasileiro (ex. R$ 1.234,56).
Links Dinâmicos: Se houver mais de 15 registros, um link "Mostrar Todos" é adicionado ao título do gráfico, direcionando para uma página HTML com todos os dados.
Máscara de Valor: Aplicada para garantir o padrão de formatação brasileiro.

Contribuições
Sinta-se à vontade para contribuir para este projeto. Faça um fork do repositório, crie uma branch para suas alterações e envie um pull request.

Licença
Este projeto está licenciado sob a MIT License.
