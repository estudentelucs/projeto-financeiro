import json
import os
from google import genai
from google.genai import types


CATEGORIAS_DESPESA = {
    'INSUMOS AGRÍCOLAS': [
        'Sementes', 'Fertilizantes', 'Defensivos Agrícolas', 'Corretivos'
    ],
    'MANUTENÇÃO E OPERAÇÃO': [
        'Combustíveis e Lubrificantes', 'Peças, Parafusos, Componentes Mecânicos',
        'Manutenção de Máquinas e Equipamentos', 'Pneus, Filtros, Correias',
        'Ferramentas e Utensílios'
    ],
    'RECURSOS HUMANOS': [
        'Mão de Obra Temporária', 'Salários e Encargos'
    ],
    'SERVIÇOS OPERACIONAIS': [
        'Frete e Transporte', 'Colheita Terceirizada',
        'Secagem e Armazenagem', 'Pulverização e Aplicação'
    ],
    'INFRAESTRUTURA E UTILIDADES': [
        'Energia Elétrica', 'Arrendamento de Terras',
        'Construções e Reformas', 'Materiais de Construção'
    ],
    'ADMINISTRATIVAS': [
        'Honorários (Contábeis, Advocatícios, Agronômicos)',
        'Despesas Bancárias e Financeiras'
    ],
    'SEGUROS E PROTEÇÃO': [
        'Seguro Agrícola', 'Seguro de Ativos (Máquinas/Veículos)',
        'Seguro Prestamista'
    ],
    'IMPOSTOS E TAXAS': [
        'ITR, IPTU, IPVA, INCRA-CCIR'
    ],
    'INVESTIMENTOS': [
        'Aquisição de Máquinas e Implementos', 'Aquisição de Veículos',
        'Aquisição de Imóveis', 'Infraestrutura Rural'
    ],
}


def extrair_dados_nota_fiscal(pdf_bytes: bytes, nome_arquivo: str) -> dict:
    """
    Envia um PDF de nota fiscal ao Gemini para extração de dados estruturados.
    Retorna um dicionário com os dados extraídos.
    """
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY não configurada. Defina a variável de ambiente no arquivo .env')

    client = genai.Client(api_key=api_key)

    categorias_texto = ''
    for categoria, subcategorias in CATEGORIAS_DESPESA.items():
        categorias_texto += f'\n- {categoria}:'
        for sub in subcategorias:
            categorias_texto += f'\n  - {sub}'

    prompt = f"""Você é um especialista em análise de notas fiscais brasileiras.
Analise o PDF da nota fiscal anexado e extraia os seguintes dados em formato JSON.

Campos obrigatórios para extração:
1. **fornecedor**: objeto com:
   - razao_social: Razão Social do fornecedor/emitente
   - nome_fantasia: Nome Fantasia do fornecedor/emitente
   - cnpj: CNPJ do fornecedor/emitente (formato: XX.XXX.XXX/XXXX-XX)

2. **faturado**: objeto com:
   - nome_completo: Nome completo do destinatário/comprador
   - cpf: CPF do destinatário (formato: XXX.XXX.XXX-XX)

3. **numero_nota_fiscal**: Número da nota fiscal
4. **data_emissao**: Data de emissão (formato: YYYY-MM-DD)
5. **descricao_produtos**: Descrição detalhada dos produtos/serviços listados na nota
6. **quantidade_parcelas**: Número de parcelas (se não informado, assumir 1)
7. **parcelas**: array de objetos, cada um com:
   - numero: número da parcela
   - valor: valor da parcela (número decimal)
   - data_vencimento: data de vencimento (formato: YYYY-MM-DD)
8. **valor_total**: Valor total da nota fiscal (número decimal)
9. **classificacao_despesa**: Classificação da despesa baseada nos produtos.

Para a classificação da despesa, analise os produtos da nota fiscal e classifique
de acordo com as categorias abaixo. Retorne um array de objetos com 'categoria' e 'subcategoria':
{categorias_texto}

Exemplos de classificação:
- Compra de Óleo Diesel → MANUTENÇÃO E OPERAÇÃO / Combustíveis e Lubrificantes
- Compra de Material Hidráulico → INFRAESTRUTURA E UTILIDADES / Materiais de Construção
- Compra de Sementes de Soja → INSUMOS AGRÍCOLAS / Sementes

IMPORTANTE:
- Retorne APENAS o JSON, sem texto adicional, sem markdown, sem blocos de código.
- Todos os valores monetários devem ser números decimais (não strings).
- Todas as datas devem estar no formato YYYY-MM-DD.
- Se algum campo não for encontrado, use null.
- O JSON deve ser válido e parseable.
"""

    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type='application/pdf'
    )

    modelos_candidatos = [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-2.5-pro',
        'gemini-1.5-pro',
    ]

    response = None
    ultimo_erro = None

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
    )

    for modelo in modelos_candidatos:
        for tentativa in range(2):
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=[
                        prompt,
                        pdf_part
                    ],
                    config=config
                )
                if response and response.text:
                    break
            except Exception as e:
                ultimo_erro = e
                import time
                time.sleep(1)
        if response and response.text:
            break

    if not response or not response.text:
        raise ValueError(f'Não foi possível obter resposta dos modelos do Gemini. Erro: {ultimo_erro}')

    texto_resposta = response.text.strip()

    # Limpar possíveis markers de código
    if texto_resposta.startswith('```json'):
        texto_resposta = texto_resposta[7:]
    if texto_resposta.startswith('```'):
        texto_resposta = texto_resposta[3:]
    if texto_resposta.endswith('```'):
        texto_resposta = texto_resposta[:-3]
    texto_resposta = texto_resposta.strip()

    try:
        dados = json.loads(texto_resposta)
    except json.JSONDecodeError as e:
        raise ValueError(f'Erro ao processar resposta do Gemini. Resposta recebida: {texto_resposta[:500]}... Erro: {str(e)}')

    return dados
