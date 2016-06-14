class FeatureMatchException(Exception):
    def __init__(self, message):
        super(FeatureMatchException, self).__init__(message)
        self.message = message
