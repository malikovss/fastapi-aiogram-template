from tortoise import fields, Model


class FieldsMixin:
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class User(Model, FieldsMixin):
    tg_id = fields.IntField(unique=True)
    first_name = fields.CharField(max_length=65)
    last_name = fields.CharField(max_length=65, null=True)
    tg_username = fields.CharField(max_length=65, null=True)
    password = fields.CharField(max_length=120, null=True)
    is_admin = fields.BooleanField(default=False)


class Author(Model, FieldsMixin):
    name = fields.CharField(max_length=255)
    created_by = fields.ForeignKeyField("models.User", on_delete=fields.SET_NULL, null=True)


class Quote(FieldsMixin, Model):
    author = fields.ForeignKeyField("models.Author", on_delete=fields.SET_NULL, null=True)
    content = fields.TextField(null=True)
    created_by = fields.ForeignKeyField("models.User", on_delete=fields.SET_NULL, null=True)
    is_public = fields.BooleanField(default=True)
