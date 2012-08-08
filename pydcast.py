import os
from lxml import etree
from hsaudiotag import mpeg
from email.utils import formatdate


class PydcastError(Exception):
    pass


def format_secs_to_hmmss(seconds):
    """Converts a duration of integer seconds to a string H:MM:SS for
    use in the feed."""
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%i:%02i:%02i" % (hours, minutes, seconds)


def validate_item(item):
    """Verify that an object is a Pydcast.Item before adding it to the feed.
    This could stand to be duck-typed instead, probably."""
    if type(item) == Item:
        return True
    else:
        raise TypeError("must be a pydcast Item object")


def get_from_tag(mpegobject, tagname):
    """Get an individual id3 tag property from the hsaudiotag Mpeg object.
    Falls back from id3v2 to id3v1; note that if there is no tag at all,
    hsaudiotag will return an empty string when querying id3v1."""
    try:
        return getattr(mpegobject.id3v2, tagname)
    except TypeError:
        return getattr(mpegobject.id3v1, tagname)


class Item(object):
    """An individual mp3 item for inclusion in the a Feed."""

    def __init__(self, from_file, title=None, author=None,
                       subtitle=None, summary=None, description=None,
                       imageurl=None):
        """Create a new mp3 Item for inclusion in a Feed.
        Required args:
            from_file -- the mp3 filename to be podcast. We will try to extract
                         sane defaults from it if the other args are missing.
                         Can include a subdirectory, but not an absolute path.

        Optional keyword args, all used by podcast readers:
            title -- default is the filename (with leading path stripped)
            author -- default is blank
            subtitle -- default is blank
            summary -- default is a combination like 'filename - title'"""
        m = mpeg.Mpeg(from_file)
        if m.duration == 0:
            # hsaudiotag is very forgiving; more so than we want to be.
            # this seems to indicate a malformed mp3 file.
            raise PydcastError("file %s appears to be corrupt" % from_file)

        self.shortfilename = os.path.basename(from_file)
        self.filename = from_file
        self.filesize = str(m.size)
        self.duration = format_secs_to_hmmss(m.duration)
        self.pubdate = formatdate(os.stat(from_file).st_ctime)

        self.title = title if title else get_from_tag(m, 'title')
        self.titler()
        self.imageurl = imageurl
        self.author = author if author else get_from_tag(m, 'artist')
        self.subtitle = subtitle if subtitle else ''
        self.summary = summary if summary else "%s - %s" % \
                                (self.shortfilename, self.title)

    def titler(self):
        if self.title == '':
            self.title = self.shortfilename


class Feed(object):
    """A podcast feed generator."""
    def __init__(self, title='MP3 Feed', baseurl=None, link=None,
                description=None, author=None, imageurl=None):
        """Create a pydcast feed.
        Requred args:
            baseurl -- web url under which the files will be located.
                       individual item urls are baseurl + filename.
                         (where filename can include a subdirectory path)
            link -- address at which the podcast xml file will be published.
        Optional args:
            title -- Title for the feed; default is 'MP3 Feed'
            description -- used by podcast readers; default is blank
            author -- used by podcast readers; default is blank"""
        self.item_list = []
        self.title = title
        if baseurl == None:
            raise ValueError("a base url is required")
        self.baseurl = baseurl
        if self.baseurl[-1] != '/':
            self.baseurl += '/'
        if link == None:
            raise ValueError("a feed link is required")
        self.link = link
        self.description = description
        self.author = author
        self.imageurl = imageurl

    def append(self, item):
        """Add a pydcast Item to the Feed"""
        if validate_item(item):
            self.item_list.append(item)

    def __len__(self):
        """Number of items in the Feed"""
        return len(self.item_list)

    def __str__(self):
        """Returns the xml text for the podcast feed itself."""
        itunes_url = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        itunes = '{%s}' % itunes_url
        nsmap = {'itunes': itunes_url}

        rss = etree.Element('rss', version="2.0", nsmap=nsmap)
        channel = etree.SubElement(rss, 'channel')
        chantitle = etree.SubElement(channel, 'title')
        chantitle.text = self.title
        chanlink = etree.SubElement(channel, 'link')
        chanlink.text = self.link
        if self.description:
            chandescr = etree.SubElement(channel, 'description')
            chandescr.text = self.description
        if self.author:
            chanauthor = etree.SubElement(channel, itunes + 'author')
            chanauthor.text = self.author

        for i in self.item_list:
            item = etree.SubElement(channel, 'item')
            title = etree.SubElement(item, 'title')
            title.text = i.title
            link = etree.SubElement(item, 'link')
            itemurl = self.baseurl + i.shortfilename
            link.text = itemurl
            etree.SubElement(item, 'enclosure', url=itemurl,
                            length=i.filesize, type='audio/mpeg')
            if i.author:
                author = etree.SubElement(item, itunes + 'author')
                author.text = i.author
            subtitle = etree.SubElement(item, itunes + 'subtitle')
            subtitle.text = i.subtitle
            summary = etree.SubElement(item, itunes + 'summary')
            summary.text = i.summary
            duration = etree.SubElement(item, itunes + 'duration')
            duration.text = i.duration
            pubdate = etree.SubElement(item, 'pubDate')
            pubdate.text = i.pubdate
            if i.imageurl:
                imageurl = etree.SubElement(item, itunes + 'image')
                imageurl.text = i.imageurl

        return etree.tostring(rss, xml_declaration=True, encoding="UTF-8",
                                pretty_print=True)
