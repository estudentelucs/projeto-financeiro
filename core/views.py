from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from .models import (
    Fornecedor, Cliente, Faturado,
    TipoDespesa, TipoReceita,
    ContasPagar, ContasReceber, Parcela
)
from .forms import (
    CustomLoginForm, FornecedorForm, ClienteForm, FaturadoForm,
    TipoDespesaForm, TipoReceitaForm, ContasPagarForm, ContasReceberForm
)


def login_view(request):
    """Tela de login do sistema."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('core:home')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = CustomLoginForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Logout do usuário."""
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('core:login')


@login_required
def home(request):
    """Dashboard principal com métricas e código da última atualização do GitHub."""
    total_fornecedores = Fornecedor.objects.filter(ativo=True).count()
    total_clientes = Cliente.objects.filter(ativo=True).count()
    total_faturados = Faturado.objects.filter(ativo=True).count()
    total_despesas = TipoDespesa.objects.filter(ativo=True).count()
    total_receitas = TipoReceita.objects.filter(ativo=True).count()

    total_pagar_valor = ContasPagar.objects.filter(ativo=True).aggregate(s=Sum('valor_total'))['s'] or 0
    total_receber_valor = ContasReceber.objects.filter(ativo=True).aggregate(s=Sum('valor_total'))['s'] or 0

    ultimas_contas_pagar = ContasPagar.objects.filter(ativo=True).select_related('fornecedor').order_by('-id')[:5]

    context = {
        'total_fornecedores': total_fornecedores,
        'total_clientes': total_clientes,
        'total_faturados': total_faturados,
        'total_despesas': total_despesas,
        'total_receitas': total_receitas,
        'total_pagar_valor': total_pagar_valor,
        'total_receber_valor': total_receber_valor,
        'ultimas_contas_pagar': ultimas_contas_pagar,
    }
    return render(request, 'core/home.html', context)


# ==========================================================
# 1. MANTER FORNECEDOR
# ==========================================================

