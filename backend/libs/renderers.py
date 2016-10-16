from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_text

from io import StringIO
from rest_framework.compat import six
from rest_framework.compat import BytesIO
from rest_framework.renderers import BaseRenderer

class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        #stream = StringIO()
        stream = BytesIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        self._to_xml(xml, 'response', data)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, name, data):
        if isinstance(data, dict):
            attrs = {}
            for key, value in six.iteritems(data):
                if not isinstance(value, (list, tuple, dict)):
                    attrs[key] = smart_text(value)

            xml.startElement(name, attrs)

            for key, value in six.iteritems(data):
                if isinstance(value, (list, tuple, dict)):
                    self._to_xml(xml, key, value)

            xml.endElement(name)

        elif isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(xml, name, item)

        elif data is None:
            pass
