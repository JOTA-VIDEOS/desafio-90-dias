# 🔥 Desafio 90 Dias

App para monitorar o desafio de postar 1 vídeo/dia no Instagram por 90 dias.  
Funciona no **Windows, Mac e celular** — como app instalado ou pelo navegador.

---

## ⚡ Como funciona

| O que                        | Como                                                     |
|------------------------------|----------------------------------------------------------|
| **Plataforma**               | Web app (PWA) — instala como app nativo em qualquer OS   |
| **Coleta diária**            | GitHub Actions, 23h50 Brasília, 100% automático          |
| **Dados**                    | API oficial do Instagram (sem scraping, sem bloqueio)     |
| **Custo**                    | Zero (GitHub Pages + Actions, tudo gratuito)             |
| **Métricas**                 | Views, alcance, curtidas, comentários, compartilhamentos, salvamentos |

---

## 🚀 Setup (uma vez só, ~15 min para os 3)

### 1. Subir o repositório

```bash
git init
git add .
git commit -m "desafio 90 dias"
git remote add origin https://github.com/SEU-USUARIO/desafio-90-dias.git
git push -u origin main
```

### 2. Ativar GitHub Pages

Repositório → **Settings → Pages → Branch: main → / (root) → Save**  
O app vai ficar em: `https://SEU-USUARIO.github.io/desafio-90-dias/`

### 3. Conectar o Instagram (cada participante faz 1 vez)

As 3 contas precisam ser **Criador de Conteúdo** ou **Comercial** (troca grátis nas config do Instagram).

1. Entre em [developers.facebook.com](https://developers.facebook.com)
2. **My Apps → Create App → Business**
3. Adicione o produto **Instagram API with Instagram Login**
4. Em **Instagram API → Generate Token**, conecte sua conta
5. Copie o token gerado

### 4. Colocar os tokens no GitHub

Repositório → **Settings → Secrets → Actions → New repository secret**:

| Secret           | Valor            |
|------------------|------------------|
| `TOKEN_JOTA`     | Token do Jota    |
| `TOKEN_ISAIAS`   | Token do Isaías  |
| `TOKEN_GABRIEL`  | Token do Gabriel |

**Opcional:** crie `GH_PAT` (Personal Access Token com permissão `repo`) para renovar tokens automaticamente todo domingo.

### 5. Editar config.json

Coloque a data real de início no campo `"inicio"`.

### 6. Primeira coleta

**Actions → Coleta diária → Run workflow** para testar.

---

## 📱 Instalar como app

O site é uma PWA — funciona como app nativo:

| Plataforma     | Como instalar                                                       |
|----------------|---------------------------------------------------------------------|
| **Windows**    | Abre no Edge ou Chrome → ícone de instalar na barra de endereço     |
| **Mac**        | Abre no Chrome → Menu (⋮) → "Instalar Desafio 90 Dias"            |
| **iPhone**     | Abre no Safari → Compartilhar (↑) → "Adicionar à Tela de Início"   |
| **Android**    | Abre no Chrome → banner automático ou Menu → "Instalar app"         |

Depois de instalar, abre como qualquer app do sistema — com ícone, sem barra do navegador.

---

## 🤖 Como funciona no dia a dia

Ninguém precisa fazer nada. Todo dia às 23h50:

1. GitHub Actions acorda
2. Roda `coletar.py` que lê as 3 contas via API
3. Atualiza `dados.js` e faz commit
4. GitHub Pages republica o site
5. Todo mundo vê o ranking atualizado

Tokens são renovados automaticamente aos domingos (se tiver o `GH_PAT`).

---

## 📂 Arquivos

```
index.html          → App (PWA)
manifest.json       → Configuração do app instalável
sw.js               → Service worker (funciona offline)
icon-192.svg        → Ícone do app
icon-512.svg        → Ícone grande
config.json         → Participantes e data de início
coletar.py          → Robô de coleta (Python, roda no GitHub Actions)
dados.js            → Dados atualizados (gerado automaticamente)
.github/workflows/  → Rotina diária
```
