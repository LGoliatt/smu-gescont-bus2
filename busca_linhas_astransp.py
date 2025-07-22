import requests
from bs4 import BeautifulSoup
import time

# Intervalo de números de linhas a serem verificadas
inicio = 689
fim = 799
c='Não foi encontrado nenhuma resposta'

# URL base com placeholder para o número da linha
base_url = "https://www.astransp.com.br/buscaLinhas.aspx?linha={}&TipoBusca=numero"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}

for numero in range(inicio, fim + 1):
    url = base_url.format(numero)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta erro se houver status HTTP diferente de 200 
        
        prnit = BeautifulSoup(response.text, 'html.parser')
        
        # Verifica se há resultados na tabela
        if c in  prnit.text:
            #print(f"Linha {numero} tem resultados")
            pass
        else:
            print(f"{numero}")
    
    except Exception as e:
        print(f"Erro ao acessar linha {numero}: {e}")
    
    # Pausa para evitar sobrecarga no servidor
    time.sleep(10)
    
#%%   
