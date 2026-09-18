# Guia de anotação NER

## Objetivo

Padronizar a anotação de entidades nos títulos da base `audio_and_video`, garantindo consistência entre os integrantes e dados adequados para treinamento e avaliação.

## Entidades

| TAG | O que anotar | Exemplos |
|---|---|---|
| `PRODUTO` | Tipo explícito do produto, usando a expressão completa. | `Caixa de Som`, `Fone de Ouvido`, `Headphone`, `Projetor Multimídia`, `Soundbar` |
| `MARCA` | Marca escrita no título. Não inferir pela descrição. | `JBL`, `Apple`, `Pulse`, `Goldentec` |
| `CONECTIVIDADE` | Tecnologia, padrão ou interface de conexão. Incluir versão ou variação. | `Bluetooth 5.3`, `Wi-Fi`, `USB-C`, `HDMI ARC`, `TWS` |
| `COR` | Cor explícita, incluindo qualificadores. | `Preta`, `Branco`, `Azul Marinho` |
| `POTENCIA` | Valor e unidade de potência. Incluir multiplicador e `RMS`, quando presentes. | `80W RMS`, `30 W`, `2x40W RMS` |

## Regras gerais

1. Anotar somente informações presentes no título.
2. Selecionar exatamente o trecho da entidade, sem espaços ou pontuação nas extremidades.
3. Anotar a expressão completa: `Bluetooth 5.3`, não apenas `Bluetooth`.
4. Anotar todas as ocorrências válidas, sem criar entidades sobrepostas.
5. Não corrigir nem alterar o texto original.
6. Termos genéricos como `sem fio` não serão anotados como `CONECTIVIDADE`.
7. Em caso de dúvida, deixar sem anotação e encaminhar para revisão do grupo.

## Exemplo

Texto:

```text
Caixa de Som JBL Boombox 3 Bluetooth Preta
```

Anotação:

```json
{
  "text": "Caixa de Som JBL Boombox 3 Bluetooth Preta",
  "entities": [
    [0, 12, "PRODUTO"],
    [13, 16, "MARCA"],
    [27, 36, "CONECTIVIDADE"],
    [37, 42, "COR"]
  ]
}
```

O índice inicial é incluído e o índice final não é incluído.

## Decisões do grupo

- `MODELO` não será utilizado.
- `SKU` não será utilizado.
- Nomes de modelos e códigos de referência permanecerão sem anotação.
