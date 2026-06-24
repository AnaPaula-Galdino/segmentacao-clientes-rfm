import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from relatorio_exec import construir
import segmentacao_rfm as S

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens")
def img(n): return os.path.join(IMG, n)
r = S.resumo()

config = {
 "eyebrow": "RELATÓRIO DE SEGMENTAÇÃO DE CLIENTES",
 "titulo": "Segmentação de Clientes (RFM)",
 "subtitulo": "Agrupamento de clientes por Recência, Frequência e Valor com K-Means",
 "meta": "Ana Paula Galdino · Data Analytics (POSTECH/FIAP) · Junho de 2026",
 "fonte": "Base de transações de clientes  ·  Análise: Ana Paula Galdino",
 "sumario": [
   f"Nem todo cliente vale o mesmo, e tratá-los igual desperdiça recurso. A partir de "
   f"<b>{r['n_clientes']:,}</b> clientes, calculei o RFM (Recência, Frequência e Valor) e usei K-Means "
   f"para agrupá-los em <b>{r['k']} segmentos</b> claros e acionáveis.".replace(",", "."),
   f"O resultado confirma a regra do negócio: os <b>Campeões</b> são só <b>{r['camp_pct']:.0f}%</b> da "
   f"base, mas respondem por <b>{r['camp_receita']:.0f}%</b> da receita. No outro extremo, "
   f"<b>{r['risco_pct']:.0f}%</b> dos clientes estão em risco ou já inativos — um alerta de retenção.",
 ],
 "kpis": [
   (f"{r['n_clientes']:,}".replace(",", "."), "clientes segmentados"),
   (str(r['k']), "segmentos (K-Means)"),
   (f"{r['camp_receita']:.0f}%", "da receita nos Campeões"),
   (f"{r['risco_pct']:.0f}%", "em risco ou inativos"),
 ],
 "secoes": [
   {"titulo": "1. Construindo o RFM",
    "texto": [
      "RFM resume cada cliente em três números: há quanto tempo comprou (Recência), quantas vezes "
      "(Frequência) e quanto gastou (Valor). É simples, interpretável e poderoso.",
      f"A escolha de <b>{r['k']} segmentos</b> foi guiada pelo método do cotovelo e pela silhueta "
      f"(score de {r['silhueta']:.2f}), equilibrando separação dos grupos e facilidade de ação.",
    ],
    "imagens": [(img("01_distribuicao_rfm.png"), "Distribuição de recência, frequência e valor"),
                (img("02_escolha_k.png"), "Cotovelo e silhueta para definir o número de segmentos")]},
   {"titulo": "2. Os segmentos encontrados",
    "texto": [
      "O modelo separou os clientes em quatro grupos com perfis bem distintos: <b>Campeões</b> "
      "(compram muito, recente e com alto valor), <b>Leais</b>, <b>Em risco</b> e <b>Inativos</b> "
      "(não compram há muito tempo).",
      "A leitura por recência e valor mostra visualmente a distância entre os grupos — e onde mora o "
      "valor da carteira.",
    ],
    "imagens": [(img("04_heatmap_segmentos.png"), "Perfil RFM médio de cada segmento"),
                (img("03_clusters_scatter.png"), "Separação dos segmentos por recência e valor")]},
   {"titulo": "3. Tamanho × valor de cada grupo",
    "texto": [
      f"Aqui está o insight que vira estratégia: poucos <b>Campeões</b> ({r['camp_pct']:.0f}% da base) "
      f"sustentam {r['camp_receita']:.0f}% da receita. Protegê-los é prioridade.",
      f"E <b>{r['risco_clientes']}</b> clientes (em risco + inativos) representam a maior oportunidade — e "
      "o maior risco — de retenção. Cada segmento pede uma ação diferente.",
    ],
    "imagens": [(img("05_tamanho_segmentos.png"), "Número de clientes por segmento"),
                (img("06_receita_por_segmento.png"), "Receita concentrada por segmento")]},
 ],
 "conclusao_titulo": "Ações por segmento",
 "conclusoes": [
   "<b>Campeões:</b> programa de relacionamento e benefícios exclusivos — são a base da receita.",
   "<b>Leais:</b> incentivos de recompra e cross-sell para subir o ticket.",
   "<b>Em risco:</b> campanhas de reativação antes que virem inativos.",
   "<b>Inativos:</b> ofertas de retorno pontuais, sem gastar muito — o retorno tende a ser baixo.",
 ],
}

if __name__ == "__main__":
    construir(config, os.path.join(BASE, "Analise_Executiva_Segmentacao.pdf"))
