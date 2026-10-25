from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Fornecedor, Cliente, Faturado,
    TipoDespesa, TipoReceita,
    ContasPagar, ContasReceber, Parcela
)


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário...',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha...',
        })
    )


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'email', 'telefone', 'endereco']
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@empresa.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Endereço completo'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome_completo', 'cpf', 'cnpj', 'email', 'telefone', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@cliente.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Endereço completo'}),
        }


class FaturadoForm(forms.ModelForm):
    class Meta:
        model = Faturado
        fields = ['nome_completo', 'cpf', 'email', 'telefone', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do faturado'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@faturado.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Endereço completo'}),
        }


class TipoDespesaForm(forms.ModelForm):
    class Meta:
        model = TipoDespesa
        fields = ['categoria', 'nome', 'descricao']
        widgets = {
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: MANUTENÇÃO E OPERAÇÃO'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Combustíveis e Lubrificantes'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada'}),
        }


class TipoReceitaForm(forms.ModelForm):
    class Meta:
        model = TipoReceita
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Venda de Grãos / Serviços'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada'}),
        }


class ContasPagarForm(forms.ModelForm):
    data_vencimento_parcela = forms.DateField(
        label='Data de Vencimento (1ª Parcela)',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = ContasPagar
        fields = ['fornecedor', 'faturado', 'numero_nota_fiscal', 'data_emissao', 'valor_total', 'tipos_despesa', 'descricao_produtos', 'observacoes']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'faturado': forms.Select(attrs={'class': 'form-select'}),
            'numero_nota_fiscal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12345'}),
            'data_emissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'tipos_despesa': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'descricao_produtos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição dos produtos'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar apenas registros ativos
        self.fields['fornecedor'].queryset = Fornecedor.objects.filter(ativo=True)
        self.fields['faturado'].queryset = Faturado.objects.filter(ativo=True)
        self.fields['tipos_despesa'].queryset = TipoDespesa.objects.filter(ativo=True)


class ContasReceberForm(forms.ModelForm):
    data_vencimento_parcela = forms.DateField(
        label='Data de Vencimento (1ª Parcela)',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = ContasReceber
        fields = ['cliente', 'numero_documento', 'data_emissao', 'valor_total', 'tipos_receita', 'descricao', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: DOC-987'}),
            'data_emissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'tipos_receita': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição do recebimento'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True)
        self.fields['tipos_receita'].queryset = TipoReceita.objects.filter(ativo=True)
