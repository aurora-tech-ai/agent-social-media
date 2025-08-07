from flask import Flask, render_template, request, jsonify, send_file, session
import os
import tempfile
import asyncio
from datetime import datetime
import base64
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
import json
import uuid
import secrets

# Importar conversores alternativos
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Importar PIL para conversão de imagens
from PIL import Image
import io

# Tentar importar Playwright (opcional)
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright não disponível. Usando Selenium como fallback.")

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Configurar cliente DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Armazenamento temporário para HTML (em produção, use Redis ou similar)
html_storage = {}

class SocialMediaAgent:
    def __init__(self):
        self.templates = {
            "instagram": self.get_instagram_template(),
            "linkedin": self.get_linkedin_template(),
            "twitter": self.get_twitter_template()
        }
        
        # Configurar Selenium como fallback
        self.selenium_options = Options()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--window-size=1080,1080')
        self.selenium_options.add_argument('--hide-scrollbars')
        self.selenium_options.add_argument('--disable-web-security')
    
    def selenium_html_to_image(self, html_content, format='png'):
        """Converte HTML para imagem usando Selenium (método confiável)"""
        driver = None
        temp_html_path = None
        
        try:
            # Criar arquivo HTML temporário
            temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_html.write(html_content)
            temp_html.close()
            temp_html_path = temp_html.name
            
            # Inicializar driver
            driver = webdriver.Chrome(options=self.selenium_options)
            
            # Carregar página
            driver.get(f'file://{temp_html_path}')
            
            # Aguardar carregamento completo
            time.sleep(3)  # Tempo para animações CSS
            
            # Definir tamanho da janela baseado na plataforma
            if "1080px" in html_content and "1080px" in html_content:
                driver.set_window_size(1080, 1080)
            elif "1200px" in html_content and "630px" in html_content:
                driver.set_window_size(1200, 630)
            elif "1200px" in html_content and "675px" in html_content:
                driver.set_window_size(1200, 675)
            else:
                driver.set_window_size(1080, 1080)
            
            # Capturar screenshot
            screenshot_bytes = driver.get_screenshot_as_png()
            
            # Converter para o formato desejado
            img = Image.open(io.BytesIO(screenshot_bytes))
            
            if format.lower() in ['jpg', 'jpeg']:
                # Criar fundo branco para JPEG
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                
                output = io.BytesIO()
                background.save(output, format='JPEG', quality=95, optimize=True)
                return output.getvalue()
                
            elif format.lower() == 'gif':
                # Para GIF, capturar múltiplos frames
                frames = []
                for i in range(10):  # Capturar 10 frames
                    time.sleep(0.3)  # Aguardar entre frames
                    frame_bytes = driver.get_screenshot_as_png()
                    frame_img = Image.open(io.BytesIO(frame_bytes))
                    if frame_img.mode == 'RGBA':
                        # Converter RGBA para RGB para GIF
                        rgb_img = Image.new('RGB', frame_img.size, (255, 255, 255))
                        rgb_img.paste(frame_img, mask=frame_img.split()[-1])
                        frames.append(rgb_img)
                    else:
                        frames.append(frame_img)
                
                # Salvar como GIF animado
                output = io.BytesIO()
                frames[0].save(
                    output,
                    format='GIF',
                    save_all=True,
                    append_images=frames[1:],
                    duration=300,  # 300ms entre frames
                    loop=0,
                    optimize=True
                )
                return output.getvalue()
                
            else:  # PNG
                output = io.BytesIO()
                img.save(output, format='PNG', optimize=True)
                return output.getvalue()
            
        except Exception as e:
            print(f"Erro Selenium: {e}")
            raise Exception(f"Erro ao gerar imagem com Selenium: {str(e)}")
        
        finally:
            # Cleanup
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            
            if temp_html_path and os.path.exists(temp_html_path):
                try:
                    os.unlink(temp_html_path)
                except:
                    pass

    async def playwright_html_to_image(self, html_content, format='png'):
        """Converte HTML para imagem usando Playwright (se disponível)"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright não está disponível")
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                page = await browser.new_page()
                
                # Detectar e configurar viewport baseado no conteúdo
                if "1080px" in html_content and "1080px" in html_content:
                    await page.set_viewport_size({"width": 1080, "height": 1080})
                elif "1200px" in html_content and "630px" in html_content:
                    await page.set_viewport_size({"width": 1200, "height": 630})
                elif "1200px" in html_content and "675px" in html_content:
                    await page.set_viewport_size({"width": 1200, "height": 675})
                else:
                    await page.set_viewport_size({"width": 1080, "height": 1080})
                
                # Carregar conteúdo e aguardar recursos
                await page.set_content(html_content, wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                if format.lower() == 'gif':
                    # Para GIF, capturar múltiplos screenshots
                    frames = []
                    for i in range(10):
                        screenshot = await page.screenshot(type='png')
                        img = Image.open(io.BytesIO(screenshot))
                        if img.mode == 'RGBA':
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[-1])
                            frames.append(rgb_img)
                        else:
                            frames.append(img)
                        await page.wait_for_timeout(300)
                    
                    # Criar GIF
                    output = io.BytesIO()
                    frames[0].save(
                        output,
                        format='GIF',
                        save_all=True,
                        append_images=frames[1:],
                        duration=300,
                        loop=0,
                        optimize=True
                    )
                    await browser.close()
                    return output.getvalue()
                    
                else:
                    # Screenshot normal
                    if format.lower() in ['jpg', 'jpeg']:
                        screenshot = await page.screenshot(type='jpeg', quality=95)
                    else:
                        screenshot = await page.screenshot(type='png')
                    
                    await browser.close()
                    return screenshot
                    
        except Exception as e:
            print(f"Erro Playwright: {e}")
            raise Exception(f"Erro ao gerar imagem com Playwright: {str(e)}")

    async def html_to_image(self, html_content, format='png'):
        """Converte HTML para imagem - tenta Playwright primeiro, depois Selenium"""
        
        # Validar formato
        valid_formats = ['png', 'jpg', 'jpeg', 'gif']
        if format.lower() not in valid_formats:
            raise ValueError(f"Formato inválido: {format}. Use: {', '.join(valid_formats)}")
        
        # Tentar Playwright primeiro (se disponível)
        if PLAYWRIGHT_AVAILABLE:
            try:
                print(f"🎭 Tentando Playwright para {format}...")
                return await self.playwright_html_to_image(html_content, format)
            except Exception as e:
                print(f"❌ Playwright falhou: {e}")
                print("🔄 Usando Selenium como fallback...")
        
        # Fallback para Selenium
        try:
            print(f"🌐 Usando Selenium para {format}...")
            return self.selenium_html_to_image(html_content, format)
        except Exception as e:
            print(f"❌ Selenium também falhou: {e}")
            raise Exception("Todos os métodos de conversão falharam")

    async def html_to_mp4(self, html_content, duration=5):
        """Gera MP4 - fallback para imagem estática se vídeo não funcionar"""
        
        if PLAYWRIGHT_AVAILABLE:
            try:
                print("🎬 Tentando gerar vídeo com Playwright...")
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                    page = await browser.new_page()
                    
                    # Configurar viewport
                    await page.set_viewport_size({"width": 1080, "height": 1080})
                    
                    # Carregar conteúdo
                    await page.set_content(html_content, wait_until='networkidle')
                    await page.wait_for_timeout(2000)
                    
                    # Criar arquivo temporário para vídeo
                    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
                    temp_video.close()
                    
                    # Iniciar gravação
                    await page.video.start(path=temp_video.name)
                    
                    # Gravar por duração especificada
                    await page.wait_for_timeout(duration * 1000)
                    
                    # Parar gravação
                    await page.video.stop()
                    await browser.close()
                    
                    # Ler arquivo
                    with open(temp_video.name, 'rb') as f:
                        video_bytes = f.read()
                    
                    os.unlink(temp_video.name)
                    return video_bytes
                    
            except Exception as e:
                print(f"❌ Vídeo falhou: {e}")
        
        # Fallback: criar "vídeo" estático (imagem como MP4)
        print("📸 Gerando imagem estática como fallback...")
        image_bytes = await self.html_to_image(html_content, 'png')
        
        # Retornar imagem (front-end vai tratar como "vídeo")
        return image_bytes
    
    def get_instagram_template(self):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Instagram Post</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { font-family: 'Inter', sans-serif; }
                .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .animate-float { animation: float 6s ease-in-out infinite; }
                .animate-pulse-slow { animation: pulse 3s ease-in-out infinite; }
                .animate-slide-in { animation: slideIn 2s ease-out; }
                .animate-rotate { animation: rotate 8s linear infinite; }
                .animate-bounce-slow { animation: bounceSlow 4s ease-in-out infinite; }
                .animate-glow { animation: glow 2s ease-in-out infinite alternate; }
                
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-20px); }
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.8; transform: scale(1.05); }
                }
                
                @keyframes slideIn {
                    0% { transform: translateX(-100%); opacity: 0; }
                    100% { transform: translateX(0); opacity: 1; }
                }
                
                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes bounceSlow {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-15px); }
                }
                
                @keyframes glow {
                    0% { box-shadow: 0 0 20px rgba(255,255,255,0.3); }
                    100% { box-shadow: 0 0 40px rgba(255,255,255,0.6); }
                }
                
                .particle { animation: float 4s ease-in-out infinite; }
                .particle:nth-child(2) { animation-delay: -1s; }
                .particle:nth-child(3) { animation-delay: -2s; }
                .particle:nth-child(4) { animation-delay: -3s; }
            </style>
        </head>
        <body class="m-0 p-0">
            <div class="w-[1080px] h-[1080px] gradient-bg flex flex-col justify-center items-center relative overflow-hidden">
                {CONTENT}
                <!-- Partículas animadas de fundo -->
                <div class="absolute top-10 left-10 w-4 h-4 bg-white/20 rounded-full particle"></div>
                <div class="absolute top-32 right-20 w-6 h-6 bg-white/15 rounded-full particle"></div>
                <div class="absolute bottom-20 left-32 w-3 h-3 bg-white/25 rounded-full particle"></div>
                <div class="absolute bottom-40 right-10 w-5 h-5 bg-white/10 rounded-full particle"></div>
            </div>
        </body>
        </html>
        """
    
    def get_linkedin_template(self):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LinkedIn Post</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { font-family: 'Source Sans Pro', sans-serif; }
                .professional-bg { background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%); }
            </style>
        </head>
        <body class="m-0 p-0">
            <div class="w-[1200px] h-[630px] professional-bg flex flex-col justify-center items-center relative">
                {CONTENT}
            </div>
        </body>
        </html>
        """
    
    def get_twitter_template(self):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Twitter Post</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Twitter+Chirp:wght@400;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
                .twitter-bg { background: linear-gradient(135deg, #1da1f2 0%, #1a91da 100%); }
            </style>
        </head>
        <body class="m-0 p-0">
            <div class="w-[1200px] h-[675px] twitter-bg flex flex-col justify-center items-center relative">
                {CONTENT}
            </div>
        </body>
        </html>
        """

    def generate_post_content(self, prompt, platform="instagram"):
        """Gera conteúdo do post usando DeepSeek Reasoner"""
        platform_specs = {
            "instagram": "1080x1080px, visual impactante, cores vibrantes, foco em engajamento",
            "linkedin": "1200x630px, profissional, corporativo, foco em networking",
            "twitter": "1200x675px, conciso, viral, foco em compartilhamento"
        }
        
        system_prompt = f"""
        Você é um especialista em design para redes sociais. Crie APENAS o conteúdo HTML que vai dentro da div principal.
        
        Plataforma: {platform}
        Especificações: {platform_specs[platform]}
        
        REGRAS:
        1. Use apenas classes Tailwind CSS
        2. Use ícones Font Awesome quando apropriado
        3. Crie design moderno e atrativo
        4. Inclua animações CSS para vídeos: animate-float, animate-pulse-slow, animate-slide-in, animate-rotate, animate-bounce-slow, animate-glow
        5. NÃO inclua tags html, head, body - apenas o conteúdo da div
        6. Use cores que contrastem bem com o fundo
        7. Foque na legibilidade e impacto visual
        8. Para vídeos, use mais elementos animados e dinâmicos
        
        RETORNE APENAS O HTML DO CONTEÚDO, SEM EXPLICAÇÕES.
        """
        
        try:
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Crie um post sobre: {prompt}"}
                ],
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro ao gerar conteúdo: {e}")
            return f"""
            <div class="text-center text-white p-8">
                <i class="fas fa-image text-6xl mb-4 animate-pulse-slow"></i>
                <h1 class="text-5xl font-bold mb-4 animate-float">{prompt}</h1>
                <p class="text-xl opacity-90">Post gerado automaticamente</p>
                <div class="mt-8 flex justify-center space-x-4">
                    <i class="fab fa-instagram text-3xl animate-bounce-slow"></i>
                    <i class="fab fa-linkedin text-3xl animate-bounce-slow" style="animation-delay: 0.2s"></i>
                    <i class="fab fa-twitter text-3xl animate-bounce-slow" style="animation-delay: 0.4s"></i>
                </div>
            </div>
            """

    def create_post(self, prompt, platform="instagram"):
        """Cria post completo"""
        template = self.templates[platform]
        content = self.generate_post_content(prompt, platform)
        html = template.replace("{CONTENT}", content)
        return html

