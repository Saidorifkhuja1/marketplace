

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Deletes temporary product photo folders older than 5 days"

    def handle(self, *args, **kwargs):
        temp_root = os.path.join(settings.MEDIA_ROOT, 'temp_products')
        if not os.path.exists(temp_root):
            return

        deleted_count = 0
        now = datetime.now()

        for folder in os.listdir(temp_root):
            folder_path = os.path.join(temp_root, folder)
            if os.path.isdir(folder_path):
                created_at = datetime.fromtimestamp(os.path.getctime(folder_path))
                if now - created_at > timedelta(days=5):
                    shutil.rmtree(folder_path, ignore_errors=True)
                    deleted_count += 1

        self.stdout.write(f"{deleted_count} expired temp folders deleted.")