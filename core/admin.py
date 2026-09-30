from django.contrib import admin
from .models import (
    Fornecedor, Cliente, Faturado,
    TipoReceita, TipoDespesa,
    ContasPagar, ContasReceber, Parcela
)


class ParcelaInline(admin.TabularInline):
    model = Parcela
    extra = 1


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'nome_fantasia', 'cnpj', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('razao_social', 'nome_fantasia', 'cnpj')
    actions = ['inativar_selecionados', 'reativar_selecionados']

    def inativar_selecionados(self, request, queryset):
        queryset.update(ativo=False)
    inativar_selecionados.short_description = 'Inativar selecionados'

    def reativar_selecionados(self, request, queryset):
        queryset.update(ativo=True)
    reativar_selecionados.short_description = 'Reativar selecionados'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'cnpj', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome_completo', 'cpf', 'cnpj')
    actions = ['inativar_selecionados', 'reativar_selecionados']

    def inativar_selecionados(self, request, queryset):
        queryset.update(ativo=False)
    inativar_selecionados.short_description = 'Inativar selecionados'

    def reativar_selecionados(self, request, queryset):
        queryset.update(ativo=True)
    reativar_selecionados.short_description = 'Reativar selecionados'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Faturado)
class FaturadoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome_completo', 'cpf')
    actions = ['inativar_selecionados', 'reativar_selecionados']

    def inativar_selecionados(self, request, queryset):
        queryset.update(ativo=False)
    inativar_selecionados.short_description = 'Inativar selecionados'

    def reativar_selecionados(self, request, queryset):
        queryset.update(ativo=True)
    reativar_selecionados.short_description = 'Reativar selecionados'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TipoReceita)
class TipoReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TipoDespesa)
class TipoDespesaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'ativo')
    list_filter = ('ativo', 'categoria')
    search_fields = ('nome', 'categoria')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContasPagar)
class ContasPagarAdmin(admin.ModelAdmin):
    list_display = ('numero_nota_fiscal', 'fornecedor', 'faturado', 'valor_total', 'data_emissao', 'ativo')
    list_filter = ('ativo', 'data_emissao')
    search_fields = ('numero_nota_fiscal', 'fornecedor__razao_social')
    filter_horizontal = ('tipos_despesa',)
    inlines = [ParcelaInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContasReceber)
class ContasReceberAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'cliente', 'valor_total', 'data_emissao', 'ativo')
    list_filter = ('ativo', 'data_emissao')
    search_fields = ('numero_documento', 'cliente__nome_completo')
    filter_horizontal = ('tipos_receita',)
    inlines = [ParcelaInline]

    def has_delete_permission(self, request, obj=None):
        return False
