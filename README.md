# mt-lab-session-ner-starter

## Grupo
1. NOME INTEGRANTE - EMAIL
2. NOME INTEGRANTE - EMAIL
3. NOME INTEGRANTE - EMAIL

> Preencher os nomes e e-mails dos integrantes antes da submissão.

## Solução desenvolvida

- **Base escolhida:** `data/raw/audio_and_video.ibyte.json`.
- **Entidades:** `PRODUTO`, `MARCA`, `CONECTIVIDADE`, `COR` e `POTENCIA`.
- **Base final:** 300 títulos e 1.042 entidades em
  [`data/annotations/audio_and_video_annotated_300.jsonl`](data/annotations/audio_and_video_annotated_300.jsonl).
- **Teste final:** 100 títulos revisados manualmente no Doccano.
- **Desenvolvimento:** 200 títulos anotados com assistência de IA, seguindo o
  [guia de anotação](docs/guia_anotacao_ner.md).
- **Abordagens comparadas:** regras, CRF e spaCy NER leve.

O treinamento, a seleção de configurações e a avaliação estão organizados no
notebook [`notebooks/01_treinamento_avaliacao_ner.ipynb`](notebooks/01_treinamento_avaliacao_ner.ipynb),
com as saídas da execução preservadas.

### Resultado final

| Abordagem | Precisão | Recall | F1 micro |
|---|---:|---:|---:|
| CRF | 0,981 | 0,933 | **0,956** |
| spaCy NER | 0,941 | 0,918 | 0,929 |
| Regras | 0,983 | 0,686 | 0,808 |

O **CRF** foi selecionado por apresentar o melhor F1 e desempenho consistente entre
as cinco entidades. Os resultados completos estão em
[`results/ner_models/`](results/ner_models/), incluindo comparação dos modelos,
métricas por TAG e matrizes de confusão.

### Fluxo do projeto

1. `prepare_audio_and_video.py`: limpeza da base escolhida;
2. `prepare_doccano.py` e `preannotate_ner.py`: preparação e pré-anotação;
3. `create_annotation_pilot.py`: seleção do piloto revisado no Doccano;
4. `create_annotation_additional.py` e `annotate_additional_ai_review.py`: criação e
   anotação assistida dos 200 títulos adicionais;
5. `combine_reviewed_annotations.py`: formação da base final de 300 títulos;
6. `01_treinamento_avaliacao_ner.ipynb`: treinamento e comparação das abordagens.

As versões usadas na execução estão registradas em
[`results/ner_models/metadados_execucao.json`](results/ner_models/metadados_execucao.json).

## Prerequisites:
* Docker
* Python

## Overview
1. Considere o cenário de uma plataforma de e-commerce, no fluxo de cadastrar novos produtos.
2. Seu objetivo é construir um sistema para auxiliar a extração de informações de um produto, a partir do título dele. Assim, as informações de catálogo/cadastro do produto podem ser preenchidas automaticamente.
3. Por exemplo, quando o usuário digitar "iphone 14 128gb vermelho", o sistema já deve identificar e sugerir automaticamente a categoria (SMARTPHONES), o modelo (IPHONE 14), a memória (128GB) e a cor (VERMELHO).

## Descrição da atividade
1. Cada grupo deve escolher uma base de dados na pasta `data/raw/` e escolher uma base de dados (diferente de `beauty.ibyte.jsonl` e `toys_and_babies.ibyte`)
2. O grupo deve realizar o processo de definição das TAGs (entidades nomeadas), anotação, treinamento e seleção da melhor abordagem de NER para resolver esse problema (ver seção [Running Doccano](#running-doccano)). O grupo pode usar outras alternativas para anotação das entidades (datasets externos, zero-shot learning, etc).
4. As anotações devem ser salvas na pasta `data/annotations/nome_do_dataset.jsonl`, no mesmo formato dos arquivos de exemplo `beauty.ibyte.jsonl` e `toys_and_babies.ibyte`, e.g.:
```
{"text": "Pelucia Bonnie Bear 30Cm Azul Multikids   BR166", "entities": [[0, 7, "TIPO"], [8, 19, "PRODUTO"], [30, 39, "MARCA"]]}
```
5. Os notebooks para treinamento e avaliação devem estar salvos de forma ORGANIZADA na pasta `notebooks`
6. No dia agendado para a apresentação, o grupo deve mostrar em sala como foi o processo de solução do problema, e os resultados obtidos (no máximo 5 - 10 min por grupo).

## Avaliação:
Os critérios para a avaliação serão:
- Anotações das entidades no formato adequado
- Organização e metodologia experimental
- Apresentação dos resultados

# Running Doccano
## Run as docker container
```
chmod +x scripts/start-doccano.sh
./scripts/0.setup-doccano.sh
./scripts/1.start-doccano.sh
```

## Import annotations
1. Access doccano at the URL localhost:8000
2. Login 
3. Go to "Dataset" --> "Actions" --> Import Dataset
4. Change the File Format to JSONL
5. Set column label to be "entities"

![Doccano Setup](imgs/doccano-import-dataset.png)

6. See the annotations at "Start Annotation"