@login_required
def fornecedor_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    # Requisito a: Tabela de registros inicialmente vazia
    carregou = False
    fornecedores = []

    if todos or q:
        carregou = True
        qs = Fornecedor.objects.all()
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            # Requisito c: TODOS carrega status = ATIVO
            qs = qs.filter(ativo=True)

        if q:
            # Requisito e: Busca por mais de um elemento
            qs = qs.filter(
                Q(razao_social__icontains=q) |
                Q(nome_fantasia__icontains=q) |
                Q(cnpj__icontains=q) |
                Q(email__icontains=q) |
                Q(telefone__icontains=q)
            )
        fornecedores = qs.order_by('razao_social')

    return render(request, 'core/fornecedor_list.html', {
        'fornecedores': fornecedores,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def fornecedor_create(request):
    # Requisito g: No CREATE campo STATUS oculto = ATIVO
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            messages.success(request, f'Fornecedor "{obj.razao_social}" cadastrado com sucesso!')
            return redirect('core:fornecedor_list')
    else:
        form = FornecedorForm()
    return render(request, 'core/fornecedor_form.html', {'form': form, 'titulo': 'Novo Fornecedor'})


@login_required
def fornecedor_update(request, pk):
    # Requisito h: No UPDATE campo STATUS oculto
    obj = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fornecedor "{obj.razao_social}" atualizado com sucesso!')
            return redirect('core:fornecedor_list')
    else:
        form = FornecedorForm(instance=obj)
    return render(request, 'core/fornecedor_form.html', {'form': form, 'titulo': f'Editar Fornecedor: {obj.razao_social}', 'objeto': obj})


@login_required
def fornecedor_delete(request, pk):
    # Requisito i: No DELETE altera campo STATUS = INATIVO (Exclusão Lógica)
    obj = get_object_or_404(Fornecedor, pk=pk)
    obj.inativar()
    messages.warning(request, f'Fornecedor "{obj.razao_social}" foi INATIVADO com sucesso (Exclusão Lógica).')
    return redirect('core:fornecedor_list')


@login_required
def fornecedor_reativar(request, pk):
    obj = get_object_or_404(Fornecedor, pk=pk)
    obj.reativar()
    messages.success(request, f'Fornecedor "{obj.razao_social}" foi REATIVADO com sucesso!')
    return redirect('core:fornecedor_list')


# ==========================================================
# 2. MANTER CLIENTE
# ==========================================================

@login_required
def cliente_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    clientes = []

    if todos or q:
        carregou = True
        qs = Cliente.objects.all()
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(nome_completo__icontains=q) |
                Q(cpf__icontains=q) |
                Q(cnpj__icontains=q) |
                Q(email__icontains=q) |
                Q(telefone__icontains=q)
            )
        clientes = qs.order_by('nome_completo')

    return render(request, 'core/cliente_list.html', {
        'clientes': clientes,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            messages.success(request, f'Cliente "{obj.nome_completo}" cadastrado com sucesso!')
            return redirect('core:cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'core/cliente_form.html', {'form': form, 'titulo': 'Novo Cliente'})


@login_required
def cliente_update(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{obj.nome_completo}" atualizado com sucesso!')
            return redirect('core:cliente_list')
    else:
        form = ClienteForm(instance=obj)
    return render(request, 'core/cliente_form.html', {'form': form, 'titulo': f'Editar Cliente: {obj.nome_completo}', 'objeto': obj})


@login_required
def cliente_delete(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    obj.inativar()
    messages.warning(request, f'Cliente "{obj.nome_completo}" foi INATIVADO com sucesso (Exclusão Lógica).')
    return redirect('core:cliente_list')


@login_required
def cliente_reativar(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    obj.reativar()
    messages.success(request, f'Cliente "{obj.nome_completo}" foi REATIVADO com sucesso!')
    return redirect('core:cliente_list')


# ==========================================================
# 3. MANTER FATURADO
# ==========================================================

@login_required
def faturado_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    faturados = []

    if todos or q:
        carregou = True
        qs = Faturado.objects.all()
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(nome_completo__icontains=q) |
                Q(cpf__icontains=q) |
                Q(email__icontains=q) |
                Q(telefone__icontains=q)
            )
        faturados = qs.order_by('nome_completo')

    return render(request, 'core/faturado_list.html', {
        'faturados': faturados,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def faturado_create(request):
    if request.method == 'POST':
        form = FaturadoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            messages.success(request, f'Faturado "{obj.nome_completo}" cadastrado com sucesso!')
            return redirect('core:faturado_list')
    else:
        form = FaturadoForm()
    return render(request, 'core/faturado_form.html', {'form': form, 'titulo': 'Novo Faturado'})


@login_required
def faturado_update(request, pk):
    obj = get_object_or_404(Faturado, pk=pk)
    if request.method == 'POST':
        form = FaturadoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Faturado "{obj.nome_completo}" atualizado com sucesso!')
            return redirect('core:faturado_list')
    else:
        form = FaturadoForm(instance=obj)
    return render(request, 'core/faturado_form.html', {'form': form, 'titulo': f'Editar Faturado: {obj.nome_completo}', 'objeto': obj})


@login_required
def faturado_delete(request, pk):
    obj = get_object_or_404(Faturado, pk=pk)
    obj.inativar()
    messages.warning(request, f'Faturado "{obj.nome_completo}" foi INATIVADO com sucesso (Exclusão Lógica).')
    return redirect('core:faturado_list')


@login_required
def faturado_reativar(request, pk):
    obj = get_object_or_404(Faturado, pk=pk)
    obj.reativar()
    messages.success(request, f'Faturado "{obj.nome_completo}" foi REATIVADO com sucesso!')
    return redirect('core:faturado_list')


# ==========================================================
# 4. MANTER TIPO DE DESPESA
# ==========================================================

@login_required
def despesa_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    despesas = []

    if todos or q:
        carregou = True
        qs = TipoDespesa.objects.all()
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(categoria__icontains=q) |
                Q(nome__icontains=q) |
                Q(descricao__icontains=q)
            )
        despesas = qs.order_by('categoria', 'nome')

    return render(request, 'core/despesa_list.html', {
        'despesas': despesas,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def despesa_create(request):
    if request.method == 'POST':
        form = TipoDespesaForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            messages.success(request, f'Tipo de Despesa "{obj.categoria} - {obj.nome}" cadastrado com sucesso!')
            return redirect('core:despesa_list')
    else:
        form = TipoDespesaForm()
    return render(request, 'core/despesa_form.html', {'form': form, 'titulo': 'Novo Tipo de Despesa'})


@login_required
def despesa_update(request, pk):
    obj = get_object_or_404(TipoDespesa, pk=pk)
    if request.method == 'POST':
        form = TipoDespesaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de Despesa "{obj.nome}" atualizado com sucesso!')
            return redirect('core:despesa_list')
    else:
        form = TipoDespesaForm(instance=obj)
    return render(request, 'core/despesa_form.html', {'form': form, 'titulo': f'Editar Tipo de Despesa: {obj.nome}', 'objeto': obj})


@login_required
def despesa_delete(request, pk):
    obj = get_object_or_404(TipoDespesa, pk=pk)
    obj.inativar()
    messages.warning(request, f'Tipo de Despesa "{obj.nome}" foi INATIVADO com sucesso (Exclusão Lógica).')
    return redirect('core:despesa_list')


@login_required
def despesa_reativar(request, pk):
    obj = get_object_or_404(TipoDespesa, pk=pk)
    obj.reativar()
    messages.success(request, f'Tipo de Despesa "{obj.nome}" foi REATIVADO com sucesso!')
    return redirect('core:despesa_list')


# ==========================================================
# 5. MANTER TIPO DE RECEITA
# ==========================================================

@login_required
def receita_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    receitas = []

    if todos or q:
        carregou = True
        qs = TipoReceita.objects.all()
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(nome__icontains=q) |
                Q(descricao__icontains=q)
            )
        receitas = qs.order_by('nome')

    return render(request, 'core/receita_list.html', {
        'receitas': receitas,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def receita_create(request):
    if request.method == 'POST':
        form = TipoReceitaForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            messages.success(request, f'Tipo de Receita "{obj.nome}" cadastrado com sucesso!')
            return redirect('core:receita_list')
    else:
        form = TipoReceitaForm()
    return render(request, 'core/receita_form.html', {'form': form, 'titulo': 'Novo Tipo de Receita'})


@login_required
def receita_update(request, pk):
    obj = get_object_or_404(TipoReceita, pk=pk)
    if request.method == 'POST':
        form = TipoReceitaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de Receita "{obj.nome}" atualizado com sucesso!')
            return redirect('core:receita_list')
    else:
        form = TipoReceitaForm(instance=obj)
    return render(request, 'core/receita_form.html', {'form': form, 'titulo': f'Editar Tipo de Receita: {obj.nome}', 'objeto': obj})


@login_required
def receita_delete(request, pk):
    obj = get_object_or_404(TipoReceita, pk=pk)
    obj.inativar()
    messages.warning(request, f'Tipo de Receita "{obj.nome}" foi INATIVADO com sucesso (Exclusão Lógica).')
    return redirect('core:receita_list')


@login_required
def receita_reativar(request, pk):
    obj = get_object_or_404(TipoReceita, pk=pk)
    obj.reativar()
    messages.success(request, f'Tipo de Receita "{obj.nome}" foi REATIVADO com sucesso!')
    return redirect('core:receita_list')


# ==========================================================
# 6. REGISTRAR CONTAS A PAGAR
# ==========================================================

@login_required
def contas_pagar_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    contas = []

    if todos or q:
        carregou = True
        qs = ContasPagar.objects.select_related('fornecedor', 'faturado').prefetch_related('tipos_despesa', 'parcelas')
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(numero_nota_fiscal__icontains=q) |
                Q(fornecedor__razao_social__icontains=q) |
                Q(fornecedor__cnpj__icontains=q) |
                Q(faturado__nome_completo__icontains=q) |
                Q(descricao_produtos__icontains=q)
            )
        contas = qs.order_by('-data_emissao', '-id')

    return render(request, 'core/contas_pagar_list.html', {
        'contas': contas,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def contas_pagar_create(request):
    if request.method == 'POST':
        form = ContasPagarForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            form.save_m2m()

            # Cria parcela inicial se data de vencimento informada
            data_venc = form.cleaned_data.get('data_vencimento_parcela') or obj.data_emissao
            Parcela.objects.create(
                conta_pagar=obj,
                numero_parcela=1,
                valor=obj.valor_total,
                data_vencimento=data_venc,
                ativo=True
            )

            messages.success(request, f'Conta a Pagar NF {obj.numero_nota_fiscal} registrada com sucesso!')
            return redirect('core:contas_pagar_list')
    else:
        form = ContasPagarForm()
    return render(request, 'core/contas_pagar_form.html', {'form': form, 'titulo': 'Registrar Conta a Pagar'})


@login_required
def contas_pagar_update(request, pk):
    obj = get_object_or_404(ContasPagar, pk=pk)
    if request.method == 'POST':
        form = ContasPagarForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conta a Pagar NF {obj.numero_nota_fiscal} atualizada com sucesso!')
            return redirect('core:contas_pagar_list')
    else:
        form = ContasPagarForm(instance=obj)
    return render(request, 'core/contas_pagar_form.html', {'form': form, 'titulo': f'Editar Conta a Pagar: NF {obj.numero_nota_fiscal}', 'objeto': obj})


@login_required
def contas_pagar_delete(request, pk):
    obj = get_object_or_404(ContasPagar, pk=pk)
    obj.inativar()
    messages.warning(request, f'Conta a Pagar NF "{obj.numero_nota_fiscal}" foi INATIVADA com sucesso (Exclusão Lógica).')
    return redirect('core:contas_pagar_list')


@login_required
def contas_pagar_reativar(request, pk):
    obj = get_object_or_404(ContasPagar, pk=pk)
    obj.reativar()
    messages.success(request, f'Conta a Pagar NF "{obj.numero_nota_fiscal}" foi REATIVADA com sucesso!')
    return redirect('core:contas_pagar_list')


# ==========================================================
# 7. REGISTRAR CONTAS A RECEBER
# ==========================================================

@login_required
def contas_receber_list(request):
    q = request.GET.get('q', '').strip()
    todos = request.GET.get('todos')
    mostrar_inativos = request.GET.get('inativos')

    carregou = False
    contas = []

    if todos or q:
        carregou = True
        qs = ContasReceber.objects.select_related('cliente').prefetch_related('tipos_receita', 'parcelas')
        if mostrar_inativos:
            qs = qs.filter(ativo=False)
        else:
            qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(numero_documento__icontains=q) |
                Q(cliente__nome_completo__icontains=q) |
                Q(descricao__icontains=q)
            )
        contas = qs.order_by('-data_emissao', '-id')

    return render(request, 'core/contas_receber_list.html', {
        'contas': contas,
        'carregou': carregou,
        'q': q,
        'todos': todos,
        'mostrar_inativos': mostrar_inativos,
    })


@login_required
def contas_receber_create(request):
    if request.method == 'POST':
        form = ContasReceberForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ativo = True
            obj.save()
            form.save_m2m()

            data_venc = form.cleaned_data.get('data_vencimento_parcela') or obj.data_emissao
            Parcela.objects.create(
                conta_receber=obj,
                numero_parcela=1,
                valor=obj.valor_total,
                data_vencimento=data_venc,
                ativo=True
            )

            messages.success(request, f'Conta a Receber Doc {obj.numero_documento} registrada com sucesso!')
            return redirect('core:contas_receber_list')
    else:
        form = ContasReceberForm()
    return render(request, 'core/contas_receber_form.html', {'form': form, 'titulo': 'Registrar Conta a Receber'})


@login_required
def contas_receber_update(request, pk):
    obj = get_object_or_404(ContasReceber, pk=pk)
    if request.method == 'POST':
        form = ContasReceberForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conta a Receber Doc {obj.numero_documento} atualizada com sucesso!')
            return redirect('core:contas_receber_list')
    else:
        form = ContasReceberForm(instance=obj)
    return render(request, 'core/contas_receber_form.html', {'form': form, 'titulo': f'Editar Conta a Receber: Doc {obj.numero_documento}', 'objeto': obj})


@login_required
def contas_receber_delete(request, pk):
    obj = get_object_or_404(ContasReceber, pk=pk)
    obj.inativar()
    messages.warning(request, f'Conta a Receber Doc "{obj.numero_documento}" foi INATIVADA com sucesso (Exclusão Lógica).')
    return redirect('core:contas_receber_list')


@login_required
def contas_receber_reativar(request, pk):
    obj = get_object_or_404(ContasReceber, pk=pk)
    obj.reativar()
    messages.success(request, f'Conta a Receber Doc "{obj.numero_documento}" foi REATIVADA com sucesso!')
    return redirect('core:contas_receber_list')
