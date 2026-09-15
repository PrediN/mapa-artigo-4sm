"""
Mapa de pontos de coleta/revitalização em São Paulo.
Lê 3 geojsons (CRS original: EPSG:31983 - SIRGAS 2000 / UTM 23S),
reprojeta pra Web Mercator (EPSG:3857) e plota cada categoria com
uma cor diferente sobre um basemap.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# --- 1. Arquivos de entrada e cor de cada categoria ---
CAMADAS = {
    "Ecoponto":                    ("/mnt/user-data/uploads/ecoponto.geojson", "#1f77b4"),
    "Ponto de Entrega Voluntária": ("/mnt/user-data/uploads/ponto_entrega_voluntaria.geojson", "#2ca02c"),
    "Ponto Revitalizado":          ("/mnt/user-data/uploads/ponto_revitalizado.geojson", "#d62728"),
}

# --- 2. Leitura + reprojeção pra Web Mercator (padrão dos tiles do contextily) ---
gdfs = {}
for nome, (caminho, cor) in CAMADAS.items():
    gdf = gpd.read_file(caminho)
    gdfs[nome] = gdf.to_crs(epsg=3857)

# --- 3. Plot ---
fig, ax = plt.subplots(figsize=(12, 12))

for nome, (_, cor) in CAMADAS.items():
    gdfs[nome].plot(
        ax=ax,
        color=cor,
        markersize=8,
        alpha=0.7,
        label=f"{nome} ({len(gdfs[nome])})",
    )

# Basemap (requer internet na hora de rodar — baixa os tiles sob demanda)
# OBS: o tile server oficial do OSM (tile.openstreetmap.org) bloqueia acesso
# automatizado via contextily (retorna 403 "Access blocked"). CartoDB é
# construído sobre dados do OSM mas permite esse tipo de uso em apps/scripts.
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

ax.set_title("Pontos de coleta e revitalização — São Paulo", fontsize=14, fontweight="bold")
ax.set_axis_off()
ax.legend(loc="upper right", frameon=True, fontsize=10)

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/mapa_pontos_sp.png", dpi=200, bbox_inches="tight")
print("Mapa salvo em /mnt/user-data/outputs/mapa_pontos_sp.png")
