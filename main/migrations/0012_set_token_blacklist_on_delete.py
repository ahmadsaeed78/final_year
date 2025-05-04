from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_studentmarking_evaluated_at'),
        ('token_blacklist', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE token_blacklist_outstandingtoken
            DROP CONSTRAINT token_blacklist_outs_user_id_83bc629a_fk_main_cust;
            
            ALTER TABLE token_blacklist_outstandingtoken
            ADD CONSTRAINT token_blacklist_outs_user_id_83bc629a_fk_main_cust
            FOREIGN KEY (user_id) REFERENCES main_customuser(id)
            ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE token_blacklist_outstandingtoken
            DROP CONSTRAINT token_blacklist_outs_user_id_83bc629a_fk_main_cust;
            
            ALTER TABLE token_blacklist_outstandingtoken
            ADD CONSTRAINT token_blacklist_outs_user_id_83bc629a_fk_main_cust
            FOREIGN KEY (user_id) REFERENCES main_customuser(id);
            """
        ),
    ] 