"""PostgreSQL-only extension required by the following GiST constraints."""

from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("data", "0001_initial")]
    operations = [BtreeGistExtension()]
