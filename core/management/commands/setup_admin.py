from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Cria o superusuário padrão admin se não existir'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'[OK] Superusuario "{username}" criado com sucesso!'))
        else:
            u = User.objects.get(username=username)
            u.set_password(password)
            u.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Superusuario "{username}" ja existia e sua senha foi atualizada.'))
