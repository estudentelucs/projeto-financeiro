import json
import re
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import extrair_dados_nota_fiscal
from core.models import Fornecedor, Faturado, TipoDespesa, ContasPagar, Parcela


def limpa_documento(doc):
    """Remove pontuações de CPF/CNPJ para comparação flexível."""
    if not doc:
        return ''
    return re.sub(r'\D', '', str(doc))


def index(request):
    """Página principal do extrator de notas fiscais."""
    return render(request, 'extrator/index.html')


@csrf_exempt
@require_http_methods(['POST'])
def processar_pdf(request):
    """Endpoint para processar PDF de nota fiscal via Gemini e consultar o Banco de Dados (2ª Etapa)."""
    try:
        arquivo_pdf = request.FILES.get('arquivo_pdf')

        if not arquivo_pdf:
            return JsonResponse({'erro': 'Nenhum arquivo PDF foi enviado.'}, status=400)

        if not arquivo_pdf.name.lower().endswith('.pdf'):
            return JsonResponse({'erro': 'O arquivo deve estar no formato PDF.'}, status=400)

        if arquivo_pdf.size > 10 * 1024 * 1024:
            return JsonResponse({'erro': 'O arquivo PDF deve ter no máximo 10MB.'}, status=400)

        pdf_bytes = arquivo_pdf.read()
        dados_extraidos = extrair_dados_nota_fiscal(pdf_bytes, arquivo_pdf.name)

        # ==========================================================
        # 2ª ETAPA: Análise e Consulta no Banco de Dados
        # ==========================================================
        consulta_bd = {}

        # 1. Consulta Fornecedor (por CNPJ)
        fornec_data = dados_extraidos.get('fornecedor') or {}
        cnpj_extraido = fornec_data.get('cnpj') or ''
        razao_extraida = fornec_data.get('razao_social') or 'FORNECEDOR NÃO INFORMADO'
        fantasia_extraida = fornec_data.get('nome_fantasia') or ''

        fornecedor_obj = None
        if cnpj_extraido:
            cnpj_limpo = limpa_documento(cnpj_extraido)
            for f in Fornecedor.objects.all():
                if limpa_documento(f.cnpj) == cnpj_limpo:
                    fornecedor_obj = f
                    break

        if fornecedor_obj:
            consulta_bd['fornecedor'] = {
                'existe': True,
                'id': fornecedor_obj.id,
                'razao_social': fornecedor_obj.razao_social,
                'cnpj': fornecedor_obj.cnpj,
                'status_texto': f'EXISTE – ID: {fornecedor_obj.id}',
                'cor': '#0d6efd',
            }
        else:
            consulta_bd['fornecedor'] = {
                'existe': False,
                'id': None,
                'razao_social': razao_extraida,
                'cnpj': cnpj_extraido or 'NÃO INFORMADO',
                'status_texto': 'NÃO EXISTE',
                'cor': '#dc3545',
            }

        # 2. Consulta Faturado (por CPF)
        faturado_data = dados_extraidos.get('faturado') or {}
        cpf_extraido = faturado_data.get('cpf') or ''
        nome_faturado = faturado_data.get('nome_completo') or 'FATURADO NÃO INFORMADO'

        faturado_obj = None
        if cpf_extraido:
            cpf_limpo = limpa_documento(cpf_extraido)
            for fat in Faturado.objects.all():
                if limpa_documento(fat.cpf) == cpf_limpo:
                    faturado_obj = fat
                    break

        if faturado_obj:
            consulta_bd['faturado'] = {
                'existe': True,
                'id': faturado_obj.id,
                'nome_completo': faturado_obj.nome_completo,
                'cpf': faturado_obj.cpf,
                'status_texto': f'EXISTE – ID: {faturado_obj.id}',
                'cor': '#0d6efd',
            }
        else:
            consulta_bd['faturado'] = {
                'existe': False,
                'id': None,
                'nome_completo': nome_faturado,
                'cpf': cpf_extraido or 'NÃO INFORMADO',
                'status_texto': 'NÃO EXISTE',
                'cor': '#dc3545',
            }

        # 3. Consulta Despesa (por categoria/subcategoria)
        classif = dados_extraidos.get('classificacao_despesa')
        cat_nome = ''
        subcat_nome = ''

        if isinstance(classif, list) and len(classif) > 0:
            c0 = classif[0]
            if isinstance(c0, dict):
                cat_nome = c0.get('categoria', '')
                subcat_nome = c0.get('subcategoria', '')
            else:
                cat_nome = str(c0)
        elif isinstance(classif, dict):
            cat_nome = classif.get('categoria', '')
            subcat_nome = classif.get('subcategoria', '')
        elif isinstance(classif, str):
            cat_nome = classif

        despesa_obj = None
        if subcat_nome:
            despesa_obj = TipoDespesa.objects.filter(nome__icontains=subcat_nome).first()
        if not despesa_obj and cat_nome:
            despesa_obj = TipoDespesa.objects.filter(categoria__icontains=cat_nome).first()

        desc_exibicao = f"{cat_nome} - {subcat_nome}".strip(' -') if subcat_nome else cat_nome or 'DESPESA NÃO IDENTIFICADA'

        if despesa_obj:
            consulta_bd['despesa'] = {
                'existe': True,
                'id': despesa_obj.id,
                'descricao': f'{despesa_obj.categoria} ({despesa_obj.nome})',
                'status_texto': f'EXISTE – ID: {despesa_obj.id}',
                'cor': '#0d6efd',
            }
        else:
            consulta_bd['despesa'] = {
                'existe': False,
                'id': None,
                'descricao': desc_exibicao,
                'status_texto': 'NÃO EXISTE',
                'cor': '#dc3545',
            }

        return JsonResponse({
            'sucesso': True,
            'dados': dados_extraidos,
            'consulta_bd': consulta_bd,
            'arquivo': arquivo_pdf.name
        })

    except ValueError as e:
        return JsonResponse({'erro': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'erro': f'Erro interno ao processar a nota fiscal: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def lancar_movimento(request):
    """
    2ª ETAPA: Cria novos registros (se não existirem) e gera o Movimento de Contas e suas Parcelas.
    1. CRIAR O NOVO FORNECEDOR (se for o caso)
    2. CRIAR O NOVO FATURADO (se for o caso)
    3. CRIAR NOVA DESPESA (se for o caso)
    4. CRIAR UM NOVO REGISTRO DO MOVIMENTO E SUA PARCELA
    5. INFORMAR AO USUÁRIO QUE REGISTRO FOI LANÇADO COM SUCESSO.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        dados = payload.get('dados', {})
        consulta = payload.get('consulta_bd', {})

        if not dados:
            return JsonResponse({'erro': 'Dados da nota fiscal não informados.'}, status=400)

        # 1. Tratar Fornecedor
        fornec_data = dados.get('fornecedor') or {}
        cnpj = (fornec_data.get('cnpj') or '00.000.000/0000-00').strip()
        razao = (fornec_data.get('razao_social') or 'Fornecedor sem razão social').strip()
        fantasia = (fornec_data.get('nome_fantasia') or razao).strip()

        fornecedor_obj = None
        if cnpj:
            cnpj_limpo = limpa_documento(cnpj)
            for f in Fornecedor.objects.all():
                if limpa_documento(f.cnpj) == cnpj_limpo:
                    fornecedor_obj = f
                    break

        if not fornecedor_obj:
            fornecedor_obj = Fornecedor.objects.create(
                razao_social=razao,
                nome_fantasia=fantasia,
                cnpj=cnpj,
                ativo=True
            )

        # 2. Tratar Faturado
        fat_data = dados.get('faturado') or {}
        cpf = (fat_data.get('cpf') or '000.000.000-00').strip()
        nome_fat = (fat_data.get('nome_completo') or 'Faturado sem nome').strip()

        faturado_obj = None
        if cpf:
            cpf_limpo = limpa_documento(cpf)
            for fat in Faturado.objects.all():
                if limpa_documento(fat.cpf) == cpf_limpo:
                    faturado_obj = fat
                    break

        if not faturado_obj:
            faturado_obj = Faturado.objects.create(
                nome_completo=nome_fat,
                cpf=cpf,
                ativo=True
            )

        # 3. Tratar Despesa
        classif = dados.get('classificacao_despesa')
        cat_nome = 'OUTRAS DESPESAS'
        subcat_nome = 'Despesas Gerais'

        if isinstance(classif, list) and len(classif) > 0:
            c0 = classif[0]
            if isinstance(c0, dict):
                cat_nome = c0.get('categoria', cat_nome)
                subcat_nome = c0.get('subcategoria', subcat_nome)
            elif isinstance(c0, str):
                cat_nome = c0
        elif isinstance(classif, dict):
            cat_nome = classif.get('categoria', cat_nome)
            subcat_nome = classif.get('subcategoria', subcat_nome)
        elif isinstance(classif, str):
            cat_nome = classif

        despesa_obj = TipoDespesa.objects.filter(nome__icontains=subcat_nome).first()
        if not despesa_obj:
            despesa_obj = TipoDespesa.objects.filter(categoria__icontains=cat_nome).first()

        if not despesa_obj:
            despesa_obj = TipoDespesa.objects.create(
                categoria=cat_nome,
                nome=subcat_nome,
                descricao=f'Despesa classificada automaticamente para {cat_nome}',
                ativo=True
            )

        # 4. Criar Novo Registro do Movimento (Contas a Pagar)
        num_nf = str(dados.get('numero_nota_fiscal') or 'S/N')
        data_emissao = dados.get('data_emissao') or '2026-01-01'
        desc_produtos = dados.get('descricao_produtos') or 'Produtos constantes na nota fiscal.'
        valor_total_raw = dados.get('valor_total') or 0
        try:
            valor_total = Decimal(str(valor_total_raw))
        except Exception:
            valor_total = Decimal('0.00')

        conta_pagar = ContasPagar.objects.create(
            fornecedor=fornecedor_obj,
            faturado=faturado_obj,
            numero_nota_fiscal=num_nf,
            data_emissao=data_emissao,
            descricao_produtos=desc_produtos,
            valor_total=valor_total,
            ativo=True
        )
        conta_pagar.tipos_despesa.add(despesa_obj)

        # 5. Criar Parcela(s)
        parcelas_data = dados.get('parcelas')
        parcelas_criadas = []

        if isinstance(parcelas_data, list) and len(parcelas_data) > 0:
            for p in parcelas_data:
                p_num = p.get('numero', 1)
                p_venc = p.get('data_vencimento') or dados.get('data_vencimento') or data_emissao
                p_val_raw = p.get('valor') or valor_total
                try:
                    p_val = Decimal(str(p_val_raw))
                except Exception:
                    p_val = valor_total

                parcela = Parcela.objects.create(
                    conta_pagar=conta_pagar,
                    numero_parcela=p_num,
                    valor=p_val,
                    data_vencimento=p_venc,
                    ativo=True
                )
                parcelas_criadas.append(parcela.id)
        else:
            # Parcela única
            venc = dados.get('data_vencimento') or data_emissao
            parcela = Parcela.objects.create(
                conta_pagar=conta_pagar,
                numero_parcela=1,
                valor=valor_total,
                data_vencimento=venc,
                ativo=True
            )
            parcelas_criadas.append(parcela.id)

        # 6. Informar ao usuário que registro foi lançado com sucesso
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'REGISTRO FOI LANÇADO COM SUCESSO!',
            'conta_id': conta_pagar.id,
            'fornecedor_id': fornecedor_obj.id,
            'fornecedor_nome': fornecedor_obj.razao_social,
            'faturado_id': faturado_obj.id,
            'faturado_nome': faturado_obj.nome_completo,
            'despesa_id': despesa_obj.id,
            'despesa_nome': f'{despesa_obj.categoria} - {despesa_obj.nome}',
            'numero_nf': conta_pagar.numero_nota_fiscal,
            'total_parcelas': len(parcelas_criadas),
        })

    except Exception as e:
        return JsonResponse({'erro': f'Erro ao lançar movimento no banco de dados: {str(e)}'}, status=500)
