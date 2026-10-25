from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard & Auth
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 1. Manter Fornecedor
    path('fornecedores/', views.fornecedor_list, name='fornecedor_list'),
    path('fornecedores/novo/', views.fornecedor_create, name='fornecedor_create'),
    path('fornecedores/<int:pk>/editar/', views.fornecedor_update, name='fornecedor_update'),
    path('fornecedores/<int:pk>/excluir/', views.fornecedor_delete, name='fornecedor_delete'),
    path('fornecedores/<int:pk>/reativar/', views.fornecedor_reativar, name='fornecedor_reativar'),

    # 2. Manter Cliente
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),
    path('clientes/<int:pk>/reativar/', views.cliente_reativar, name='cliente_reativar'),

    # 3. Manter Faturado
    path('faturados/', views.faturado_list, name='faturado_list'),
    path('faturados/novo/', views.faturado_create, name='faturado_create'),
    path('faturados/<int:pk>/editar/', views.faturado_update, name='faturado_update'),
    path('faturados/<int:pk>/excluir/', views.faturado_delete, name='faturado_delete'),
    path('faturados/<int:pk>/reativar/', views.faturado_reativar, name='faturado_reativar'),

    # 4. Manter Tipo de Despesa
    path('despesas/', views.despesa_list, name='despesa_list'),
    path('despesas/nova/', views.despesa_create, name='despesa_create'),
    path('despesas/<int:pk>/editar/', views.despesa_update, name='despesa_update'),
    path('despesas/<int:pk>/excluir/', views.despesa_delete, name='despesa_delete'),
    path('despesas/<int:pk>/reativar/', views.despesa_reativar, name='despesa_reativar'),

    # 5. Manter Tipo de Receita
    path('receitas/', views.receita_list, name='receita_list'),
    path('receitas/nova/', views.receita_create, name='receita_create'),
    path('receitas/<int:pk>/editar/', views.receita_update, name='receita_update'),
    path('receitas/<int:pk>/excluir/', views.receita_delete, name='receita_delete'),
    path('receitas/<int:pk>/reativar/', views.receita_reativar, name='receita_reativar'),

    # 6. Registrar Contas a Pagar
    path('contas-pagar/', views.contas_pagar_list, name='contas_pagar_list'),
    path('contas-pagar/nova/', views.contas_pagar_create, name='contas_pagar_create'),
    path('contas-pagar/<int:pk>/editar/', views.contas_pagar_update, name='contas_pagar_update'),
    path('contas-pagar/<int:pk>/excluir/', views.contas_pagar_delete, name='contas_pagar_delete'),
    path('contas-pagar/<int:pk>/reativar/', views.contas_pagar_reativar, name='contas_pagar_reativar'),

    # 7. Registrar Contas a Receber
    path('contas-receber/', views.contas_receber_list, name='contas_receber_list'),
    path('contas-receber/nova/', views.contas_receber_create, name='contas_receber_create'),
    path('contas-receber/<int:pk>/editar/', views.contas_receber_update, name='contas_receber_update'),
    path('contas-receber/<int:pk>/excluir/', views.contas_receber_delete, name='contas_receber_delete'),
    path('contas-receber/<int:pk>/reativar/', views.contas_receber_reativar, name='contas_receber_reativar'),
]
