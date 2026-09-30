import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import extrair_dados_nota_fiscal


def index(request):
    """Página principal do extrator de notas fiscais."""
    return render(request, 'extrator/index.html')


@csrf_exempt
@require_http_methods(['POST'])
def processar_pdf(request):
    """Endpoint para processar PDF de nota fiscal via Gemini."""
    try:
        arquivo_pdf = request.FILES.get('arquivo_pdf')

        if not arquivo_pdf:
            return JsonResponse(
                {'erro': 'Nenhum arquivo PDF foi enviado.'},
                status=400
            )

        if not arquivo_pdf.name.lower().endswith('.pdf'):
            return JsonResponse(
                {'erro': 'O arquivo deve estar no formato PDF.'},
                status=400
            )

        # Limite de 10MB
        if arquivo_pdf.size > 10 * 1024 * 1024:
            return JsonResponse(
                {'erro': 'O arquivo PDF deve ter no máximo 10MB.'},
                status=400
            )

        pdf_bytes = arquivo_pdf.read()
        dados_extraidos = extrair_dados_nota_fiscal(pdf_bytes, arquivo_pdf.name)

        return JsonResponse({
            'sucesso': True,
            'dados': dados_extraidos,
            'arquivo': arquivo_pdf.name
        })

    except ValueError as e:
        return JsonResponse(
            {'erro': str(e)},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'erro': f'Erro interno ao processar a nota fiscal: {str(e)}'},
            status=500
        )
