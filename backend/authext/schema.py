# -*- coding: utf-8 -*-
from __future__ import annotations

# -- stdlib --
# -- third party --
import graphene as gh
import django.contrib.auth as auth
import django.contrib.auth.models as auth_models
from graphene_django import DjangoObjectType

# -- own --
from . import models
from utils.graphql import require_perm


# -- code --
class User(DjangoObjectType):
    class Meta:
        model = auth_models.User
        exclude = [
            'password',
        ]

    token = gh.String(description="登录令牌")

    @staticmethod
    def resolve_token(root, info):
        # from backend import debug
        # rv = debug.state.collect_current()
        # print(f'http://localhost:8000/.debug/console/{rv["id"]}')
        return root.token()


class Group(DjangoObjectType):
    class Meta:
        model = auth_models.Group


class Permission(DjangoObjectType):
    class Meta:
        model = auth_models.Permission


class Login(gh.ObjectType):
    phone = gh.Field(
        User,
        phone=gh.String(required=True, description="手机"),
        code=gh.String(required=True, description="验证码"),
        description="登录",
    )

    @staticmethod
    def resolve_phone(root, info, phone, code):
        phone = phone and phone.strip()
        from authext.models import PhoneLogin
        if phone := PhoneLogin.objects.filter(phone=phone).first():
            return phone.user

        return None

    token = gh.Field(
        User,
        token=gh.String(required=True, description="令牌"),
        description="令牌登录",
    )

    @staticmethod
    def resolve_token(root, info, token):
        if user := auth.authenticate(token=token):
            return user

        return None


class UserQuery(gh.ObjectType):
    user = gh.Field(
        User,
        id=gh.Int(required=True, description="用户ID"),
        description="获取用户",
    )

    @staticmethod
    def resolve_user(root, info, id):
        ctx = info.context
        require_perm(ctx, 'player.view_user')
        return models.User.objects.filter(id=id).first()

    login = gh.Field(Login, description="登录")

    def resolve_login(root, info):
        return Login()


class UserOps(gh.ObjectType):
    pass
