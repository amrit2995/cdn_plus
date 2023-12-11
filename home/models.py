from django.db import models
from django.core.validators import RegexValidator

class Distribution(models.Model):
    _id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    domain = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Enter a valid domain.',
                code='invalid_domain'
            ),
        ],
    )
    origin_server = models.CharField(max_length=100)
    ssl_tls_config = models.CharField(max_length=50)
    caching_policy = models.CharField(max_length=50) #limited caching policy
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name