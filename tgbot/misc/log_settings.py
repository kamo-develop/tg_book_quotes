import logging


class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        my_context = kwargs.pop('id', self.extra['id'])
        return '%s [id:%s]' % (msg, my_context), kwargs