from django.core.management.base import BaseCommand
from core.models import TipoDespesa


CATEGORIAS_DESPESA = {
    'INSUMOS AGRÍCOLAS': [
        ('Sementes', 'Sementes para plantio'),
        ('Fertilizantes', 'Fertilizantes e adubos'),
        ('Defensivos Agrícolas', 'Defensivos e agrotóxicos'),
        ('Corretivos', 'Corretivos de solo'),
    ],
    'MANUTENÇÃO E OPERAÇÃO': [
        ('Combustíveis e Lubrificantes', 'Diesel, gasolina, óleos lubrificantes'),
        ('Peças e Componentes Mecânicos', 'Parafusos, peças, componentes'),
        ('Manutenção de Máquinas e Equipamentos', 'Serviços de manutenção'),
        ('Pneus, Filtros e Correias', 'Pneus, filtros, correias'),
        ('Ferramentas e Utensílios', 'Ferramentas diversas'),
    ],
    'RECURSOS HUMANOS': [
        ('Mão de Obra Temporária', 'Contratação de mão de obra temporária'),
        ('Salários e Encargos', 'Folha de pagamento e encargos'),
    ],
    'SERVIÇOS OPERACIONAIS': [
        ('Frete e Transporte', 'Serviços de frete e transporte'),
        ('Colheita Terceirizada', 'Serviços de colheita'),
        ('Secagem e Armazenagem', 'Secagem e armazenamento de grãos'),
        ('Pulverização e Aplicação', 'Serviços de pulverização'),
    ],
    'INFRAESTRUTURA E UTILIDADES': [
        ('Energia Elétrica', 'Contas de energia'),
        ('Arrendamento de Terras', 'Aluguel de terras'),
        ('Construções e Reformas', 'Obras e reformas'),
        ('Materiais de Construção', 'Materiais hidráulicos, elétricos, etc.'),
    ],
    'ADMINISTRATIVAS': [
        ('Honorários', 'Honorários contábeis, advocatícios, agronômicos'),
        ('Despesas Bancárias e Financeiras', 'Taxas bancárias e despesas financeiras'),
    ],
    'SEGUROS E PROTEÇÃO': [
        ('Seguro Agrícola', 'Seguro de safra'),
        ('Seguro de Ativos', 'Seguro de máquinas e veículos'),
        ('Seguro Prestamista', 'Seguro de crédito'),
    ],
    'IMPOSTOS E TAXAS': [
        ('ITR', 'Imposto Territorial Rural'),
        ('IPTU', 'Imposto Predial e Territorial Urbano'),
        ('IPVA', 'Imposto sobre Veículos'),
        ('INCRA-CCIR', 'Certificado de Cadastro de Imóvel Rural'),
    ],
    'INVESTIMENTOS': [
        ('Aquisição de Máquinas e Implementos', 'Compra de máquinas agrícolas'),
        ('Aquisição de Veículos', 'Compra de veículos'),
        ('Aquisição de Imóveis', 'Compra de propriedades'),
        ('Infraestrutura Rural', 'Investimentos em infraestrutura'),
    ],
}


class Command(BaseCommand):
    help = 'Popula o banco de dados com os tipos de despesa padrão'

    def handle(self, *args, **options):
        criados = 0
        existentes = 0

        for categoria, tipos in CATEGORIAS_DESPESA.items():
            for nome, descricao in tipos:
                obj, created = TipoDespesa.objects.get_or_create(
                    nome=nome,
                    defaults={
                        'descricao': descricao,
                        'categoria': categoria,
                    }
                )
                if created:
                    criados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  [OK] Criado: {categoria} - {nome}')
                    )
                else:
                    existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResultado: {criados} tipos criados, {existentes} já existentes.'
            )
        )
