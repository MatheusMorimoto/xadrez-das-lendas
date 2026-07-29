# Xadrez das Lendas ♟️

Jogo de puzzles progressivos de xadrez desenvolvido em Python, com três fases e transições em vídeo inspiradas em lendas brasileiras.

## Requisitos

- Windows 10/11 (também pode rodar em Linux/macOS, mas o build fornecido é para Windows)
- Python 3.10 ou mais recente

## Instalação no Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Para instalar também testes, análise estática e geração do executável:

```powershell
python -m pip install -e ".[dev]"
```

Alternativamente, use `python -m pip install -r requirements.txt` e, para desenvolvimento, `python -m pip install -r requirements-dev.txt`.

## Executar

```powershell
python -m xadrez_das_lendas
```

Ou use `xadrez-das-lendas`. `Esc` volta ao menu; durante um vídeo, `Esc` pula a sequência atual.

## Testes e qualidade

```powershell
python -m pytest
python -m ruff check src tests
python -m compileall -q src tests
```

Os testes de regras não abrem janela. Eles cobrem movimentos, bloqueios, capturas, proteção do rei, xeque, mate, afogamento, fases, assets, objetivos e estados.

## Gerar o executável

```powershell
python -m pip install -r requirements-dev.txt
python -m PyInstaller --clean --noconfirm XadrezDasLendas.spec
```

O resultado será criado em `dist/XadrezDasLendas.exe`. O `.spec` inclui os assets e o ícone.

## Estrutura

```text
assets/                         imagens, ícone e vídeos originais
src/xadrez_das_lendas/
  __init__.py                   metadados do pacote
  __main__.py                   entrada de `python -m`
  asset_catalog.py              catálogo central de imagens das peças
  board.py                      tabuleiro e operações estruturais
  game.py                       aplicação e loop de eventos
  paths.py                      localização centralizada de assets
  phase_models.py               modelos imutáveis de configuração
  phases.py                     dados, posições e objetivos das fases
  piece.py                      modelo independente de interface
  renderer.py                   composição do tabuleiro com Pygame
  rules.py                      movimentos, ataques, xeque e mate
  state.py                      máquina de estados e temporizadores
  ui_actions.py                 ações de interface sem nomes de botões
  ui_components.py              textos, botões e indicadores reutilizáveis
  ui_geometry.py                conversão de cliques em casas do tabuleiro
  ui_screens.py                 menu, introdução e encerramento
  video.py                      reprodução interna com OpenCV
tests/                          testes automatizados
pyproject.toml                  instalação, dependências e ferramentas
XadrezDasLendas.spec            build reproduzível para Windows
```

## Regras suportadas

São implementados os movimentos normais de rei, rainha, torre, bispo, cavalo e peão, incluindo avanço duplo inicial e captura de peão. A validação impede atravessar peças, capturar uma peça da mesma cor, capturar diretamente o rei, deixar o próprio rei em xeque, mover o rei para uma casa atacada e manter os reis adjacentes. O motor diferencia xeque, xeque-mate e afogamento.

Como as posições são puzzles de uma jogada, não fazem parte do escopo atual: roque, en passant, promoção, repetição, regra dos 50 movimentos e material insuficiente.

## Fases

- Fase 1: brancas procuram xeque-mate.
- Fase 2: pretas procuram xeque-mate.
- Fase 3: pretas levam a rainha ao alvo configurado, preservando a condição especial original.

Movimentos legais que não resolvem o puzzle restauram a fase após três segundos.

## Assets e vídeos

Os nomes são sensíveis a maiúsculas e minúsculas: `YARA.mp4`, `cucacaldeirao.mp4`, `cuca.mp4` e `boitata.mp4`. OpenCV reproduz os frames dentro da janela, enquanto o mixer do Pygame toca as trilhas OGG correspondentes em volume total. A interface usa pygame-ce, implementação compatível importada como `pygame`. Se um vídeo ou áudio falhar, o erro é registrado e o jogo avança sem bloquear.
