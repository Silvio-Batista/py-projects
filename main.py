import json
from datetime import datetime

# Caminhos dos arquivos
json_file = 'Constellation Euro V_2019_13+15-190.json'
output_sql = 'import_script.sql'

# Obter o timestamp atual
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Carregar o arquivo JSON
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Função para escapar strings no SQL
def escape_string(value):
    if isinstance(value, str):
        return value.replace("'", "''")
    return value

# Função para gerar instruções SQL para a tabela `categorias`
def generate_categoria_insert(categoria_id, categoria_data):
    nome_categoria = escape_string(categoria_data["grupo"])
    modelo_id = 1
    ano_id = 1
    versao_id = 1
    return (f"INSERT INTO categorias (id, modelo_id, ano_id, versao_id, nome, created_at, updated_at) "
            f"VALUES ({categoria_id}, {modelo_id}, {ano_id}, {versao_id}, '{nome_categoria}', '{current_timestamp}', '{current_timestamp}');\n")

# Função para gerar instruções SQL para a tabela `subcategorias`
def generate_subcategoria_insert(subcategoria_id, categoria_id, subcategoria_data):
    nome_subcategoria = escape_string(subcategoria_data["Denominação"])
    ilustracao = escape_string(subcategoria_data["Ilustração"])
    observacao = escape_string(subcategoria_data["Observação"])
    indicacao_modelo = escape_string(subcategoria_data.get("Indicação de modelo", ""))
    cod_imagem = escape_string(subcategoria_data["cod_imagem"])
    
    return (f"INSERT INTO subcategorias (id, categoria_id, denominacao, ilustracao, observacao, indicacao_modelo, cod_imagem, created_at, updated_at) "
            f"VALUES ({subcategoria_id}, {categoria_id}, '{nome_subcategoria}', '{ilustracao}', '{observacao}', '{indicacao_modelo}', '{cod_imagem}', '{current_timestamp}', '{current_timestamp}');\n")

# Função para gerar instruções SQL para a tabela `pecas`
def generate_peca_insert(peca_id, peca_data, subcategoria_id):
    pos = format_value(peca_data.get("Pos.", None))
    numero_item = escape_string(peca_data["Número do item"])
    tempo_montagem = escape_string(peca_data["Tempo de montagem"])
    nome_peca = escape_string(peca_data["Denominação"])
    observacao = escape_string(peca_data["Observação"])
    unidades = escape_string(peca_data["Unidades"])
    modelo_indicacao = escape_string(peca_data.get("Indicação de modelo", ""))
    
    return (f"INSERT INTO pecas (id, numero_item, tempo_montagem, denominacao, observacao, unidades, indicacao_modelo, created_at, updated_at) "
            f"VALUES ({peca_id}, '{numero_item}', '{tempo_montagem}', '{nome_peca}', '{observacao}', '{unidades}', '{modelo_indicacao}', '{current_timestamp}', '{current_timestamp}');\n")

# Função para gerar instruções SQL para a tabela `subcategorias_pecas`
def generate_subcategorias_pecas_insert(subcategoria_id, peca_id, posicao, posicao_label):
    return (f"INSERT INTO subcategoria_pecas (subcategoria_id, peca_id, posicao, posicao_label, created_at, updated_at) "
            f"VALUES ({subcategoria_id}, {peca_id}, '{posicao}', '{posicao_label}', '{current_timestamp}', '{current_timestamp}');\n")

# Função para gerar instruções SQL para a tabela `hotspots`
def generate_hotspot_insert(hotspot_id, subcategoria_id, hotspot_data):
    key = escape_string(hotspot_data["key"])
    return f"INSERT INTO hotspots (id, subcategoria_id, `key`, created_at, updated_at) VALUES ({hotspot_id}, {subcategoria_id}, '{key}', '{current_timestamp}', '{current_timestamp}');\n"

# Função para gerar instruções SQL para a tabela `areas`
def generate_area_insert(area_id, hotspot_id, area_data):
    left = area_data["left"]
    top = area_data["top"]
    width = area_data["width"]
    height = area_data["height"]
    descricao = escape_string(area_data.get("descr", ""))
    
    return (f"INSERT INTO areas (id, hotspot_id, `left`, top, width, height, descricao, created_at, updated_at) "
            f"VALUES ({area_id}, {hotspot_id}, {left}, {top}, {width}, {height}, '{descricao}', '{current_timestamp}', '{current_timestamp}');\n")

# Função para limpar parênteses ao redor de números e converter para inteiro
def format_value(value):
    if isinstance(value, str):
        if value.startswith("(") and value.endswith(")"):
            value = value[1:-1]
        if value == "-":
            return None
    try:
        return int(value)
    except ValueError:
        return None

# Processar e gerar o script SQL
with open(output_sql, 'w', encoding='utf-8') as file:
    categoria_id = 1
    subcategoria_id = 1
    peca_id = 1
    hotspot_id = 1
    area_id = 1
    
    for categoria in data["data"]:
        file.write(generate_categoria_insert(categoria_id, categoria))
        
        for subcategoria in categoria.get("subgrupos", []):
            file.write(generate_subcategoria_insert(subcategoria_id, categoria_id, subcategoria))
            
            for peca in subcategoria.get("pecas", []):
                file.write(generate_peca_insert(peca_id, peca, subcategoria_id))
                posicao = format_value(peca.get("Pos.", None))
                posicao_label = f"Posição {posicao}: {peca['Denominação']}"
                file.write(generate_subcategorias_pecas_insert(subcategoria_id, peca_id, posicao, posicao_label))
                peca_id += 1
            
            for hotspot in (subcategoria.get("hotspots") or []):
                file.write(generate_hotspot_insert(hotspot_id, subcategoria_id, hotspot))
                
                for area in hotspot.get("areas", []):
                    file.write(generate_area_insert(area_id, hotspot_id, area))
                    area_id += 1
                
                hotspot_id += 1
            
            subcategoria_id += 1
        
        categoria_id += 1

print("Script de importação SQL gerado com sucesso.")
