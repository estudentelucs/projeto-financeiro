import subprocess
import os
from django.conf import settings


def git_info(request):
    """Disponibiliza o código da última atualização do GitHub e dados do sistema em todos os templates."""
    commit_hash = '4bfcd0e'
    try:
        repo_dir = settings.BASE_DIR
        output = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL
        ).decode('ascii').strip()
        if output:
            commit_hash = output
    except Exception:
        pass

    return {
        'ULTIMA_ATUALIZACAO_GITHUB': commit_hash,
        'GITHUB_REPO_URL': 'https://github.com/estudentelucs/projeto-financeiro',
        'SITE_HOSPEDADO_URL': 'https://projeto-financeiro-fnfz.onrender.com',
    }
