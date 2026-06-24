"""
Segmentação de Clientes com RFM + K-Means
Calcula Recência, Frequência e Valor (RFM), agrupa os clientes e nomeia os segmentos.
Autora: Ana Paula Galdino
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens"); os.makedirs(IMG, exist_ok=True)
HOJE = pd.Timestamp("2026-06-23")
C = {"escuro":"#1f4e79","medio":"#2e6da4","claro":"#5b9bd5","suave":"#a6c8e0",
     "destaque":"#4fc3f7","cinza":"#d9d9d9","alerta":"#c0392b"}
SEGCOR = {"Campeões":"#1f4e79","Leais":"#2e6da4","Em risco":"#5b9bd5","Inativos":"#a6c8e0"}
FONTE = "Base de transações de clientes  ·  Análise: Ana Paula Galdino"
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.edgecolor":"#9aa7b8",
    "axes.grid":True,"grid.color":"#eef2f7","axes.axisbelow":True,"figure.dpi":120,"savefig.bbox":"tight"})
def rodape(fig): fig.text(0.01,0.005,FONTE,fontsize=7.5,color="#7a8aa0")

# ---- RFM ----
tx = pd.read_csv(os.path.join(BASE,"dados","transacoes.csv"), parse_dates=["data_compra"])
rfm = tx.groupby("cliente_id").agg(
    recencia=("data_compra", lambda d: (HOJE - d.max()).days),
    frequencia=("data_compra", "count"),
    valor=("valor", "sum")).reset_index()

X = StandardScaler().fit_transform(rfm[["recencia","frequencia","valor"]])

# ---- escolha de k ----
ks = range(2, 9); inercias=[]; sils=[]
for k in ks:
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
    inercias.append(km.inertia_); sils.append(silhouette_score(X, km.labels_))
K = 4
km = KMeans(n_clusters=K, random_state=42, n_init=10).fit(X)
rfm["cluster"] = km.labels_

# ---- nomear segmentos por valor (composto RFM) ----
perfil = rfm.groupby("cluster").agg(r=("recencia","mean"), f=("frequencia","mean"),
                                    m=("valor","mean"), n=("cliente_id","count"))
z = (perfil[["r","f","m"]] - perfil[["r","f","m"]].mean()) / perfil[["r","f","m"]].std()
perfil["score"] = -z["r"] + z["f"] + z["m"]
ordem = perfil["score"].sort_values(ascending=False).index.tolist()
nomes = ["Campeões","Leais","Em risco","Inativos"]
mapa = {cl: nomes[i] for i, cl in enumerate(ordem)}
rfm["segmento"] = rfm["cluster"].map(mapa)

# 1) Distribuição RFM
def g1():
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,(col,tit,cor) in zip(axes,[("recencia","Recência (dias)",C["escuro"]),
            ("frequencia","Frequência (compras)",C["medio"]),("valor","Valor total (R$)",C["claro"])]):
        ax.hist(rfm[col], bins=30, color=cor, edgecolor="white")
        ax.set_title(tit, fontsize=11, color=C["escuro"], fontweight="bold"); ax.set_ylabel("Clientes")
    fig.suptitle("Distribuição das métricas RFM", fontweight="bold", color=C["escuro"], fontsize=14)
    rodape(fig); fig.tight_layout(); fig.savefig(os.path.join(IMG,"01_distribuicao_rfm.png")); plt.close(fig)

# 2) Escolha de k
def g2():
    fig,ax=plt.subplots(figsize=(9,5))
    ax.plot(list(ks), inercias, color=C["escuro"], marker="o", lw=2, label="Inércia (cotovelo)")
    ax.set_xlabel("Número de clusters (k)"); ax.set_ylabel("Inércia", color=C["escuro"])
    ax.axvline(K, color=C["alerta"], ls="--", lw=1.2, label=f"k escolhido = {K}")
    ax2=ax.twinx(); ax2.plot(list(ks), sils, color=C["destaque"], marker="s", lw=2, label="Silhueta")
    ax2.set_ylabel("Silhueta", color=C["destaque"]); ax2.grid(False)
    ax.set_title("Escolha do número de segmentos", fontweight="bold", color=C["escuro"], fontsize=13, pad=10)
    l1,la1=ax.get_legend_handles_labels(); l2,la2=ax2.get_legend_handles_labels()
    ax.legend(l1+l2, la1+la2, loc="center right", frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"02_escolha_k.png")); plt.close(fig)

# 3) Scatter dos clusters
def g3():
    fig,ax=plt.subplots(figsize=(9.5,6))
    for seg,cor in SEGCOR.items():
        s=rfm[rfm["segmento"]==seg]
        ax.scatter(s["recencia"], s["valor"], s=18, color=cor, alpha=0.6, label=seg, edgecolor="none")
    ax.set_yscale("log"); ax.set_xlabel("Recência (dias desde a última compra)")
    ax.set_ylabel("Valor total gasto (R$, log)")
    ax.set_title("Segmentos de clientes — recência × valor", fontweight="bold", color=C["escuro"], fontsize=13, pad=10)
    ax.legend(title="Segmento", frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"03_clusters_scatter.png")); plt.close(fig)

# 4) Heatmap RFM por segmento
def g4():
    tab = rfm.groupby("segmento")[["recencia","frequencia","valor"]].mean().reindex(nomes)
    norm = (tab - tab.min()) / (tab.max() - tab.min())
    fig,ax=plt.subplots(figsize=(8,4.6))
    im=ax.imshow(norm.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(3)); ax.set_xticklabels(["Recência","Frequência","Valor"])
    ax.set_yticks(range(len(nomes))); ax.set_yticklabels(nomes)
    for i in range(len(nomes)):
        for j,col in enumerate(["recencia","frequencia","valor"]):
            v=tab.iloc[i][col]
            txt=f"{v:.0f}" if col!="valor" else f"R${v/1000:.1f}k"
            ax.text(j,i,txt,ha="center",va="center",color="white" if norm.values[i,j]>0.5 else "#1f4e79",fontsize=10)
    ax.set_title("Perfil médio de cada segmento (RFM)", fontweight="bold", color=C["escuro"], fontsize=13, pad=10)
    ax.grid(False)
    rodape(fig); fig.savefig(os.path.join(IMG,"04_heatmap_segmentos.png")); plt.close(fig)

# 5) Tamanho dos segmentos
def g5():
    cont = rfm["segmento"].value_counts().reindex(nomes)
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(cont.index, cont.values, color=[SEGCOR[s] for s in cont.index])
    for i,v in enumerate(cont.values): ax.text(i,v,f"{v}\n({v/len(rfm)*100:.0f}%)",ha="center",va="bottom",fontsize=10)
    ax.set_title("Quantos clientes em cada segmento", fontweight="bold", color=C["escuro"], fontsize=13, pad=10)
    ax.set_ylabel("Clientes"); ax.set_ylim(0, cont.max()*1.18)
    rodape(fig); fig.savefig(os.path.join(IMG,"05_tamanho_segmentos.png")); plt.close(fig)

# 6) Receita por segmento
def g6():
    rec = rfm.groupby("segmento")["valor"].sum().reindex(nomes)
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(rec.index, rec.values, color=[SEGCOR[s] for s in rec.index])
    tot=rec.sum()
    for i,v in enumerate(rec.values): ax.text(i,v,f"R${v/1000:.0f}k\n({v/tot*100:.0f}%)",ha="center",va="bottom",fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f"R${x/1000:.0f}k"))
    ax.set_title("Onde está a receita (por segmento)", fontweight="bold", color=C["escuro"], fontsize=13, pad=10)
    ax.set_ylabel("Receita total"); ax.set_ylim(0, rec.max()*1.18)
    rodape(fig); fig.savefig(os.path.join(IMG,"06_receita_por_segmento.png")); plt.close(fig)

def resumo():
    rec = rfm.groupby("segmento")["valor"].sum()
    cont = rfm["segmento"].value_counts()
    camp_rec = rec.get("Campeões",0)/rec.sum()*100
    camp_pct = cont.get("Campeões",0)/len(rfm)*100
    risco = cont.get("Em risco",0)+cont.get("Inativos",0)
    return {"n_clientes":len(rfm),"k":K,"silhueta":max(sils),
            "camp_pct":camp_pct,"camp_receita":camp_rec,
            "risco_clientes":int(risco),"risco_pct":risco/len(rfm)*100}

def main():
    for g in (g1,g2,g3,g4,g5,g6): g()
    print({k:(round(v,2) if isinstance(v,float) else v) for k,v in resumo().items()})
    print("Gráficos:", sorted(x for x in os.listdir(IMG) if x.startswith("0")))

if __name__=="__main__":
    main()
