# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from django.test import TestCase
import mock

from teams.signals import api_teamvideo_new
from videos.signals import feed_imported
from utils import test_factories

class TeamVideoImportTestCase(TestCase):
    def test_create_team_videos_for_team_feed(self):
        api_teamvideo_new_handler = mock.Mock()
        api_teamvideo_new.connect(api_teamvideo_new_handler, weak=False)
        self.addCleanup(api_teamvideo_new.disconnect,
                        api_teamvideo_new_handler)

        team = test_factories.create_team()
        user = test_factories.create_team_member(team).user
        videos = [test_factories.create_video() for i in xrange(5)]
        feed = mock.Mock(team=team, user=user)
        feed_imported.send(sender=feed, new_videos=videos)
        for video in videos:
            self.assertNotEquals(video.get_team_video(), None)
            self.assertEquals(video.get_team_video().team, team)


        correct_api_calls = [
            mock.call(signal=api_teamvideo_new, sender=video.get_team_video())
            for video in videos
        ]

        api_teamvideo_new_handler.assert_has_calls(correct_api_calls,
                                                   any_order=True)

    def test_noop_for_non_team_feed(self):
        team = test_factories.create_team()
        user = test_factories.create_user()
        videos = [test_factories.create_video() for i in xrange(5)]
        feed = mock.Mock(team=None, user=user)
        feed_imported.send(sender=feed, new_videos=videos)
        for video in videos:
            self.assertEquals(video.get_team_video(), None)
