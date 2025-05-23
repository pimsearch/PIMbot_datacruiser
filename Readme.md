# 🧩 DataCruiser — Cruzamento inteligente de planilhas

O **DataCruiser** é uma aplicação web leve construída em Python/Flask que simula um PROCV do Excel, mas com superpoderes:  
ela cruza duas planilhas e retorna **todos os resultados relacionados**, organizados automaticamente em colunas adicionais.

> 🚀 Ideal para quem precisa cruzar grandes volumes de dados sem fórmulas complicadas ou conhecimento avançado de Excel.

---

## ✅ Funcionalidades principais

- 🔍 Cruzamento de dados entre duas planilhas (simula PROCV)
- 🔁 Suporte a múltiplos resultados por chave (valores distribuídos em colunas)
- 🧼 Limpeza automática de caracteres inválidos para exportação segura
- 📦 Suporte a arquivos `.xlsx`, `.csv`, `.xls`, `.xlsb`
- ⚡ Exportação em `.xlsx` ou `.csv` de acordo com o volume de dados
- 💻 Interface moderna e responsiva com Bootstrap
- 🧠 Processamento 100% local, sem dependência de banco de dados

---

## 🧰 Tecnologias utilizadas

- Python 3.11+
- Flask
- Pandas
- OpenPyXL / xlrd / pyxlsb
- Gunicorn (produção)
- Bootstrap 5

---

## 🚀 Como executar localmente

1. Clone o projeto:
```bash
git clone https://github.com/renansales/PIMbot_datacruiser.git
cd datacruiser
