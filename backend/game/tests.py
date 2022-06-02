# -*- coding: utf-8 -*-

# -- stdlib --
import json

# -- third party --
import pytest
import factory

# -- own --
from . import models


# -- code --
class GameArchiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GameArchive

    replay = b'AAA'


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Game

    id         = factory.Sequence(lambda v: v + 1)
    name       = 'name'
    type       = 'THBattle2v2'
    flags      = '{}'
    started_at = factory.Faker('date_time')
    duration   = 233
    archive    = factory.RelatedFactory(GameArchiveFactory)


def test_GmAllocGameId(Q):
    response = Q('''
        mutation {
            GmAllocGameId
        }
        '''
    )

    content = json.loads(response.content)
    assert content['data']['GmAllocGameId'] > 0
    assert 'errors' not in content


@pytest.mark.django_db
def test_GmArchive(Q, auth_header):
    from player.tests import PlayerFactory
    PlayerFactory.create()
    PlayerFactory.create()

    import random
    gid = random.randint(100, 10000000)
    game = {
        'gameId': gid,
        'name': 'foo!',
        'type': 'THBattle2v2',
        'flags': {},
        'players': [1, 2],
        'winners': [1],
        'deserters': [2],
        'startedAt': '2020-12-02T15:43:05Z',
        'duration': 333,
    }

    response = Q('''
        mutation TestGmArchive($game: GameInput!) {
            GmArchive(game: $game, archive: "AAAA") {
                id
            }
        }
    ''', variables={'game': game}, headers=auth_header)

    content = json.loads(response.content)
    assert 'errors' not in content
    assert content['data']['GmArchive']['id'] == gid
    models.Game.objects.get(id=gid)
    models.GameArchive.objects.get(game_id=gid)


@pytest.mark.django_db
def test_GmSettleRewards(Q, auth_header):
    from player.tests import PlayerFactory

    PlayerFactory.create()
    PlayerFactory.create()
    g = GameFactory.create()

    game = {
        'gameId': g.id,
        'name': 'foo!',
        'type': 'THBattle2v2',
        'flags': {},
        'players': [1, 2],
        'winners': [1],
        'deserters': [2],
        'startedAt': '2020-12-02T15:43:05Z',
        'duration': 333,
    }

    response = Q('''
        mutation TestGmSettleRewards($game: GameInput!) {
            GmSettleRewards(game: $game) {
                id
            }
        }
    ''', variables={'game': game}, headers=auth_header)

    content = json.loads(response.content)
    assert 'errors' not in content
    rid = content['data']['GmSettleRewards'][0]['id']
    assert rid
    models.GameReward.objects.get(id=rid)
