import sys
import os
import unittest
import nose
from email.utils import formatdate
from nose.tools import *

testdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(testdir, '..'))
import pydcast


class PydcastTests(unittest.TestCase):
    def setUp(self):
        self.title = "A test feed"
        self.baseurl = 'http://example.com/'
        self.link = 'http://example.com/rss.xml'
        self.description = 'A Test Description'
        self.author = 'Somebody'
        self.test1mp3 = os.path.join(testdir, 'test1.mp3')
        self.test2mp3 = os.path.join(testdir, 'test2.mp3')
        self.testbadmp3 = os.path.join(testdir, 'testbad.mp3')

    def test_item_creation(self):
        item = pydcast.Item(self.test1mp3)
        eq_(type(item), pydcast.Item)

    def test_item_attributes(self):
        item = pydcast.Item(self.test1mp3)
        eq_(item.title, "Test Title One")
        eq_(item.author, "Test Artist One")
        eq_(item.filename, self.test1mp3)
        eq_(item.shortfilename, 'test1.mp3')
        eq_(item.filesize, '33563')
        eq_(item.duration, '0:00:02')
        eq_(item.pubdate, formatdate(os.stat(self.test1mp3).st_ctime))

    @raises(pydcast.PydcastError)
    def test_item_fails_on_bad_duration(self):
        pydcast.Item(self.testbadmp3)

    def test_feed_basic_creation(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        eq_(type(f), pydcast.Feed)

    @raises(ValueError)
    def test_feed_must_have_baseurl(self):
        pydcast.Feed(link=self.link)

    @raises(ValueError)
    def test_feed_must_have_link(self):
        pydcast.Feed(baseurl=self.baseurl)

    def test_feed_baseurl_ends_with_a_slash(self):
        f = pydcast.Feed(baseurl=self.baseurl[:-1], link=self.link)
        eq_(f.baseurl, self.baseurl)

    def test_feed_attributes_are_assigned_properly(self):
        f = pydcast.Feed(baseurl=self.baseurl,
                         title=self.title,
                         link=self.link,
                         description=self.description,
                         author=self.author)
        eq_(f.baseurl, self.baseurl)
        eq_(f.title, self.title)
        eq_(f.link, self.link)
        eq_(f.description, self.description)
        eq_(f.author, self.author)

    def test_adding_items_to_feed(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        for i in range(3):
            f.append(pydcast.Item(self.test1mp3))
        eq_(3, len(f))

    @raises(TypeError)
    def test_adding_other_objects_to_feed(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        f.append("oh hi there")


if __name__ == '__main__':
    nose.main()
