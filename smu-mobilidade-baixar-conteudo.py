import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

# URL da página
base_url = "https://www.gov.br/cidades/pt-br/central-de-conteudos/publicacoes/mobilidade-urbana"

# Pasta para salvar os PDFs
output_folder = "pdf_mobilidade"
os.makedirs(output_folder, exist_ok=True)

# Cabeçalhos para simular acesso de navegador
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Requisição HTTP
response = requests.get(base_url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Erro ao acessar a página: {response.status_code}")

# Parse do HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Buscar todos os links de PDF
pdf_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.endswith(".pdf"):
        full_url = urljoin(base_url, href)
        pdf_links.append(full_url)

print(f"{len(pdf_links)} PDFs encontrados. Iniciando download...")

# Baixar cada PDF
for url in pdf_links:
    filename = url.split("/")[-1]
    filepath = os.path.join(output_folder, filename)
    print(f"Baixando: {filename}")
    pdf_data = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(pdf_data.content)

print("Todos os arquivos foram baixados com sucesso.")
