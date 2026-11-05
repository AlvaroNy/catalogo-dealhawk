# Clearance Walmart — Houston (catálogo DealHawk)

Página estática para consultar, pelo celular, as ofertas de clearance do Walmart (10 lojas da região de Houston, TX) coletadas do DealHawk.
Dados coletados em **05/11/2026** — **3.613 itens**, 3.613 UPCs únicos.

> Uso pessoal. Projeto independente, sem vínculo com Walmart ou DealHawk. Preços, estoque e corredores mudam rápido: confirme na loja.

## O que a página faz

- **Busca por nome** (várias palavras, sem acento).
- **Código de barras (UPC)**: digite ou toque em **📷 Ler** (câmera; só aparece em navegadores com `BarcodeDetector`, como o Chrome no Android). Zeros à esquerda são ignorados (`0036023907` = `36023907`).
- **Desconto**: chips Todos / 25%+ / 50%+ / 70%+ / 80%+.
- **CEP (ZIP) / loja**: digite o ZIP (ou só o começo, ex. `770`) ou toque nos chips das lojas (com contagem de itens).
- **Preço máximo**, **etiquetas** (Novo, Menor preço, Preço caiu, Estoque caindo) e **ordenação** (desconto, economia em $, menor/maior preço, estoque, nome).
- Cada card mostra preço, preço regular, % off, estoque, corredor, loja + ZIP, UPC (toque para copiar) e "atualizado há…" (relativo ao momento da coleta).

## Como foi feito (passo a passo)

### 1. Origem dos dados
Os dados vêm da aba **All** de `https://dealhawkpro.io/walmart/products`, vista com a conta do próprio usuário (plano atual). Só foi usado o que o plano já mostra: **nenhum plano foi assinado ou alterado** e nada pago/bloqueado ("Unlock deals", lojas extras) foi acessado.

1. O usuário fez login no navegador embutido do app Claude.
2. Um script JavaScript rolou a lista (que carrega mais itens ao rolar, ~560 px a cada 400 ms) e, a cada passo, leu o texto dos cards visíveis, deduplicando por conteúdo. Terminou em exatamente 3.613 itens, igual ao total exibido pelo site.
3. Cada card foi interpretado por regras (preços `$`, `Save $`, `% off`, `N in stock`, UPC numérico, corredor, selos `NEW/LOWEST/PRICE ↓↑/STOCK ↑↓`, `+N more`, `Updated`) e exportado para CSV (`data/dealhawk_walmart_all_deals.csv`).
4. A coleta foi feita pela interface do site; não foram usadas chamadas diretas à API.

Colunas do CSV: `name, store, price, regular, save, pct, stock, aisle, upc, pickup, options, badges, more, updated`.

### 2. ZIP das lojas
O site mostra só endereço e nº da loja. Os ZIPs foram obtidos com o geocodificador público do U.S. Census (endereço → ZIP):

| Loja | Endereço | ZIP |
|---|---|---|
| #2257 | 13484 Northwest Fwy, Houston | 77040 |
| #2718 | 9555 S Post Oak Rd, Houston | 77096 |
| #3425 | 9598 Rowlett Rd, Houston | 77075 |
| #3584 | 5405 S Rice Ave, Houston | 77081 |
| #4416 | 13003 Tomball Pkwy (TX-249), Houston | 77086 |
| #2724 | 1107 Shaver St, Pasadena | 77506 |
| #752 | 5200 Fairmont Pkwy, Pasadena | 77505 |
| #872 | 1919 N Main St, Houston | 77009 |
| #2066 | 2727 Dunvale Rd, Houston | 77063 |
| #3640 | 1118 Silber Rd, Houston | 77055 |

Observações: #4416 só geocodifica como "13003 State Hwy 249" (mesmo endereço); #872 e #752 foram escolhidos por coerência com a distância entre lojas informada pelo DealHawk (todas a ≤ 5,2 mi umas das outras) — conferir se necessário.

### 3. Geração da página
`build.py` (apenas biblioteca padrão do Python) lê o CSV, converte os itens em arrays compactos (`[nome, loja, preço, regular, %, estoque, corredor, upc, selos, opções, atualizado]`), embute tudo em um único `index.html` autossuficiente (HTML + CSS + JS, sem dependências, ~465 KB) e grava o arquivo. "Check stock" vira estoque `-1` ("confirmar").

```bash
py build.py        # regenera index.html a partir de data/dealhawk_walmart_all_deals.csv
```

**Nunca edite o `index.html` à mão** — altere `build.py` (template e lojas) ou o CSV e regere.

### 4. Testes feitos
Em viewport mobile (375×812) no navegador embutido: total 3.613; ZIP `77075` → 656 itens; ZIP `770` → 3.238; UPC `36023907` (com e sem zeros à esquerda) → 2 itens; busca "breast pump" → 8; filtro 50%+ e preço até $5 funcionando.

### 5. Publicação
Site estático servido pelo GitHub Pages (branch `main`, raiz). `index.html` tem `noindex` para não aparecer em buscadores.

## Como atualizar os dados
1. Logar no DealHawk e repetir a coleta da aba **All** (passos acima), exportando o CSV com as mesmas colunas.
2. Substituir `data/dealhawk_walmart_all_deals.csv`, ajustar `EXTRACTED_ON` em `build.py`, rodar `py build.py`, commit e push.

## Limitações
- Dados de um único instante; "atualizado há" é relativo à coleta.
- Cobre só as 10 lojas visíveis no plano; sem outras regiões.
- Os termos de uso do DealHawk podem restringir a redistribuição dos dados; manter para uso pessoal.
