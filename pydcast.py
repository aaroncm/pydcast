import os
from lxml import etree
from hsaudiotag import mpeg
from email.utils import formatdate


def format_secs_to_hhmmss(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%i:%02i:%02i" % (hours, minutes, seconds)


def validate_item(item):
    if type(item) == Item:
        return True
    else:
        raise TypeError("must be a pydcast Item object")


class PydcastError(Exception):
    pass


class Item(object):
    def __init__(self, from_file):
        m = mpeg.Mpeg(from_file)
        if m.duration == 0:
            # hsaudiotag is very forgiving; more so than we want to be.
            # this seems to indicate a malformed mp3 file.
            raise PydcastError("file %s appears to be corrupt" % from_file)

        self.shortfilename = os.path.basename(from_file)
        self.filename = from_file
        self.filesize = str(m.size)
        self.duration = format_secs_to_hhmmss(m.duration)
        self.pubdate = formatdate(os.stat(from_file).st_ctime)
        try:
            self.title = m.id3v2.title
        except TypeError:
            try:
                self.title = m.id3v1.title
            except TypeError:
                self.title = self.shortfilename

        try:
            self.author = m.id3v2.artist
        except TypeError:
            try:
                self.author = m.id3v1.artist
            except TypeError:
                self.author = None


class Feed(object):

    def __init__(self, title='MP3 Feed', baseurl=None, link=None,
                description=None, author=None):
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
        if description:
            self.description = description
        self.author = author

    def append(self, item):
        if validate_item(item):
            self.item_list.append(item)

    def __len__(self):
        return len(self.item_list)

    def __str__(self):
        itunes_url = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        itunes = '{%s}' % itunes_url
        nsmap = {'itunes': itunes_url}

        rss = etree.Element('rss', version="2.0", nsmap=nsmap)
        channel = etree.SubElement(rss, 'channel')
        chantitle = etree.SubElement(channel, 'title')
        chantitle.text = self.title
        chanlink = etree.SubElement(channel, 'link')
        chanlink.text = self.link
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
            subtitle.text = i.title
            summary = etree.SubElement(item, itunes + 'summary')
            summary.text = i.title
            duration = etree.SubElement(item, itunes + 'duration')
            duration.text = i.duration
            pubdate = etree.SubElement(item, 'pubDate')
            pubdate.text = i.pubdate

        return etree.tostring(rss, xml_declaration=True, encoding="UTF-8",
                                pretty_print=True)
