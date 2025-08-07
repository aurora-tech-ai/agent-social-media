# 🎨 Social Media AI Generator

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-2.0+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/AI-DeepSeek%20Reasoner-purple.svg" alt="AI Model">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 Gere posts incríveis para redes sociais usando IA</h3>
  <p>Uma aplicação Flask que transforma suas ideias em posts visuais profissionais para Instagram, LinkedIn e Twitter usando inteligência artificial.</p>
</div>

---

## ✨ Funcionalidades

### 🎯 **Geração Inteligente**
- **IA Avançada**: Powered by DeepSeek Reasoner para criação de conteúdo
- **Enhancement de Prompts**: Melhora automaticamente suas ideias básicas
- **Templates Responsivos**: Designs otimizados para cada plataforma

### 🖼️ **Múltiplos Formatos**
- 📸 **Imagens**: PNG, JPG, JPEG
- 🎬 **GIF Animado**: Com múltiplos frames
- 🎥 **MP4 Video**: Para stories e reels
- 📱 **Dimensões Otimizadas**: Cada formato no tamanho ideal

### 🌐 **Plataformas Suportadas**
- **Instagram**: 1080x1080px - Visual impactante
- **LinkedIn**: 1200x630px - Profissional e corporativo  
- **Twitter**: 1200x675px - Conciso e viral

### ⚡ **Tecnologias de Ponta**
- **Dupla Conversão**: Playwright + Selenium (fallback automático)
- **Animações CSS**: Efeitos visuais dinâmicos
- **Tailwind CSS**: Design system moderno
- **Font Awesome**: Iconografia profissional

---

## 🚀 Quick Start

### 1️⃣ **Pré-requisitos**
```bash
# Python 3.8+
# Chrome/Chromium browser
# Git
```

### 2️⃣ **Instalação**
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/social-media-ai-generator.git
cd social-media-ai-generator

# Instale as dependências
pip install -r requirements.txt

# Instale o Playwright (opcional, mas recomendado)
playwright install chromium
```

### 3️⃣ **Configuração**
```bash
# Crie o arquivo .env
cp .env.example .env

# Configure suas chaves de API
DEEPSEEK_API_KEY=sua_chave_deepseek_aqui
SECRET_KEY=sua_chave_secreta_flask
```

### 4️⃣ **Execute**
```bash
python app.py
```

Acesse: `http://localhost:5010` 🎉

---

## 🛠️ Instalação Detalhada

### **Dependências Python**
```bash
pip install flask openai python-dotenv selenium pillow
```

### **Playwright (Recomendado)**
```bash
# Instalar Playwright
pip install playwright

# Baixar browsers
playwright install chromium
```

### **Chrome Driver (Selenium)**
O Chrome driver será gerenciado automaticamente pelo Selenium.

---

## 📖 Como Usar

### **1. Interface Web**
1. Acesse `http://localhost:5010`
2. Digite sua ideia de post
3. Escolha a plataforma (Instagram/LinkedIn/Twitter)
4. Clique em "Gerar Post"
5. Faça download no formato desejado

### **2. API Endpoints**

#### **Gerar Post**
```bash
POST /generate
Content-Type: application/json

{
  "prompt": "Dicas de produtividade para desenvolvedores",
  "platform": "instagram"
}
```

#### **Melhorar Prompt**
```bash
POST /enhance-prompt
Content-Type: application/json

{
  "prompt": "produtividade",
  "platform": "linkedin"
}
```

#### **Download**
```bash
POST /download
Content-Type: application/json

{
  "format": "png",
  "html": "<html>...</html>",
  "content_id": "uuid-here",
  "duration": 5
}
```

---

## ⚙️ Configuração Avançada

### **Variáveis de Ambiente**
```bash
# .env
DEEPSEEK_API_KEY=sk-xxx          # Obrigatório
SECRET_KEY=random-secret-key     # Obrigatório
FLASK_ENV=production             # Opcional
FLASK_PORT=5010                  # Opcional
```

