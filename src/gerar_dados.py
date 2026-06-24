"""
Gera transações de clientes para a análise RFM. Cada cliente tem um perfil latente
(campeão, leal, em risco, novo...), o que cria segmentos naturais para o K-Means encontrar.
Autora: Ana Paula Galdino
"""
import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(31)
HOJE = date(2026, 6, 23)

# perfil: (peso, freq_media, recencia_max_dias, ticket_medio)
perfis = {
    "campeao":  (0.15, 12, 40,  450),
    "leal":     (0.22, 7,  90,  300),
    "potencial":(0.20, 4,  120, 250),
    "novo":     (0.15, 2,  30,  180),
    "em_risco": (0.18, 5,  300, 280),
    "perdido":  (0.10, 3,  520, 150),
}
nomes, pesos = list(perfis), [perfis[p][0] for p in perfis]
linhas = []
cid = 0
for _ in range(1500):
    cid += 1
    perfil = rng.choice(nomes, p=np.array(pesos)/sum(pesos))
    _, fm, rmax, tm = perfis[perfil]
    freq = max(1, int(rng.poisson(fm)))
    ultima = int(rng.integers(1, rmax + 1))           # dias desde a última compra
    # datas das compras entre 'ultima' e ~2 anos atrás
    span = max(ultima + 1, int(rng.integers(ultima + 1, 760)))
    dias = sorted(rng.integers(ultima, span, freq))
    for d in dias:
        valor = round(float(rng.gamma(3.0, tm / 3)) + 20, 2)
        data = HOJE - timedelta(days=int(d))
        linhas.append([cid, data.isoformat(), valor])

df = pd.DataFrame(linhas, columns=["cliente_id", "data_compra", "valor"])
out = os.path.join(BASE, "dados", "transacoes.csv")
df.to_csv(out, index=False)
print(f"Transações: {len(df)} | Clientes: {df['cliente_id'].nunique()} -> {out}")