# Instanciar o agente
agent = SocialMediaAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enhance-prompt', methods=['POST'])
def enhance_prompt():
    """Melhora/expande o prompt do usuário usando IA"""
    data = request.get_json()
    original_prompt = data.get('prompt', '')
    platform = data.get('platform', 'instagram')
    
    if not original_prompt:
        return jsonify({'error': 'Prompt é obrigatório'}), 400
    
    platform_context = {
        "instagram": "Instagram (visual, jovem, engajamento, hashtags, stories)",
        "linkedin": "LinkedIn (profissional, networking, B2B, thought leadership)",
        "twitter": "Twitter/X (viral, conciso, trending, retweets)"
    }
    
    try:
        enhancement_prompt = f"""
        Você é um especialista em marketing de redes sociais. 
        O usuário forneceu esta ideia básica: "{original_prompt}"
        
        Plataforma alvo: {platform_context[platform]}
        
        Expanda e melhore este prompt para criar um briefing detalhado para geração de post.
        
        Inclua:
        1. Descrição visual detalhada (cores, estilo, elementos)
        2. Tom de voz e mensagem principal
        3. Público-alvo específico
        4. Call-to-action sugerido
        5. Elementos de design (ícones, gráficos, layout)
        6. Palavras-chave e hashtags relevantes
        
        Mantenha o prompt expandido conciso mas completo (máximo 3-4 linhas).
        Retorne APENAS o prompt melhorado, sem explicações adicionais.
        """
        
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "Você é um expert em marketing digital e copywriting para redes sociais."},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        enhanced = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'enhanced_prompt': enhanced,
            'original_prompt': original_prompt
        })
        
    except Exception as e:
        print(f"Erro ao melhorar prompt: {e}")
        # Fallback: retornar prompt com melhorias básicas
        fallback_enhanced = f"{original_prompt}. Design moderno e atrativo para {platform}, com cores vibrantes, elementos visuais impactantes, foco no público-alvo da plataforma, incluindo call-to-action relevante."
        return jsonify({
            'success': True,
            'enhanced_prompt': fallback_enhanced,
            'original_prompt': original_prompt,
            'fallback': True
        })

