from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BaseModel(models.Model):
    """Modelo base com campos comuns a todas as entidades."""
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True

    def inativar(self):
        """Inativa o registro (soft delete)."""
        self.ativo = False
        self.save(update_fields=['ativo', 'atualizado_em'])

    def reativar(self):
        """Reativa um registro inativo."""
        self.ativo = True
        self.save(update_fields=['ativo', 'atualizado_em'])


class Fornecedor(BaseModel):
    """Manter Fornecedor."""
    razao_social = models.CharField(max_length=255, verbose_name='Razão Social')
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nome Fantasia')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, null=True, verbose_name='Endereço')

    class Meta:
        db_table = 'fornecedor'
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['razao_social']

    def __str__(self):
        return f'{self.razao_social} ({self.cnpj})'


class Cliente(BaseModel):
    """Manter Cliente."""
    nome_completo = models.CharField(max_length=255, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name='CPF')
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name='CNPJ')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, null=True, verbose_name='Endereço')

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo


class Faturado(BaseModel):
    """Manter Faturado - Pessoa a quem a nota fiscal é faturada."""
    nome_completo = models.CharField(max_length=255, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, null=True, verbose_name='Endereço')

    class Meta:
        db_table = 'faturado'
        verbose_name = 'Faturado'
        verbose_name_plural = 'Faturados'
        ordering = ['nome_completo']

    def __str__(self):
        return f'{self.nome_completo} ({self.cpf})'


class TipoReceita(BaseModel):
    """Manter Tipo de Receita."""
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')

    class Meta:
        db_table = 'tipo_receita'
        verbose_name = 'Tipo de Receita'
        verbose_name_plural = 'Tipos de Receita'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TipoDespesa(BaseModel):
    """Manter Tipo de Despesa."""
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    categoria = models.CharField(max_length=100, verbose_name='Categoria')

    class Meta:
        db_table = 'tipo_despesa'
        verbose_name = 'Tipo de Despesa'
        verbose_name_plural = 'Tipos de Despesa'
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f'{self.categoria} - {self.nome}'


class ContasPagar(BaseModel):
    """Registrar Contas a Pagar."""
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name='contas_pagar',
        verbose_name='Fornecedor'
    )
    faturado = models.ForeignKey(
        Faturado,
        on_delete=models.PROTECT,
        related_name='contas_pagar',
        verbose_name='Faturado'
    )
    numero_nota_fiscal = models.CharField(max_length=50, verbose_name='Número da Nota Fiscal')
    data_emissao = models.DateField(verbose_name='Data de Emissão')
    descricao_produtos = models.TextField(verbose_name='Descrição dos Produtos')
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Total'
    )
    tipos_despesa = models.ManyToManyField(
        TipoDespesa,
        related_name='contas_pagar',
        verbose_name='Tipos de Despesa',
        blank=True
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        db_table = 'contas_pagar'
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['-data_emissao']

    def __str__(self):
        return f'NF {self.numero_nota_fiscal} - {self.fornecedor.razao_social}'


class ContasReceber(BaseModel):
    """Registrar Contas a Receber."""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='contas_receber',
        verbose_name='Cliente'
    )
    numero_documento = models.CharField(max_length=50, verbose_name='Número do Documento')
    data_emissao = models.DateField(verbose_name='Data de Emissão')
    descricao = models.TextField(verbose_name='Descrição')
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Total'
    )
    tipos_receita = models.ManyToManyField(
        TipoReceita,
        related_name='contas_receber',
        verbose_name='Tipos de Receita',
        blank=True
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        db_table = 'contas_receber'
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['-data_emissao']

    def __str__(self):
        return f'Doc {self.numero_documento} - {self.cliente.nome_completo}'


class Parcela(BaseModel):
    """Parcelas de contas a pagar ou a receber."""
    conta_pagar = models.ForeignKey(
        ContasPagar,
        on_delete=models.CASCADE,
        related_name='parcelas',
        blank=True,
        null=True,
        verbose_name='Conta a Pagar'
    )
    conta_receber = models.ForeignKey(
        ContasReceber,
        on_delete=models.CASCADE,
        related_name='parcelas',
        blank=True,
        null=True,
        verbose_name='Conta a Receber'
    )
    numero_parcela = models.PositiveIntegerField(verbose_name='Número da Parcela')
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    data_vencimento = models.DateField(verbose_name='Data de Vencimento')
    data_pagamento = models.DateField(blank=True, null=True, verbose_name='Data de Pagamento')
    pago = models.BooleanField(default=False, verbose_name='Pago')

    class Meta:
        db_table = 'parcela'
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['numero_parcela']

    def __str__(self):
        return f'Parcela {self.numero_parcela} - R$ {self.valor}'
