import sys
import os
import unittest
import nose
from email.utils import formatdate
from nose.tools import eq_, raises

testdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(testdir, '..'))
import pydcast


class PydcastTests(unittest.TestCase):
    def setUp(self):
        self.title = "A test feed"
        self.baseurl = 'http://example.com/'
        self.link = 'http://example.com/rss.xml'
        self.description = 'A Test Description'
        self.summary = 'A test summary'
        self.author = 'Somebody'
        self.imageurl = 'http://example.com/image.png'
        self.ownername = 'Testy Tester'
        self.owneremail = 'test@example.com'
        self.test1mp3 = os.path.join(testdir, 'test1.mp3')
        self.test2mp3 = os.path.join(testdir, 'test2.mp3')
        self.testbadmp3 = os.path.join(testdir, 'testbad.mp3')
        self.testblankmp3 = os.path.join(testdir, 'testblank.mp3')

    def test_item_creation(self):
        item = pydcast.Item(self.test1mp3)
        eq_(type(item), pydcast.Item)

    def test_item_attributes(self):
        item = pydcast.Item(self.test1mp3)
        eq_(item.title, "Test Title One")
        eq_(item.author, "Test Artist One")
        eq_(item.filename, self.test1mp3)
        eq_(item.shortfilename, 'test1.mp3')
        eq_(item.subtitle, '')
        eq_(item.summary, 'test1.mp3 - Test Title One')
        eq_(item.filesize, '33563')
        eq_(item.duration, '0:00:02')
        eq_(item.pubdate, formatdate(os.stat(self.test1mp3).st_ctime))

    def test_item_without_tag(self):
        item = pydcast.Item(self.testblankmp3)
        eq_(item.title, 'testblank.mp3')
        eq_(item.author, "")

    def test_item_with_explicit_attributes(self):
        item = pydcast.Item(self.test1mp3,
                            title="Explicit Title",
                            author="Explicit Author",
                            subtitle="Explicit Subtitle",
                            summary="Explicit Summary",
                            imageurl="http://example.com/singleimage.png")
        eq_(item.title, "Explicit Title")
        eq_(item.author, "Explicit Author")
        eq_(item.subtitle, "Explicit Subtitle")
        eq_(item.summary, "Explicit Summary")
        eq_(item.imageurl, "http://example.com/singleimage.png")

    @raises(ValueError)
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
                         summary=self.summary,
                         author=self.author,
                         imageurl=self.imageurl,
                         ownername=self.ownername,
                         owneremail=self.owneremail)
        eq_(f.baseurl, self.baseurl)
        eq_(f.title, self.title)
        eq_(f.link, self.link)
        eq_(f.description, self.description)
        eq_(f.summary, self.summary)
        eq_(f.author, self.author)
        eq_(f.imageurl, self.imageurl)
        eq_(f.ownername, self.ownername)
        eq_(f.owneremail, self.owneremail)

    def test_summary_is_description_if_blank(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link,
                         description=self.description)
        eq_(f.summary, self.description)

    def test_contains(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        i = pydcast.Item(self.test1mp3)
        f.append(i)
        assert(i in f)

    def test_contains_by_title(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        i = pydcast.Item(self.test1mp3)
        f.append(i)
        assert(i.title in f)

    def test_adding_items_to_feed(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        for i in range(3):
            f.append(pydcast.Item(self.test1mp3))
        eq_(3, len(f))

    def test_delete_item_from_feed(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        i = pydcast.Item(self.test1mp3)
        f.append(i)
        eq_(1, len(f))
        del(f[0])
        eq_(0, len(f))
        f.append(i)
        eq_(1, len(f))
        f.remove(i)
        eq_(0, len(f))

    @raises(TypeError)
    def test_adding_other_objects_to_feed(self):
        f = pydcast.Feed(baseurl=self.baseurl, link=self.link)
        f.append("oh hi there")


if __name__ == '__main__':
    nose.main()
