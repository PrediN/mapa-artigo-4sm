"""
Heatmap de proximidade dos pontos de coleta/revitalização em São Paulo,
dividido pelas 5 macrorregiões da cidade (Norte, Sul, Leste, Oeste, Centro).
Lê os geojsons de pontos (CRS original: EPSG:31983 - SIRGAS 2000 / UTM 23S),
reprojeta pra Web Mercator (EPSG:3857) e, pra cada macrorregião, estima a
densidade de pontos via KDE (kernel density estimate) recortada nos limites
da própria região, pra mostrar onde eles se concentram em cada uma — todas
no mesmo painel e na mesma escala de cor, pra permitir comparação entre
regiões.
"""

import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.ops import unary_union
from scipy.stats import gaussian_kde

POLIGONO_SUBPREFEITURAS = "/home/psanchez/Faculdade/mapa-artigo-4sm/subprefeitura_v2.geojson"
COLUNA_REGIAO = "nm_regiao_05"

# --- 1. Arquivos de entrada ---
CAMADAS_PONTOS = {
    "Ecoponto": "/home/psanchez/Faculdade/mapa-artigo-4sm/ecoponto.geojson",
    "Ponto de Entrega Voluntária": "/home/psanchez/Faculdade/mapa-artigo-4sm/ponto_entrega_voluntaria.geojson",
}

GRID_RES = 200  # resolução da grade do heatmap (pixels por eixo), por região

# Grade 2x3 (2 linhas, 3 colunas), pra deixar os painéis mais próximos uns
# dos outros — a última célula (linha 1, coluna 2) fica vazia/oculta.
POSICOES_REGIOES = {
    "Norte": (0, 0),
    "Leste": (0, 1),
    "Sul": (0, 2),
    "Oeste": (1, 0),
    "Centro": (1, 1),
}
GRADE_LINHAS, GRADE_COLUNAS = 2, 3

# --- 2. Leitura + reprojeção pra Web Mercator ---
subprefs = gpd.read_file(POLIGONO_SUBPREFEITURAS).to_crs(epsg=3857)

pontos = gpd.GeoDataFrame(
    pd.concat(
        [gpd.read_file(caminho).to_crs(epsg=3857) for caminho in CAMADAS_PONTOS.values()],
        ignore_index=True,
    ),
    crs=3857,
)

# --- 3. KDE por macrorregião ---
densidades = {}
for regiao in POSICOES_REGIOES:
    subprefs_regiao = subprefs[subprefs[COLUNA_REGIAO] == regiao]
    limite_regiao = unary_union(subprefs_regiao.geometry)

    pontos_regiao = pontos[pontos.within(limite_regiao)]
    xs = pontos_regiao.geometry.x.to_numpy()
    ys = pontos_regiao.geometry.y.to_numpy()

    kde = gaussian_kde(np.vstack([xs, ys]))

    minx, miny, maxx, maxy = subprefs_regiao.total_bounds
    grid_x, grid_y = np.mgrid[
        minx:maxx:complex(GRID_RES),
        miny:maxy:complex(GRID_RES),
    ]
    densidade = kde(np.vstack([grid_x.ravel(), grid_y.ravel()])).reshape(grid_x.shape)

    # Mascara o que cai fora do limite da região, pra não pintar heatmap
    # sobre área de outra macrorregião
    dentro_da_regiao = shapely.contains_xy(limite_regiao, grid_x, grid_y)
    densidade = np.where(dentro_da_regiao, densidade, np.nan)

    densidades[regiao] = {
        "subprefs": subprefs_regiao,
        "grid_x": grid_x,
        "grid_y": grid_y,
        "densidade": densidade,
        "extent": (minx, maxx, miny, maxy),
        "n_pontos": len(pontos_regiao),
    }

# --- 4. Basemap: precisa de API key da CARTO (Positron/DarkMatter, mudança
# de ago/2026).
carto_key = "INSERIR A CHAVE DE API!"
provider = ctx.providers.CartoDB.Positron
provider["apikey"] = carto_key

# --- 5. Plot: grade 2x3, painéis mais próximos entre si ---
fig, axes = plt.subplots(
    GRADE_LINHAS,
    GRADE_COLUNAS,
    figsize=(16, 11),
    gridspec_kw={"wspace": 0.05, "hspace": 0.15},
)

for regiao, (linha, coluna) in POSICOES_REGIOES.items():
    ax = axes[linha, coluna]
    dados = densidades[regiao]

    dados["subprefs"].plot(ax=ax, facecolor="none", edgecolor="black", linewidth=0.6, zorder=2)

    heatmap = ax.imshow(
        dados["densidade"].T,
        origin="lower",
        extent=dados["extent"],
        cmap="inferno",
        vmin=0,
        vmax=np.nanmax(dados["densidade"]),
        alpha=0.75,
        zorder=1.5,
    )

    ctx.add_basemap(ax, source=provider, zorder=0)

    ax.set_title(f"{regiao} ({dados['n_pontos']} pontos)", fontsize=12, fontweight="bold")
    ax.set_axis_off()

    # Escala independente por região: cada painel destaca onde a densidade
    # se concentra DENTRO da própria região (não dá pra comparar magnitude
    # absoluta entre regiões diferentes)
    cbar = fig.colorbar(heatmap, ax=ax, fraction=0.04, pad=0.02)
    cbar.ax.tick_params(labelsize=7)

for linha in range(GRADE_LINHAS):
    for coluna in range(GRADE_COLUNAS):
        if (linha, coluna) not in POSICOES_REGIOES.values():
            axes[linha, coluna].axis("off")

fig.suptitle(
    "Heatmap de proximidade por macrorregião — Ecoponto e Ponto de Entrega "
    f"Voluntária em São Paulo ({len(pontos)} pontos, escala de cor "
    "independente por região)",
    fontsize=16,
    fontweight="bold",
)

plt.savefig("/home/psanchez/Faculdade/mapa-artigo-4sm/mapa.png", dpi=200, bbox_inches="tight")
print("Mapa salvo em /home/psanchez/Faculdade/mapa-artigo-4sm/mapa.png")