### **Customização de Templates**
```python
# Edite os templates em SocialMediaAgent
def get_instagram_template(self):
    # Customize seu template HTML aqui
    return """..."""
```

### **Configuração do Selenium**
```python
# Ajuste as opções do Chrome
self.selenium_options.add_argument('--window-size=1920,1080')
self.selenium_options.add_argument('--disable-web-security')
```

---

## 🎨 Exemplos de Uso

### **Marketing Digital**
```python
prompt = "Estratégias de growth hacking para startups, visual moderno com gráficos e ícones, cores corporativas azul e branco"
platform = "linkedin"
```

### **Lifestyle Instagram**
```python
prompt = "Rotina matinal produtiva, aesthetic minimalista, cores pastel, elementos de bem-estar"
platform = "instagram"
```

### **Tweet Viral**
```python
prompt = "Thread sobre inteligência artificial, design tech, elementos futuristas"
platform = "twitter"
```

---

## 🔧 Troubleshooting

### **Problema: Playwright não funciona**
```bash
# Solução: Usar apenas Selenium
# O sistema automaticamente usa Selenium como fallback
```

### **Problema: Chrome não encontrado**
```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# macOS
brew install chromium

# Windows
# Baixe Chrome do site oficial
```

### **Problema: Erro de conversão**
```bash
# Teste a conversão
curl http://localhost:5010/test-conversion
```

---

## 🏗️ Arquitetura

```
social-media-ai-generator/
├── 📄 app.py                 # Aplicação Flask principal
├── 🤖 SocialMediaAgent       # Classe principal do gerador
├── 🎨 templates/             # Templates HTML
├── 🔧 static/               # Assets estáticos
├── 📋 requirements.txt      # Dependências Python
├── ⚙️ .env                  # Configurações
└── 📖 README.md            # Este arquivo
```

### **Fluxo de Funcionamento**
1. **Input**: Usuário fornece prompt + plataforma
2. **IA**: DeepSeek processa e gera HTML + CSS
3. **Render**: Playwright/Selenium converte para imagem
4. **Output**: Download em múltiplos formatos

---

## 🤝 Contribuição

Contribuições são muito bem-vindas! 

### **Como Contribuir**
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add: nova feature incrível'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### **Guidelines**
- ✅ Teste todas as funcionalidades
- ✅ Mantenha o código documentado
- ✅ Siga as convenções Python (PEP 8)
- ✅ Adicione exemplos para novas features

---

## 📊 Roadmap

- [ ] 🎯 **v2.0**: Suporte para TikTok e YouTube Shorts
- [ ] 🎨 **v2.1**: Editor visual de templates
- [ ] 🤖 **v2.2**: Múltiplos modelos de IA
- [ ] ☁️ **v2.3**: Deploy automático na nuvem
- [ ] 📱 **v2.4**: App mobile React Native
- [ ] 🔄 **v2.5**: Agendamento de posts
- [ ] 📊 **v2.6**: Analytics e métricas

---

## 📜 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **DeepSeek AI** - Pela incrível API de IA
- **Playwright Team** - Pela ferramenta de automação web
- **Selenium Contributors** - Pelo sistema de fallback robusto
- **Tailwind CSS** - Pelo framework de design
- **Flask Community** - Pelo micro-framework Python

---

<div align="center">
  <h3>⭐ Gostou do projeto? Deixe uma estrela!</h3>
  <p>Feito com ❤️ e muito ☕ por <a href="https://github.com/seu-usuario">aurora-tech-ai</a></p>
  
  <p>
    <a href="https://github.com/seu-usuario/social-media-ai-generator/issues">🐛 Reportar Bug</a> •
    <a href="https://github.com/seu-usuario/social-media-ai-generator/discussions">💡 Sugerir Feature</a> •
    <a href="https://twitter.com/seu-usuario">🐦 Twitter</a>
  </p>
</div>
