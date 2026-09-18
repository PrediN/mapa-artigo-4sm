# Mapa de Pontos de Coleta e Revitalização — São Paulo

Projeto acadêmico que visualiza, em mapas gerados a partir de dados geoespaciais, a distribuição de ecopontos, pontos de entrega voluntária (PEVs) e pontos revitalizados na cidade de São Paulo, cruzando essas informações com os limites das subprefeituras e macrorregiões da cidade.

## Scripts

### `mapa_pontos_sp.py`

Plota os pontos de coleta/revitalização sobre o mapa da cidade, com os limites das subprefeituras coloridos por região (uma cor por subprefeitura, em transparência) e um basemap ao fundo.

- Lê os três geojsons de pontos (`ecoponto.geojson`, `ponto_entrega_voluntaria.geojson`, `ponto_revitalizado.geojson`) e o geojson de subprefeituras (`subprefeitura_v2.geojson`).
- Reprojeta tudo de EPSG:31983 (SIRGAS 2000 / UTM 23S) para EPSG:3857 (Web Mercator), padrão dos tiles usados pelo `contextily`.
- Gera um mapa único com legenda, salvo como imagem PNG.

### `mapa.py`

Gera um heatmap (KDE — kernel density estimate) de proximidade dos ecopontos e PEVs, dividido nas 5 macrorregiões de São Paulo (Norte, Sul, Leste, Oeste, Centro), com um painel por região na mesma escala de cor para permitir comparação.

- Recorta a densidade estimada nos limites de cada macrorregião, evitando "vazamento" de heatmap para áreas de outras regiões.
- Salva o resultado em `mapa.png`.

## Dados de entrada

| Arquivo | Descrição |
|---|---|
| `ecoponto.geojson` | Localização dos ecopontos |
| `ponto_entrega_voluntaria.geojson` | Localização dos pontos de entrega voluntária (PEVs) |
| `ponto_revitalizado.geojson` | Localização dos pontos revitalizados |
| `subprefeitura_v2.geojson` | Limites das subprefeituras e macrorregiões de São Paulo |

Todos os arquivos vêm originalmente em EPSG:31983 (SIRGAS 2000 / UTM 23S).

> **Atenção:** os caminhos dos arquivos de entrada/saída estão *hardcoded* no topo de cada script (`mapa_pontos_sp.py` usa `/mnt/user-data/uploads/...` e `/mnt/user-data/outputs/...`; `mapa.py` usa `/home/psanchez/Faculdade/mapa-artigo-4sm/...`). Ajuste esses caminhos para o seu ambiente antes de rodar.

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Chave de API da CARTO

Os basemaps (CartoDB Positron) exigem uma API key desde a mudança de política da CARTO em agosto de 2026. Crie a sua gratuitamente em [carto.com/basemaps/apikey](https://carto.com/basemaps/apikey) e defina a variável de ambiente antes de rodar os scripts:

```bash
export CARTO_API_KEY="sua_chave_aqui"
```

> Em `mapa.py` a chave ainda está como placeholder (`"INSERIR A CHAVE DE API!"`) diretamente no código — substitua pela sua chave ou adapte o script para ler de uma variável de ambiente, como já é feito em `mapa_pontos_sp.py`.

## Como rodar

```bash
python mapa_pontos_sp.py
python mapa.py
```

Cada script salva o mapa gerado como um arquivo PNG no caminho configurado internamente.