@app.route('/generate', methods=['POST'])
def generate_post():
    data = request.get_json()
    prompt = data.get('prompt', '')
    platform = data.get('platform', 'instagram')
    
    if not prompt:
        return jsonify({'error': 'Prompt é obrigatório'}), 400
    
    try:
        html_content = agent.create_post(prompt, platform)
        
        # Armazenar HTML temporariamente
        content_id = str(uuid.uuid4())
        html_storage[content_id] = html_content
        
        return jsonify({
            'success': True,
            'html': html_content,
            'content_id': content_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_file():
    """Nova rota usando POST para download"""
    data = request.get_json()
    
    # Obter parâmetros
    format = data.get('format', 'png').lower()
    html_content = data.get('html', '')
    content_id = data.get('content_id', '')
    duration = int(data.get('duration', 5))
    
    # Tentar obter HTML do storage se content_id fornecido
    if content_id and content_id in html_storage:
        html_content = html_storage[content_id]
    
    if not html_content:
        return jsonify({'error': 'HTML content is required'}), 400
    
    # Validar formato
    valid_formats = ['png', 'jpg', 'jpeg', 'gif', 'mp4']
    if format not in valid_formats:
        return jsonify({'error': f'Invalid format. Use: {", ".join(valid_formats)}'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if format == 'mp4':
            # Gerar vídeo
            file_bytes = loop.run_until_complete(agent.html_to_mp4(html_content, duration))
            mimetype = 'video/mp4'
            file_ext = 'mp4'
        else:
            # Gerar imagem (PNG, JPG, JPEG, GIF)
            file_bytes = loop.run_until_complete(agent.html_to_image(html_content, format))
            
            if format == 'gif':
                mimetype = 'image/gif'
                file_ext = 'gif'
            elif format in ['jpg', 'jpeg']:
                mimetype = 'image/jpeg'
                file_ext = 'jpg'
            else:
                mimetype = 'image/png'
                file_ext = 'png'
            
        loop.close()
        
        # Criar nome de arquivo único
        filename = f'post_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}.{file_ext}'
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}')
        temp_file.write(file_bytes)
        temp_file.close()
        
        # Enviar arquivo
        response = send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
        # Agendar remoção do arquivo após envio
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                # Limpar storage se necessário
                if content_id in html_storage:
                    del html_storage[content_id]
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Erro no download: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'details': traceback.format_exc()}), 500

# Manter rota antiga para compatibilidade
@app.route('/download/<format>')
def download_image_legacy(format):
    """Rota legada - redireciona para a nova"""
    return jsonify({
        'error': 'Esta rota está deprecada. Use POST /download',
        'example': {
            'method': 'POST',
            'url': '/download',
            'body': {
                'format': format,
                'html': 'seu_html_aqui',
                'content_id': 'opcional_id_do_conteudo'
            }
        }
    }), 400

@app.route('/test-conversion')
def test_conversion():
    """Rota para testar conversões"""
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; padding: 0; }
            .test { 
                width: 500px; 
                height: 500px; 
                background: linear-gradient(45deg, #ff0000, #00ff00);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 48px;
                font-family: Arial;
            }
        </style>
    </head>
    <body>
        <div class="test">TESTE</div>
    </body>
    </html>
    """
    
    results = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for format in ['png', 'jpg', 'gif']:
        try:
            file_bytes = loop.run_until_complete(agent.html_to_image(test_html, format))
            results[format] = f"✅ Success - {len(file_bytes)} bytes"
        except Exception as e:
            results[format] = f"❌ Error: {str(e)}"
    
    loop.close()
    
    return jsonify({
        'status': 'Test complete',
        'results': results,
        'playwright_available': PLAYWRIGHT_AVAILABLE
    })

@app.route('/preview', methods=['POST'])
def preview():
    """Preview do HTML renderizado"""
    data = request.get_json()
    html_content = data.get('html', '')
    content_id = data.get('content_id', '')
    
    if content_id and content_id in html_storage:
        html_content = html_storage[content_id]
    
    if not html_content:
        return "No content to preview", 400
    
    return html_content

@app.route('/cleanup-storage')
def cleanup_storage():
    """Limpar armazenamento temporário (útil para manutenção)"""
    count = len(html_storage)
    html_storage.clear()
    return jsonify({
        'status': 'success',
        'message': f'Cleared {count} items from storage'
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor...")
    print(f"📦 Playwright disponível: {PLAYWRIGHT_AVAILABLE}")
    print("🔧 Selenium configurado como fallback")
    print("✨ Formatos suportados: PNG, JPG, JPEG, GIF, MP4")
    app.run(debug=True, port=5010)